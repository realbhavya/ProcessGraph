from __future__ import annotations

from app.graph.errors import EntityNotFound, InvalidInput
from app.graph.repositories.base import BaseRepository


class MemoryGovernanceRepository(BaseRepository):
    def create_candidate(self, *, memory_id: str, candidate: dict, idempotency_key: str) -> dict:
        rows = self.executor.write(
            "memory_governance.create_candidate",
            """
            MATCH (outcome:Outcome {tenant_id:$tenant_id, id:$outcome_id})
            MATCH (entity {tenant_id:$tenant_id, id:$entity_id})
            MERGE (memory:Memory {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET memory.id=$memory_id, memory.memory_type=$memory_type,
                          memory.summary=$summary, memory.confidence=$confidence,
                          memory.status='candidate', memory.valid_until=$valid_until,
                          memory.synthetic=true, memory.source='runtime', memory.created_at=timestamp()
            MERGE (memory)-[:DERIVED_FROM {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(outcome)
            MERGE (memory)-[:ABOUT {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(entity)
            WITH memory
            UNWIND $evidence_ids AS evidence_id
            MATCH (evidence {tenant_id:$tenant_id, id:evidence_id})
            MERGE (memory)-[:SUPPORTED_BY {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(evidence)
            RETURN memory.id, memory.status, memory.memory_type, memory.summary,
                   memory.confidence, memory.valid_until
            """,
            self.params(memory_id=memory_id, idempotency_key=idempotency_key, **candidate),
            result_limit=1,
        ).rows
        if not rows:
            raise InvalidInput("Outcome, entity, or evidence could not be resolved")
        return self._shape(rows[0])

    def review(self, *, memory_id: str, decision: str, reason: str, reviewer_id: str, review_id: str, idempotency_key: str) -> dict:
        target = "active" if decision == "approve" else "rejected"
        rows = self.executor.write(
            "memory_governance.review",
            """
            MATCH (memory:Memory {tenant_id:$tenant_id, id:$memory_id})
            WHERE memory.status='candidate'
            MERGE (review:MemoryReview {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET review.id=$review_id, review.decision=$decision,
                          review.reason=$reason, review.reviewer_id=$reviewer_id,
                          review.synthetic=true, review.source='runtime', review.created_at=timestamp()
            MERGE (memory)-[:HAS_REVIEW {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(review)
            SET memory.status=$target_status, memory.reviewed_at=timestamp()
            RETURN memory.id, memory.status, memory.memory_type, memory.summary,
                   memory.confidence, memory.valid_until
            """,
            self.params(memory_id=memory_id, decision=decision, reason=reason, reviewer_id=reviewer_id, review_id=review_id, idempotency_key=idempotency_key, target_status=target),
            result_limit=1,
        ).rows
        if not rows:
            raise InvalidInput("Memory must exist and be in candidate status")
        return self._shape(rows[0])

    def supersede(self, *, old_memory_id: str, new_memory_id: str, reason: str, reviewer_id: str, review_id: str, idempotency_key: str) -> dict:
        rows = self.executor.write(
            "memory_governance.supersede",
            """
            MATCH (old:Memory {tenant_id:$tenant_id, id:$old_id, status:'active'})
            MATCH (new:Memory {tenant_id:$tenant_id, id:$new_id, status:'active'})
            MERGE (review:MemoryReview {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET review.id=$review_id, review.decision='supersede',
                          review.reason=$reason, review.reviewer_id=$reviewer_id,
                          review.synthetic=true, review.source='runtime', review.created_at=timestamp()
            MERGE (new)-[:SUPERSEDES {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(old)
            MERGE (old)-[:HAS_REVIEW {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(review)
            SET old.status='superseded', old.superseded_at=timestamp()
            RETURN old.id, old.status, new.id
            """,
            self.params(old_id=old_memory_id, new_id=new_memory_id, reason=reason, reviewer_id=reviewer_id, review_id=review_id, idempotency_key=idempotency_key),
            result_limit=1,
        ).rows
        if not rows:
            raise InvalidInput("Both memories must exist and be active before supersession")
        return {"old_memory_id": rows[0][0], "old_status": rows[0][1], "replacement_memory_id": rows[0][2]}

    def retrieve_active(self, *, entity_id: str, memory_types: list[str], limit: int, min_confidence: float, now_ms: int) -> list[dict]:
        rows = self.executor.read(
            "memory_governance.retrieve_active",
            """
            MATCH (memory:Memory {tenant_id:$tenant_id, status:'active'})-[:ABOUT]->
                  (entity {tenant_id:$tenant_id, id:$entity_id})
            WHERE memory.memory_type IN $memory_types
              AND memory.confidence >= $min_confidence
              AND (memory.valid_until IS NULL OR memory.valid_until > $now_ms)
            OPTIONAL MATCH (memory)-[:DERIVED_FROM]->(source)
            OPTIONAL MATCH (memory)-[:SUPPORTED_BY]->(evidence)
            OPTIONAL MATCH (replacement:Memory {tenant_id:$tenant_id})-[:SUPERSEDES]->(memory)
            WITH memory, source, collect(DISTINCT evidence.id) AS evidence_ids,
                 count(DISTINCT replacement) AS replacement_count
            WHERE replacement_count = 0
            RETURN memory.id, memory.status, memory.memory_type, memory.summary,
                   memory.confidence, memory.valid_until, source.id, evidence_ids
            ORDER BY memory.confidence DESC, memory.created_at DESC
            LIMIT $limit
            """,
            self.params(entity_id=entity_id, memory_types=memory_types, min_confidence=min_confidence, now_ms=now_ms, limit=limit),
            result_limit=limit,
        ).rows
        return [self._shape(row, source_id=row[6], evidence_ids=row[7]) for row in rows]

    def expire_stale(self, now_ms: int) -> int:
        rows = self.executor.write(
            "memory_governance.expire_stale",
            """
            MATCH (memory:Memory {tenant_id:$tenant_id, status:'active'})
            WHERE memory.valid_until IS NOT NULL AND memory.valid_until <= $now_ms
            SET memory.status='expired', memory.expired_at=timestamp()
            RETURN count(memory)
            """,
            self.params(now_ms=now_ms), result_limit=1,
        ).rows
        return rows[0][0] if rows else 0

    def get(self, memory_id: str) -> dict:
        rows = self.executor.read(
            "memory_governance.get",
            """
            MATCH (memory:Memory {tenant_id:$tenant_id, id:$memory_id})
            OPTIONAL MATCH (memory)-[:DERIVED_FROM]->(source)
            OPTIONAL MATCH (memory)-[:SUPPORTED_BY]->(evidence)
            OPTIONAL MATCH (memory)-[:HAS_REVIEW]->(review)
            RETURN memory.id, memory.status, memory.memory_type, memory.summary,
                   memory.confidence, memory.valid_until, source.id,
                   collect(DISTINCT evidence.id),
                   collect(DISTINCT {id:review.id, decision:review.decision, reason:review.reason, reviewer_id:review.reviewer_id})
            """,
            self.params(memory_id=memory_id), result_limit=1,
        ).rows
        if not rows:
            raise EntityNotFound(memory_id)
        row=rows[0]
        result=self._shape(row, source_id=row[6], evidence_ids=row[7])
        result["reviews"]=[item for item in row[8] if item.get("id")]
        return result

    @staticmethod
    def _shape(row, source_id=None, evidence_ids=None):
        return {"id":row[0],"status":row[1],"memory_type":row[2],"summary":row[3],"confidence":row[4],"valid_until":row[5],"source_id":source_id,"evidence_ids":evidence_ids or []}
