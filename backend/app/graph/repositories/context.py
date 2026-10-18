from app.graph.repositories.base import BaseRepository


class ContextRepository(BaseRepository):
    def safeguards(self, equipment_id: str) -> list[dict]:
        self.require_id(equipment_id, "EQ-")
        rows = self.executor.read(
            "context.safeguards",
            """
            MATCH (s:Safeguard {tenant_id:$tenant_id})-[:PROTECTS]->
                  (e:Equipment {tenant_id:$tenant_id, id:$equipment_id})
            OPTIONAL MATCH (s)-[:MITIGATES]->(h:Hazard)
            RETURN s.id, s.name, s.safeguard_type, s.design_status,
                   collect(DISTINCT {id:h.id, name:h.name, severity:h.severity})
            ORDER BY s.name LIMIT 50
            """,
            self.params(equipment_id=equipment_id),
        ).rows
        return [{"id": r[0], "name": r[1], "type": r[2], "design_status": r[3], "hazards": r[4]} for r in rows]

    def open_findings(self, equipment_id: str, depth: int = 3) -> list[dict]:
        self.require_id(equipment_id, "EQ-")
        depth = self.validate_depth(depth)
        query = f"""
        MATCH path=(source:Equipment {{tenant_id:$tenant_id, id:$equipment_id}})
          -[:COOLED_BY|SUPPLIED_BY|DEPENDS_ON*0..{depth}]-(related:Equipment {{tenant_id:$tenant_id}})
        MATCH (f:MaintenanceFinding {{tenant_id:$tenant_id}})-[:ABOUT]->(related)
        WHERE f.status IN ['open','monitoring']
        RETURN f.id, f.summary, f.severity, f.status, related.id, related.name,
               [n IN nodes(path) | n.id]
        ORDER BY f.severity DESC, f.created_at DESC LIMIT 100
        """
        rows = self.executor.read("context.open_findings", query, self.params(equipment_id=equipment_id)).rows
        return [{"id": r[0], "summary": r[1], "severity": r[2], "status": r[3], "equipment": {"id": r[4], "name": r[5]}, "path": r[6]} for r in rows]

    def responsible_team(self, equipment_id: str) -> dict | None:
        self.require_id(equipment_id, "EQ-")
        rows = self.executor.read(
            "context.owner",
            """
            MATCH (t:Team {tenant_id:$tenant_id})-[:OWNS]->
                  (e:Equipment {tenant_id:$tenant_id, id:$equipment_id})
            RETURN t.id, t.name LIMIT 2
            """,
            self.params(equipment_id=equipment_id),
            result_limit=2,
        ).rows
        return None if not rows else {"id": rows[0][0], "name": rows[0][1]}

    def related_incidents(self, equipment_id: str) -> list[dict]:
        self.require_id(equipment_id, "EQ-")
        rows = self.executor.read(
            "context.related_incidents",
            """
            MATCH (i:Incident {tenant_id:$tenant_id})-[:AFFECTS]->
                  (e:Equipment {tenant_id:$tenant_id, id:$equipment_id})
            OPTIONAL MATCH (i)-[:RESULTED_IN]->(a:Action)-[:PRODUCED]->(o:Outcome)
            RETURN i.id, i.summary, i.status, i.occurred_at,
                   collect(DISTINCT {action_id:a.id, outcome_id:o.id, outcome:o.summary})
            ORDER BY i.occurred_at DESC LIMIT 50
            """,
            self.params(equipment_id=equipment_id),
        ).rows
        return [{"id": r[0], "summary": r[1], "status": r[2], "occurred_at": r[3], "outcomes": r[4]} for r in rows]

    def active_memories(self, entity_id: str, limit: int = 10) -> list[dict]:
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        rows = self.executor.read(
            "context.active_memories",
            """
            MATCH (m:Memory {tenant_id:$tenant_id, status:'active'})-[:ABOUT]->
                  (entity {tenant_id:$tenant_id, id:$entity_id})
            OPTIONAL MATCH (m)-[:DERIVED_FROM]->(source)
            RETURN m.id, m.memory_type, m.summary, m.confidence,
                   source.id, labels(source)
            ORDER BY m.confidence DESC LIMIT $limit
            """,
            self.params(entity_id=entity_id, limit=limit),
            result_limit=limit,
        ).rows
        return [{"id": r[0], "type": r[1], "summary": r[2], "confidence": r[3], "source_id": r[4], "source_labels": r[5]} for r in rows]
