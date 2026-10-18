from app.graph.repositories.base import BaseRepository


class MemoryRepository(BaseRepository):
    def create_candidate(self, outcome_id: str, memory_id: str, memory_type: str, summary: str, confidence: float, entity_id: str, idempotency_key: str) -> dict:
        rows = self.executor.write(
            "memory.create_candidate",
            """
            MATCH (o:Outcome {tenant_id:$tenant_id, id:$outcome_id})
            MATCH (entity {tenant_id:$tenant_id, id:$entity_id})
            MERGE (m:Memory {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET m.id=$memory_id, m.memory_type=$memory_type, m.summary=$summary,
                          m.confidence=$confidence, m.status='candidate', m.synthetic=true,
                          m.source='runtime', m.created_at=timestamp()
            MERGE (m)-[:DERIVED_FROM {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(o)
            MERGE (m)-[:ABOUT {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(entity)
            RETURN m.id, m.status
            """,
            self.params(outcome_id=outcome_id, memory_id=memory_id, memory_type=memory_type, summary=summary, confidence=confidence, entity_id=entity_id, idempotency_key=idempotency_key),
            result_limit=1,
        ).rows
        return {"id": rows[0][0], "status": rows[0][1]}

    def supersede(self, old_memory_id: str, new_memory_id: str) -> dict:
        rows = self.executor.write(
            "memory.supersede",
            """
            MATCH (old:Memory {tenant_id:$tenant_id, id:$old_id})
            MATCH (new:Memory {tenant_id:$tenant_id, id:$new_id})
            SET old.status='superseded', old.superseded_at=timestamp()
            MERGE (new)-[:SUPERSEDES {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(old)
            RETURN old.id, old.status, new.id
            """,
            self.params(old_id=old_memory_id, new_id=new_memory_id),
            result_limit=1,
        ).rows
        return {"old_id": rows[0][0], "old_status": rows[0][1], "new_id": rows[0][2]}
