from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from sentinel_mcp.factory import build_service
from app.tools.contracts import (
    CreateHandoffInput, CreateTaskInput, EquipmentInput, EquipmentTraversalInput,
    InvestigationStateInput, MemoryInput, ProposeActionInput, ProposeMemoryInput,
    RecordFindingInput, RecordOutcomeInput, ResolveEquipmentInput,
)

mcp = FastMCP("ProcessGraph Sentinel Tools", json_response=True)


def service():
    return build_service()


@mcp.tool()
def resolve_equipment(input: ResolveEquipmentInput) -> dict:
    """Resolve an exact synthetic equipment name to its stable graph identity."""
    s = service()
    return s.execute("resolve_equipment", input, lambda: s.equipment.resolve(input.equipment_name), ["equipment.resolve"])


@mcp.tool()
def trace_process_impact(input: EquipmentTraversalInput) -> dict:
    """Trace bounded process-flow connections from a resolved equipment entity."""
    s = service()
    return s.execute("trace_process_impact", input, lambda: s.equipment.trace_process_impact(input.equipment_id, input.max_depth), ["equipment.process_impact"])


@mcp.tool()
def trace_utility_path(input: EquipmentTraversalInput) -> dict:
    """Trace bounded cooling, supply, and dependency paths."""
    s = service()
    return s.execute("trace_utility_path", input, lambda: s.equipment.trace_utility_path(input.equipment_id, input.max_depth), ["equipment.utility_path"])


@mcp.tool()
def find_connected_sensors(input: EquipmentInput) -> dict:
    """Find sensors and measured parameters directly connected to equipment."""
    s = service()
    return s.execute("find_connected_sensors", input, lambda: s.equipment.connected_sensors(input.equipment_id), ["equipment.sensors"])


@mcp.tool()
def find_related_safeguards(input: EquipmentInput) -> dict:
    """Retrieve designed safeguards and mitigated hazards for equipment."""
    s = service()
    return s.execute("find_related_safeguards", input, lambda: s.context.safeguards(input.equipment_id), ["context.safeguards"])


@mcp.tool()
def find_open_maintenance_findings(input: EquipmentTraversalInput) -> dict:
    """Find open findings on equipment reachable through bounded utility dependencies."""
    s = service()
    return s.execute("find_open_maintenance_findings", input, lambda: s.context.open_findings(input.equipment_id, input.max_depth), ["context.open_findings"])


@mcp.tool()
def find_responsible_team(input: EquipmentInput) -> dict:
    """Resolve the graph-derived owning team for equipment."""
    s = service()
    return s.execute("find_responsible_team", input, lambda: s.context.responsible_team(input.equipment_id), ["context.owner"])


@mcp.tool()
def find_related_incidents(input: EquipmentInput) -> dict:
    """Retrieve historical incidents, linked actions, and outcomes for equipment."""
    s = service()
    return s.execute("find_related_incidents", input, lambda: s.context.related_incidents(input.equipment_id), ["context.related_incidents"])


@mcp.tool()
def retrieve_active_memories(input: MemoryInput) -> dict:
    """Retrieve active, provenance-linked memories about a graph entity."""
    s = service()
    return s.execute("retrieve_active_memories", input, lambda: s.context.active_memories(input.entity_id, input.limit), ["context.active_memories"])


@mcp.tool()
def get_investigation_state(input: InvestigationStateInput) -> dict:
    """Return the current graph-backed incident state and timeline."""
    s = service()
    return s.execute("get_investigation_state", input, lambda: {"incident": s.incidents.get(input.incident_id), "timeline": s.incidents.timeline(input.incident_id)}, ["incident.get", "incident.timeline"])


@mcp.tool()
def get_evidence_paths(input: InvestigationStateInput) -> dict:
    """Return bounded evidence paths from equipment affected by an incident."""
    s = service()
    return s.execute("get_evidence_paths", input, lambda: s.incidents.paths(input.incident_id, 4), ["incident.paths"])


@mcp.tool()
def create_investigation_task(input: CreateTaskInput) -> dict:
    """Create one idempotent investigation task assigned to an allowed agent."""
    s = service()
    return s.execute("create_investigation_task", input, lambda: s.workflow.create_task(input.incident_id, input.task_id, input.agent_id, input.task_type, input.idempotency_key), ["workflow.create_task"])


@mcp.tool()
def record_finding(input: RecordFindingInput) -> dict:
    """Record an evidence-linked specialist finding."""
    s = service()
    return s.execute("record_finding", input, lambda: s.workflow.record_finding(input.task_id, input.finding_id, input.summary, input.confidence, input.evidence_entity_id, input.idempotency_key), ["workflow.record_finding"])


@mcp.tool()
def create_handoff(input: CreateHandoffInput) -> dict:
    """Create an explicit, auditable handoff between specialist agents."""
    s = service()
    return s.execute("create_handoff", input, lambda: s.workflow.create_handoff(input.task_id, input.handoff_id, input.from_agent_id, input.to_agent_id, input.reason, input.idempotency_key), ["workflow.create_handoff"])


@mcp.tool()
def propose_action(input: ProposeActionInput) -> dict:
    """Propose an allow-listed action linked to a finding and responsible team."""
    s = service()
    return s.execute("propose_action", input, lambda: s.workflow.propose_action(input.finding_id, input.action_id, input.team_id, input.action_type, input.summary, input.idempotency_key), ["workflow.propose_action"])


@mcp.tool()
def record_action_outcome(input: RecordOutcomeInput) -> dict:
    """Record the synthetic outcome of an approved action."""
    s = service()
    return s.execute("record_action_outcome", input, lambda: s.workflow.record_outcome(input.action_id, input.outcome_id, input.summary, input.effectiveness, input.idempotency_key), ["workflow.record_outcome"])


@mcp.tool()
def propose_memory(input: ProposeMemoryInput) -> dict:
    """Create a governed memory candidate from an action outcome."""
    s = service()
    return s.execute("propose_memory", input, lambda: s.memory.create_candidate(input.outcome_id, input.memory_id, input.memory_type, input.summary, input.confidence, input.entity_id, input.idempotency_key), ["memory.create_candidate"])


if __name__ == "__main__":
    mcp.run(transport=os.getenv("MCP_TRANSPORT", "stdio"))
