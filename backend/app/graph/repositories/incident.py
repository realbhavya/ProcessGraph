from __future__ import annotations

from app.graph.errors import EntityNotFound, InvalidInput
from app.graph.repositories.base import BaseRepository


class IncidentRepository(BaseRepository):
    def create_incident_bundle(
        self,
        *,
        session_id: str,
        incident_id: str,
        summary: str,
        equipment: list[dict],
        observations: list[dict],
        idempotency_key: str,
        request_id: str,
    ) -> dict:
        equipment_ids = [item["id"] for item in equipment]
        rows = self.executor.write(
            "incident.create_bundle",
            """
            MERGE (session:Session {tenant_id:$tenant_id, idempotency_key:$session_key})
            ON CREATE SET session.id=$session_id, session.status='active', session.synthetic=true,
                          session.source='runtime', session.created_at=timestamp()
            MERGE (incident:Incident {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET incident.id=$incident_id, incident.summary=$summary,
                          incident.status='RECEIVED', incident.synthetic=true,
                          incident.source='runtime', incident.created_at=timestamp()
            MERGE (session)-[:CREATED {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(incident)
            WITH session, incident
            UNWIND $equipment_ids AS equipment_id
            MATCH (equipment:Equipment {tenant_id:$tenant_id, id:equipment_id})
            MERGE (incident)-[:AFFECTS {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(equipment)
            WITH session, incident
            MERGE (event:TimelineEvent {tenant_id:$tenant_id, idempotency_key:$event_key})
            ON CREATE SET event.id=$event_id, event.event_type='INCIDENT_CREATED',
                          event.actor_type='user', event.actor_id='demo-user',
                          event.previous_state=null, event.new_state='RECEIVED',
                          event.reason='Incident accepted', event.request_id=$request_id,
                          event.synthetic=true, event.source='runtime', event.created_at=timestamp()
            MERGE (incident)-[:HAS_EVENT {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(event)
            RETURN incident.id, session.id, incident.summary, incident.status,
                   incident.created_at
            """,
            self.params(
                session_key=f"session:{idempotency_key}",
                session_id=session_id,
                idempotency_key=idempotency_key,
                incident_id=incident_id,
                summary=summary,
                equipment_ids=equipment_ids,
                event_key=f"event:{idempotency_key}:created",
                event_id=f"EVENT-{incident_id}-CREATED",
                request_id=request_id,
            ),
            result_limit=1,
        ).rows
        if not rows:
            raise InvalidInput("Unable to create incident bundle")

        for observation in observations:
            self.add_observation(
                incident_id=incident_id,
                observation=observation,
                idempotency_key=observation["idempotency_key"],
                request_id=request_id,
            )
        return self.get(incident_id)

    def add_observation(self, *, incident_id: str, observation: dict, idempotency_key: str, request_id: str) -> dict:
        rows = self.executor.write(
            "incident.add_observation",
            """
            MATCH (incident:Incident {tenant_id:$tenant_id, id:$incident_id})
            MERGE (observation:Observation {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET observation.id=$observation_id,
                          observation.parameter=$parameter,
                          observation.qualifier=$qualifier,
                          observation.value=$value,
                          observation.unit=$unit,
                          observation.sensor_name=$sensor_name,
                          observation.source_type='user_report',
                          observation.synthetic=true,
                          observation.source='runtime',
                          observation.created_at=timestamp()
            MERGE (incident)-[:HAS_OBSERVATION {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(observation)
            RETURN observation.id, observation.parameter, observation.qualifier,
                   observation.value, observation.unit, observation.sensor_name
            """,
            self.params(
                incident_id=incident_id,
                idempotency_key=idempotency_key,
                observation_id=observation["id"],
                parameter=observation["parameter"],
                qualifier=observation["qualifier"],
                value=observation.get("value"),
                unit=observation.get("unit"),
                sensor_name=observation.get("sensor_name"),
                request_id=request_id,
            ),
            result_limit=1,
        ).rows
        if not rows:
            raise EntityNotFound(incident_id)
        row = rows[0]
        return {"id": row[0], "parameter": row[1], "qualifier": row[2], "value": row[3], "unit": row[4], "sensor_name": row[5]}

    def get(self, incident_id: str) -> dict:
        self.require_id(incident_id, "INC-")
        rows = self.executor.read(
            "incident.get",
            """
            MATCH (session:Session {tenant_id:$tenant_id})-[:CREATED]->
                  (incident:Incident {tenant_id:$tenant_id, id:$incident_id})
            OPTIONAL MATCH (incident)-[:AFFECTS]->(equipment:Equipment)
            OPTIONAL MATCH (incident)-[:HAS_OBSERVATION]->(observation:Observation)
            RETURN incident.id, session.id, incident.summary, incident.status,
                   incident.created_at,
                   collect(DISTINCT {id:equipment.id, name:equipment.name, type:equipment.equipment_type}) AS equipment,
                   collect(DISTINCT {id:observation.id, parameter:observation.parameter,
                       qualifier:observation.qualifier, value:observation.value,
                       unit:observation.unit, sensor_name:observation.sensor_name}) AS observations
            """,
            self.params(incident_id=incident_id),
            result_limit=1,
        ).rows
        if not rows:
            raise EntityNotFound(incident_id)
        r = rows[0]
        observations = [item for item in r[6] if item.get("id")]
        equipment = [item for item in r[5] if item.get("id")]
        return {"id": r[0], "session_id": r[1], "summary": r[2], "status": r[3], "created_at": r[4], "equipment": equipment, "observations": observations}

    def current_state(self, incident_id: str) -> str:
        rows = self.executor.read(
            "incident.current_state",
            "MATCH (i:Incident {tenant_id:$tenant_id, id:$incident_id}) RETURN i.status",
            self.params(incident_id=incident_id),
            result_limit=1,
        ).rows
        if not rows:
            raise EntityNotFound(incident_id)
        return rows[0][0]

    def transition(self, *, incident_id: str, expected_state: str, target_state: str, reason: str, event_id: str, idempotency_key: str, request_id: str, actor_id: str = "system") -> dict:
        rows = self.executor.write(
            "incident.transition",
            """
            MATCH (incident:Incident {tenant_id:$tenant_id, id:$incident_id})
            WHERE incident.status=$expected_state
            MERGE (event:TimelineEvent {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET event.id=$event_id, event.event_type='STATE_TRANSITION',
                          event.actor_type='system', event.actor_id=$actor_id,
                          event.previous_state=$expected_state, event.new_state=$target_state,
                          event.reason=$reason, event.request_id=$request_id,
                          event.synthetic=true, event.source='runtime', event.created_at=timestamp()
            MERGE (incident)-[:HAS_EVENT {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(event)
            SET incident.status=$target_state, incident.updated_at=timestamp()
            RETURN incident.id, incident.status
            """,
            self.params(incident_id=incident_id, expected_state=expected_state, target_state=target_state, reason=reason, event_id=event_id, idempotency_key=idempotency_key, request_id=request_id, actor_id=actor_id),
            result_limit=1,
        ).rows
        if not rows:
            raise InvalidInput("Incident state changed concurrently or does not match the expected state")
        return {"id": rows[0][0], "status": rows[0][1]}

    def timeline(self, incident_id: str) -> list[dict]:
        rows = self.executor.read(
            "incident.timeline",
            """
            MATCH (:Incident {tenant_id:$tenant_id, id:$incident_id})-[:HAS_EVENT]->(event:TimelineEvent)
            RETURN event.id, event.event_type, event.actor_type, event.actor_id,
                   event.previous_state, event.new_state, event.reason,
                   event.request_id, event.created_at
            ORDER BY event.created_at, event.id LIMIT 200
            """,
            self.params(incident_id=incident_id),
            result_limit=200,
        ).rows
        return [{"id": r[0], "event_type": r[1], "actor_type": r[2], "actor_id": r[3], "previous_state": r[4], "new_state": r[5], "reason": r[6], "request_id": r[7], "created_at": r[8]} for r in rows]

    def paths(self, incident_id: str, depth: int = 4) -> list[dict]:
        depth = self.validate_depth(depth)
        query = f"""
        MATCH (incident:Incident {{tenant_id:$tenant_id, id:$incident_id}})-[:AFFECTS]->(source:Equipment)
        MATCH path=(source)-[:COOLED_BY|SUPPLIED_BY|DEPENDS_ON*1..{depth}]-(target)
        WHERE target.tenant_id=$tenant_id
        RETURN source.id, target.id, length(path),
               [n IN nodes(path) | n.id],
               [n IN nodes(path) | n.name],
               [r IN relationships(path) | type(r)]
        ORDER BY length(path), target.id LIMIT 100
        """
        rows = self.executor.read("incident.paths", query, self.params(incident_id=incident_id)).rows
        return [{"source_id": r[0], "target_id": r[1], "hops": r[2], "node_ids": r[3], "node_names": r[4], "relationships": r[5]} for r in rows]
