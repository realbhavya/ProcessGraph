from __future__ import annotations

from app.graph.errors import GraphError
from app.tools.contracts import AgentRole


TOOL_PERMISSIONS: dict[str, frozenset[AgentRole]] = {
    "resolve_equipment": frozenset({AgentRole.ORCHESTRATOR, AgentRole.CONNECTIVITY, AgentRole.SAFETY, AgentRole.MAINTENANCE_MEMORY}),
    "trace_process_impact": frozenset({AgentRole.ORCHESTRATOR, AgentRole.CONNECTIVITY}),
    "trace_utility_path": frozenset({AgentRole.ORCHESTRATOR, AgentRole.CONNECTIVITY}),
    "find_connected_sensors": frozenset({AgentRole.ORCHESTRATOR, AgentRole.CONNECTIVITY, AgentRole.SAFETY}),
    "find_related_safeguards": frozenset({AgentRole.ORCHESTRATOR, AgentRole.SAFETY}),
    "find_open_maintenance_findings": frozenset({AgentRole.ORCHESTRATOR, AgentRole.MAINTENANCE_MEMORY}),
    "find_responsible_team": frozenset({AgentRole.ORCHESTRATOR, AgentRole.ACTION}),
    "find_related_incidents": frozenset({AgentRole.ORCHESTRATOR, AgentRole.MAINTENANCE_MEMORY}),
    "retrieve_active_memories": frozenset({AgentRole.ORCHESTRATOR, AgentRole.MAINTENANCE_MEMORY}),
    "get_investigation_state": frozenset(set(AgentRole)),
    "get_evidence_paths": frozenset(set(AgentRole)),
    "create_investigation_task": frozenset({AgentRole.ORCHESTRATOR}),
    "record_finding": frozenset({AgentRole.CONNECTIVITY, AgentRole.SAFETY, AgentRole.MAINTENANCE_MEMORY}),
    "create_handoff": frozenset({AgentRole.ORCHESTRATOR, AgentRole.CONNECTIVITY, AgentRole.SAFETY, AgentRole.MAINTENANCE_MEMORY}),
    "propose_action": frozenset({AgentRole.ACTION}),
    "record_action_outcome": frozenset({AgentRole.ACTION}),
    "propose_memory": frozenset({AgentRole.MAINTENANCE_MEMORY}),
}


class ToolAuthorizationError(GraphError):
    def __init__(self, role: AgentRole, tool_name: str):
        super().__init__("UNAUTHORIZED_TOOL", f"Role {role.value} is not permitted to call {tool_name}")


def authorize(tool_name: str, role: AgentRole) -> None:
    allowed = TOOL_PERMISSIONS.get(tool_name, frozenset())
    if role not in allowed:
        raise ToolAuthorizationError(role, tool_name)
