from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class FindingStatus(StrEnum):
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    REJECTED = "rejected"


class EvidenceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entity_id: str = Field(min_length=3, max_length=100)
    entity_type: str = Field(min_length=2, max_length=80)
    source: Literal["current_graph", "current_observation", "historical_incident", "memory", "procedure"]
    path_node_ids: list[str] = Field(default_factory=list, max_length=20)
    path_relationships: list[str] = Field(default_factory=list, max_length=20)


class SpecialistFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    finding_id: str = Field(pattern=r"^FIND-[A-Z0-9-]+$")
    task_id: str = Field(pattern=r"^TASK-[A-Z0-9-]+$")
    agent_id: str = Field(pattern=r"^AGENT-[A-Z0-9-]+$")
    category: Literal["connectivity", "safety", "maintenance", "memory"]
    summary: str = Field(min_length=15, max_length=1200)
    confidence: float = Field(ge=0, le=1)
    evidence: list[EvidenceReference] = Field(min_length=1, max_length=20)
    limitations: list[str] = Field(default_factory=list, max_length=10)


class ValidatedFinding(BaseModel):
    finding: SpecialistFinding
    status: FindingStatus
    validation_reasons: list[str]


class InvestigationSummary(BaseModel):
    investigation_id: str
    incident_id: str
    status: Literal["COMPLETED", "PARTIAL", "FAILED"]
    validated_findings: list[ValidatedFinding]
    rejected_findings: list[ValidatedFinding]
    handoff_ids: list[str]
    failed_tasks: list[dict[str, Any]]
    summary: str
