from fastapi import APIRouter, Depends
from app.api.dependencies import require_idempotency_key
from app.domain.memory import MemoryCandidateCreate, MemoryReviewDecision, MemorySearchRequest, MemorySupersedeRequest
router=APIRouter(prefix="/api/v1/memories",tags=["memories"])
def service():
 from app.graph.client import get_graph
 from app.graph.executor import GraphExecutor
 from app.graph.repositories import MemoryGovernanceRepository
 from app.memory.service import MemoryService
 return MemoryService(MemoryGovernanceRepository(GraphExecutor(get_graph(),timeout_ms=5000,result_limit=100)))
@router.post("/candidates",status_code=201)
def create_candidate(payload:MemoryCandidateCreate,key:str=Depends(require_idempotency_key),svc=Depends(service)): return svc.create_candidate(payload,key)
@router.post("/{memory_id}/review")
def review_memory(memory_id:str,payload:MemoryReviewDecision,key:str=Depends(require_idempotency_key),svc=Depends(service)): return svc.review(memory_id,payload,key)
@router.post("/{memory_id}/supersede")
def supersede_memory(memory_id:str,payload:MemorySupersedeRequest,key:str=Depends(require_idempotency_key),svc=Depends(service)): return svc.supersede(memory_id,payload,key)
@router.post("/search")
def search_memories(payload:MemorySearchRequest,svc=Depends(service)): return svc.search(payload)
@router.get("/{memory_id}")
def get_memory(memory_id:str,svc=Depends(service)): return svc.repository.get(memory_id)
