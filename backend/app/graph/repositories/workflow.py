from app.graph.repositories.base import BaseRepository


class WorkflowRepository(BaseRepository):
    def create_session(self, session_id: str, idempotency_key: str) -> dict:
        self.require_id(session_id, "SESSION-")
        rows = self.executor.write(
            "workflow.create_session",
            """
            MERGE (s:Session {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET s.id=$session_id, s.status='active', s.synthetic=true,
                          s.source='runtime', s.created_at=timestamp()
            RETURN s.id, s.status, s.idempotency_key
            """,
            self.params(session_id=session_id, idempotency_key=idempotency_key),
            result_limit=1,
        ).rows
        return {"id": rows[0][0], "status": rows[0][1], "idempotency_key": rows[0][2]}

    def create_incident(self, session_id: str, incident_id: str, summary: str, equipment_id: str, idempotency_key: str) -> dict:
        self.require_id(session_id, "SESSION-")
        self.require_id(incident_id, "INC-")
        self.require_id(equipment_id, "EQ-")
        rows = self.executor.write(
            "workflow.create_incident",
            """
            MATCH (s:Session {tenant_id:$tenant_id, id:$session_id})
            MATCH (e:Equipment {tenant_id:$tenant_id, id:$equipment_id})
            MERGE (i:Incident {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET i.id=$incident_id, i.summary=$summary, i.status='RECEIVED',
                          i.synthetic=true, i.source='runtime', i.created_at=timestamp()
            MERGE (s)-[:CREATED {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(i)
            MERGE (i)-[:AFFECTS {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(e)
            RETURN i.id, i.status
            """,
            self.params(session_id=session_id, incident_id=incident_id, summary=summary, equipment_id=equipment_id, idempotency_key=idempotency_key),
            result_limit=1,
        ).rows
        return {"id": rows[0][0], "status": rows[0][1]}

    def create_task(self, incident_id: str, task_id: str, agent_id: str, task_type: str, idempotency_key: str) -> dict:
        rows = self.executor.write(
            "workflow.create_task",
            """
            MATCH (i:Incident {tenant_id:$tenant_id, id:$incident_id})
            MATCH (a:Agent {tenant_id:$tenant_id, id:$agent_id})
            MERGE (t:Task {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET t.id=$task_id, t.task_type=$task_type, t.status='PENDING',
                          t.synthetic=true, t.source='runtime', t.created_at=timestamp()
            MERGE (i)-[:HAS_TASK {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(t)
            MERGE (t)-[:ASSIGNED_TO {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(a)
            RETURN t.id, t.status
            """,
            self.params(incident_id=incident_id, task_id=task_id, agent_id=agent_id, task_type=task_type, idempotency_key=idempotency_key),
            result_limit=1,
        ).rows
        return {"id": rows[0][0], "status": rows[0][1]}

    def record_finding(self, task_id: str, finding_id: str, summary: str, confidence: float, evidence_entity_id: str, idempotency_key: str) -> dict:
        rows = self.executor.write(
            "workflow.record_finding",
            """
            MATCH (t:Task {tenant_id:$tenant_id, id:$task_id})
            MATCH (e {tenant_id:$tenant_id, id:$evidence_entity_id})
            MERGE (f:Finding {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET f.id=$finding_id, f.summary=$summary, f.confidence=$confidence,
                          f.status='candidate', f.synthetic=true, f.source='runtime', f.created_at=timestamp()
            MERGE (t)-[:PRODUCED {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(f)
            MERGE (f)-[:SUPPORTED_BY {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(e)
            RETURN f.id, f.status
            """,
            self.params(task_id=task_id, finding_id=finding_id, summary=summary, confidence=confidence, evidence_entity_id=evidence_entity_id, idempotency_key=idempotency_key),
            result_limit=1,
        ).rows
        return {"id": rows[0][0], "status": rows[0][1]}

    def create_handoff(self, task_id: str, handoff_id: str, from_agent_id: str, to_agent_id: str, reason: str, idempotency_key: str) -> dict:
        rows = self.executor.write(
            "workflow.create_handoff",
            """
            MATCH (t:Task {tenant_id:$tenant_id, id:$task_id})
            MATCH (from:Agent {tenant_id:$tenant_id, id:$from_agent_id})
            MATCH (to:Agent {tenant_id:$tenant_id, id:$to_agent_id})
            MERGE (h:Handoff {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET h.id=$handoff_id, h.reason=$reason, h.status='created',
                          h.synthetic=true, h.source='runtime', h.created_at=timestamp()
            MERGE (h)-[:FROM_AGENT {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(from)
            MERGE (h)-[:TO_AGENT {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(to)
            MERGE (h)-[:TRANSFERS {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(t)
            RETURN h.id, h.status
            """,
            self.params(task_id=task_id, handoff_id=handoff_id, from_agent_id=from_agent_id, to_agent_id=to_agent_id, reason=reason, idempotency_key=idempotency_key),
            result_limit=1,
        ).rows
        return {"id": rows[0][0], "status": rows[0][1]}

    def propose_action(self, finding_id: str, action_id: str, team_id: str, action_type: str, summary: str, idempotency_key: str) -> dict:
        rows = self.executor.write(
            "workflow.propose_action",
            """
            MATCH (f:Finding {tenant_id:$tenant_id, id:$finding_id})
            MATCH (team:Team {tenant_id:$tenant_id, id:$team_id})
            MERGE (a:Action {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET a.id=$action_id, a.action_type=$action_type, a.summary=$summary,
                          a.status='PROPOSED', a.synthetic=true, a.source='runtime', a.created_at=timestamp()
            MERGE (a)-[:ADDRESSES {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(f)
            MERGE (a)-[:ASSIGNED_TO {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(team)
            RETURN a.id, a.status
            """,
            self.params(finding_id=finding_id, action_id=action_id, team_id=team_id, action_type=action_type, summary=summary, idempotency_key=idempotency_key),
            result_limit=1,
        ).rows
        return {"id": rows[0][0], "status": rows[0][1]}

    def record_outcome(self, action_id: str, outcome_id: str, summary: str, effectiveness: str, idempotency_key: str) -> dict:
        rows = self.executor.write(
            "workflow.record_outcome",
            """
            MATCH (a:Action {tenant_id:$tenant_id, id:$action_id})
            MERGE (o:Outcome {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET o.id=$outcome_id, o.summary=$summary, o.effectiveness=$effectiveness,
                          o.synthetic=true, o.source='runtime', o.created_at=timestamp()
            MERGE (a)-[:PRODUCED {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(o)
            RETURN o.id, o.effectiveness
            """,
            self.params(action_id=action_id, outcome_id=outcome_id, summary=summary, effectiveness=effectiveness, idempotency_key=idempotency_key),
            result_limit=1,
        ).rows
        return {"id": rows[0][0], "effectiveness": rows[0][1]}
