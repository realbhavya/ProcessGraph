from fastapi import Header, HTTPException, Request

from app.graph.client import get_graph
from app.graph.executor import GraphExecutor
from app.graph.repositories import EquipmentRepository, IncidentRepository
from app.services.incidents import IncidentService


def require_idempotency_key(idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")) -> str:
    if not idempotency_key or not 8 <= len(idempotency_key) <= 200:
        raise HTTPException(status_code=400, detail={"code": "INVALID_INPUT", "message": "Idempotency-Key header must contain 8 to 200 characters"})
    return idempotency_key


def request_id(request: Request) -> str:
    return request.state.request_id


def incident_service() -> IncidentService:
    executor = GraphExecutor(get_graph(), timeout_ms=5000, result_limit=200)
    return IncidentService(EquipmentRepository(executor), IncidentRepository(executor))


def investigation_workflow():
    from app.graph.client import selected_graph_name
    from app.graph.repositories import ContextRepository, EquipmentRepository, IncidentRepository, InvestigationRepository, MemoryRepository, WorkflowRepository
    from app.graph.repositories.audit import AuditRepository
    from app.tools.service import ToolService
    from app.workflows.investigation import InvestigationWorkflow
    executor = GraphExecutor(get_graph(), timeout_ms=5000, result_limit=200)
    tools = ToolService(
        equipment=EquipmentRepository(executor), context=ContextRepository(executor),
        incidents=IncidentRepository(executor), workflow=WorkflowRepository(executor),
        memory=MemoryRepository(executor), audit=AuditRepository(executor),
        graph_name=selected_graph_name(),
    )
    return InvestigationWorkflow(
        investigation_repository=InvestigationRepository(executor),
        incident_repository=IncidentRepository(executor), tool_service=tools,
    )
