from app.graph.client import get_database, selected_graph_name
from app.graph.executor import GraphExecutor
from app.graph.repositories.audit import AuditRepository
from app.graph.repositories.context import ContextRepository
from app.graph.repositories.equipment import EquipmentRepository
from app.graph.repositories.incident import IncidentRepository
from app.graph.repositories.memory import MemoryRepository
from app.graph.repositories.workflow import WorkflowRepository
from app.tools.service import ToolService


def build_service() -> ToolService:
    graph_name = selected_graph_name()
    graph = get_database().select_graph(graph_name)
    executor = GraphExecutor(graph, timeout_ms=5000, result_limit=200)
    return ToolService(
        equipment=EquipmentRepository(executor),
        context=ContextRepository(executor),
        incidents=IncidentRepository(executor),
        workflow=WorkflowRepository(executor),
        memory=MemoryRepository(executor),
        audit=AuditRepository(executor),
        graph_name=graph_name,
    )
