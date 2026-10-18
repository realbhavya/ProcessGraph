from app.domain.memory import MemoryCandidateCreate, MemoryType
from app.memory.service import MemoryService
class Repo:
 def create_candidate(self,**kwargs): return kwargs
def test_candidate_id_is_idempotent():
 svc=MemoryService(Repo()); p=MemoryCandidateCreate(outcome_id="OUT-HIST-001",entity_id="EQ-R-101",memory_type=MemoryType.EPISODIC,summary="A sufficiently detailed evidence-grounded memory candidate.",confidence=.9,evidence_ids=["INC-HIST-001"])
 assert svc.create_candidate(p,"memory-key-001")["memory_id"]==svc.create_candidate(p,"memory-key-001")["memory_id"]
