from __future__ import annotations
from hashlib import sha256
from time import time
from app.domain.memory import MemoryCandidateCreate, MemoryReviewDecision, MemorySearchRequest, MemorySupersedeRequest
from app.memory.policy import MemoryPolicy

class MemoryService:
    def __init__(self, repository, policy=None): self.repository=repository; self.policy=policy or MemoryPolicy.default()
    @staticmethod
    def stable_id(prefix,key): return f"{prefix}-{sha256(key.encode()).hexdigest()[:16].upper()}"
    def create_candidate(self,payload:MemoryCandidateCreate,key:str):
        self.policy.validate_candidate(payload)
        data=payload.model_dump(mode="json"); data["memory_type"]=payload.memory_type.value
        return self.repository.create_candidate(memory_id=self.stable_id("MEM",key),candidate=data,idempotency_key=key)
    def review(self,memory_id,payload:MemoryReviewDecision,key):
        return self.repository.review(memory_id=memory_id,decision=payload.decision,reason=payload.reason,reviewer_id=payload.reviewer_id,review_id=self.stable_id("MEMREV",key),idempotency_key=key)
    def supersede(self,memory_id,payload:MemorySupersedeRequest,key):
        return self.repository.supersede(old_memory_id=memory_id,new_memory_id=payload.replacement_memory_id,reason=payload.reason,reviewer_id=payload.reviewer_id,review_id=self.stable_id("MEMREV",key),idempotency_key=key)
    def search(self,payload:MemorySearchRequest):
        now_ms=int(time()*1000); self.repository.expire_stale(now_ms)
        return self.repository.retrieve_active(entity_id=payload.entity_id,memory_types=[x.value for x in payload.memory_types],limit=payload.limit,min_confidence=payload.min_confidence,now_ms=now_ms)
