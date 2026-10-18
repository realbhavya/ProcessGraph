from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AgentRole(StrEnum):
    ORCHESTRATOR = "orchestrator"
    CONNECTIVITY = "connectivity"
    SAFETY = "safety"
    MAINTENANCE_MEMORY = "maintenance_memory"
    ACTION = "action"


class ToolError(BaseModel):
    code: str
    message: str
    retryable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class ToolEvidence(BaseModel):
    query_ids: list[str] = Field(default_factory=list)
    graph_name: str
    executed_at: str


class ToolResult(BaseModel):
    request_id: str
    tool_name: str
    status: Literal["success", "error"]
    data: Any | None = None
    evidence: ToolEvidence | None = None
    error: ToolError | None = None


class ToolContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenant_id: str = Field(pattern=r"^TENANT-[A-Z0-9-]+$")
    agent_role: AgentRole
    request_id: str = Field(min_length=8, max_length=100)
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=200)


class ResolveEquipmentInput(ToolContext):
    equipment_name: str = Field(min_length=1, max_length=80)


class EquipmentTraversalInput(ToolContext):
    equipment_id: str = Field(pattern=r"^EQ-[A-Z0-9-]+$")
    max_depth: int = Field(default=4, ge=1, le=4)


class EquipmentInput(ToolContext):
    equipment_id: str = Field(pattern=r"^EQ-[A-Z0-9-]+$")


class MemoryInput(ToolContext):
    entity_id: str = Field(min_length=3, max_length=100)
    limit: int = Field(default=10, ge=1, le=50)


class InvestigationStateInput(ToolContext):
    incident_id: str = Field(pattern=r"^INC-[A-Z0-9-]+$")


class CreateTaskInput(ToolContext):
    incident_id: str = Field(pattern=r"^INC-[A-Z0-9-]+$")
    task_id: str = Field(pattern=r"^TASK-[A-Z0-9-]+$")
    agent_id: str = Field(pattern=r"^AGENT-[A-Z0-9-]+$")
    task_type: str = Field(min_length=3, max_length=80)


class RecordFindingInput(ToolContext):
    task_id: str = Field(pattern=r"^TASK-[A-Z0-9-]+$")
    finding_id: str = Field(pattern=r"^FIND-[A-Z0-9-]+$")
    summary: str = Field(min_length=10, max_length=1000)
    confidence: float = Field(ge=0, le=1)
    evidence_entity_id: str = Field(min_length=3, max_length=100)


class CreateHandoffInput(ToolContext):
    task_id: str = Field(pattern=r"^TASK-[A-Z0-9-]+$")
    handoff_id: str = Field(pattern=r"^HANDOFF-[A-Z0-9-]+$")
    from_agent_id: str = Field(pattern=r"^AGENT-[A-Z0-9-]+$")
    to_agent_id: str = Field(pattern=r"^AGENT-[A-Z0-9-]+$")
    reason: str = Field(min_length=5, max_length=500)


class ProposeActionInput(ToolContext):
    finding_id: str = Field(pattern=r"^FIND-[A-Z0-9-]+$")
    action_id: str = Field(pattern=r"^ACTION-[A-Z0-9-]+$")
    team_id: str = Field(pattern=r"^TEAM-[A-Z0-9-]+$")
    action_type: Literal[
        "CREATE_INSPECTION_TASK",
        "REQUEST_ADDITIONAL_OBSERVATION",
        "ESCALATE_TO_TEAM",
        "REVIEW_SAFEGUARD_STATUS",
        "ATTACH_RELEVANT_PROCEDURE",
        "MARK_EVIDENCE_INSUFFICIENT",
    ]
    summary: str = Field(min_length=10, max_length=1000)


class RecordOutcomeInput(ToolContext):
    action_id: str = Field(pattern=r"^ACTION-[A-Z0-9-]+$")
    outcome_id: str = Field(pattern=r"^OUT-[A-Z0-9-]+$")
    summary: str = Field(min_length=10, max_length=1000)
    effectiveness: Literal["helpful", "neutral", "unhelpful", "inconclusive"]


class ProposeMemoryInput(ToolContext):
    outcome_id: str = Field(pattern=r"^OUT-[A-Z0-9-]+$")
    memory_id: str = Field(pattern=r"^MEM-[A-Z0-9-]+$")
    memory_type: Literal["episodic", "semantic", "procedural"]
    summary: str = Field(min_length=10, max_length=1500)
    confidence: float = Field(ge=0, le=1)
    entity_id: str = Field(min_length=3, max_length=100)
