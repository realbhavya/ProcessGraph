from fastapi import APIRouter,Depends
from app.api.dependencies import require_idempotency_key
from app.domain.actions import ActionDecision,ActionExecutionRequest,ActionProposal
router=APIRouter(prefix="/api/v1/actions",tags=["actions"])
def service():
 from app.actions.service import ActionService
 from app.graph.client import get_graph
 from app.graph.executor import GraphExecutor
 from app.graph.repositories import ActionGovernanceRepository
 return ActionService(ActionGovernanceRepository(GraphExecutor(get_graph(),timeout_ms=5000,result_limit=100)))
@router.post("/proposals",status_code=201)
def propose(payload:ActionProposal,key:str=Depends(require_idempotency_key),svc=Depends(service)): return svc.propose(payload,key)
@router.post("/{action_id}/decision")
def decide(action_id:str,payload:ActionDecision,key:str=Depends(require_idempotency_key),svc=Depends(service)): return svc.decide(action_id,payload,key)
@router.post("/{action_id}/execute")
def execute(action_id:str,payload:ActionExecutionRequest,key:str=Depends(require_idempotency_key),svc=Depends(service)): return svc.execute(action_id,payload,key)
@router.get("/{action_id}")
def get_action(action_id:str,svc=Depends(service)): return svc.repository.get(action_id)
