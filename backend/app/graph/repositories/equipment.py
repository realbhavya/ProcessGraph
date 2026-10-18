from app.graph.errors import AmbiguousEntity, EntityNotFound
from app.graph.repositories.base import BaseRepository


class EquipmentRepository(BaseRepository):
    def resolve(self, name: str) -> dict:
        normalized = name.strip().lower()
        result = self.executor.read(
            "equipment.resolve",
            """
            MATCH (e:Equipment {tenant_id:$tenant_id, normalized_name:$name})
            RETURN e.id, e.name, e.equipment_type, e.criticality, e.status
            LIMIT 2
            """,
            self.params(name=normalized),
            result_limit=2,
        )
        if not result.rows:
            raise EntityNotFound(name)
        if len(result.rows) > 1:
            raise AmbiguousEntity(name)
        row = result.rows[0]
        return {"id": row[0], "name": row[1], "type": row[2], "criticality": row[3], "status": row[4]}

    def context(self, equipment_id: str) -> dict:
        self.require_id(equipment_id, "EQ-")
        result = self.executor.read(
            "equipment.context",
            """
            MATCH (e:Equipment {tenant_id:$tenant_id, id:$equipment_id})
            OPTIONAL MATCH (unit:Unit)-[:CONTAINS]->(e)
            OPTIONAL MATCH (team:Team)-[:OWNS]->(e)
            OPTIONAL MATCH (sensor:Sensor)-[:MONITORS]->(e)
            RETURN e.id, e.name, unit.id, unit.name,
                   collect(DISTINCT {id:team.id, name:team.name}),
                   collect(DISTINCT {id:sensor.id, name:sensor.name})
            """,
            self.params(equipment_id=equipment_id),
        )
        if not result.rows:
            raise EntityNotFound(equipment_id)
        r = result.rows[0]
        return {"id": r[0], "name": r[1], "unit": {"id": r[2], "name": r[3]}, "teams": r[4], "sensors": r[5]}

    def trace_process_impact(self, equipment_id: str, depth: int = 4) -> list[dict]:
        self.require_id(equipment_id, "EQ-")
        depth = self.validate_depth(depth)
        query = f"""
        MATCH path=(source:Equipment {{tenant_id:$tenant_id, id:$equipment_id}})
          -[:FEEDS*1..{depth}]-(related:Equipment {{tenant_id:$tenant_id}})
        RETURN related.id, related.name, length(path),
               [n IN nodes(path) | n.id],
               [r IN relationships(path) | type(r)]
        ORDER BY length(path), related.name
        LIMIT 100
        """
        rows = self.executor.read("equipment.process_impact", query, self.params(equipment_id=equipment_id)).rows
        return [{"id": r[0], "name": r[1], "hops": r[2], "node_ids": r[3], "relationships": r[4]} for r in rows]

    def trace_utility_path(self, equipment_id: str, depth: int = 4) -> list[dict]:
        self.require_id(equipment_id, "EQ-")
        depth = self.validate_depth(depth)
        query = f"""
        MATCH path=(source:Equipment {{tenant_id:$tenant_id, id:$equipment_id}})
          -[:COOLED_BY|SUPPLIED_BY|DEPENDS_ON*1..{depth}]-(related)
        WHERE related.tenant_id=$tenant_id
        RETURN related.id, related.name, labels(related), length(path),
               [n IN nodes(path) | n.id],
               [r IN relationships(path) | type(r)]
        ORDER BY length(path), related.name
        LIMIT 100
        """
        rows = self.executor.read("equipment.utility_path", query, self.params(equipment_id=equipment_id)).rows
        return [{"id": r[0], "name": r[1], "labels": r[2], "hops": r[3], "node_ids": r[4], "relationships": r[5]} for r in rows]

    def connected_sensors(self, equipment_id: str) -> list[dict]:
        self.require_id(equipment_id, "EQ-")
        rows = self.executor.read(
            "equipment.sensors",
            """
            MATCH (s:Sensor {tenant_id:$tenant_id})-[:MONITORS]->
                  (e:Equipment {tenant_id:$tenant_id, id:$equipment_id})
            OPTIONAL MATCH (s)-[:MEASURES]->(p:Parameter)
            RETURN s.id, s.name, s.sensor_type, p.id, p.name
            ORDER BY s.name LIMIT 50
            """,
            self.params(equipment_id=equipment_id),
        ).rows
        return [{"id": r[0], "name": r[1], "type": r[2], "parameter": {"id": r[3], "name": r[4]}} for r in rows]
