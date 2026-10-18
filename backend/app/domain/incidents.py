from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class IncidentState(StrEnum):
    RECEIVED = "RECEIVED"
    VALIDATING = "VALIDATING"
    ENTITY_RESOLUTION = "ENTITY_RESOLUTION"
    INVESTIGATING = "INVESTIGATING"
    EVIDENCE_VALIDATION = "EVIDENCE_VALIDATION"
    ACTION_PROPOSED = "ACTION_PROPOSED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    IN_PROGRESS = "IN_PROGRESS"
    OUTCOME_RECORDED = "OUTCOME_RECORDED"
    MEMORY_REVIEW = "MEMORY_REVIEW"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


ALLOWED_TRANSITIONS: dict[IncidentState, set[IncidentState]] = {
    IncidentState.RECEIVED: {IncidentState.VALIDATING, IncidentState.FAILED},
    IncidentState.VALIDATING: {IncidentState.ENTITY_RESOLUTION, IncidentState.FAILED},
    IncidentState.ENTITY_RESOLUTION: {IncidentState.INVESTIGATING, IncidentState.FAILED},
    IncidentState.INVESTIGATING: {IncidentState.EVIDENCE_VALIDATION, IncidentState.FAILED},
    IncidentState.EVIDENCE_VALIDATION: {IncidentState.ACTION_PROPOSED, IncidentState.INVESTIGATING, IncidentState.FAILED},
    IncidentState.ACTION_PROPOSED: {IncidentState.AWAITING_APPROVAL, IncidentState.FAILED},
    IncidentState.AWAITING_APPROVAL: {IncidentState.IN_PROGRESS, IncidentState.FAILED},
    IncidentState.IN_PROGRESS: {IncidentState.OUTCOME_RECORDED, IncidentState.FAILED},
    IncidentState.OUTCOME_RECORDED: {IncidentState.MEMORY_REVIEW, IncidentState.COMPLETED, IncidentState.FAILED},
    IncidentState.MEMORY_REVIEW: {IncidentState.COMPLETED, IncidentState.FAILED},
    IncidentState.COMPLETED: set(),
    IncidentState.FAILED: set(),
}


class ObservationCreate(BaseModel):
    parameter: str = Field(min_length=1, max_length=80)
    qualifier: Literal["high", "low", "falling", "rising", "elevated", "normal", "unknown"]
    value: float | None = None
    unit: str | None = Field(default=None, max_length=30)
    sensor_name: str | None = Field(default=None, max_length=80)

    @field_validator("parameter", "sensor_name")
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value


class IncidentCreate(BaseModel):
    summary: str = Field(min_length=10, max_length=1000)
    equipment_names: list[str] = Field(min_length=1, max_length=10)
    observations: list[ObservationCreate] = Field(default_factory=list, max_length=50)

    @field_validator("summary")
    @classmethod
    def normalize_summary(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("equipment_names")
    @classmethod
    def normalize_equipment_names(cls, values: list[str]) -> list[str]:
        result = []
        for value in values:
            cleaned = value.strip()
            if not cleaned or len(cleaned) > 80:
                raise ValueError("equipment names must contain 1 to 80 characters")
            if cleaned not in result:
                result.append(cleaned)
        return result


class IncidentStateUpdate(BaseModel):
    target_state: IncidentState
    reason: str = Field(min_length=3, max_length=500)


class ObservationResponse(BaseModel):
    id: str
    parameter: str
    qualifier: str
    value: float | None
    unit: str | None
    sensor_name: str | None


class IncidentResponse(BaseModel):
    id: str
    session_id: str
    summary: str
    status: IncidentState
    equipment: list[dict]
    observations: list[ObservationResponse]
    created_at: int


class TimelineEventResponse(BaseModel):
    id: str
    event_type: str
    actor_type: str
    actor_id: str
    previous_state: str | None
    new_state: str | None
    reason: str
    request_id: str
    created_at: int


class PathResponse(BaseModel):
    source_id: str
    target_id: str
    hops: int
    node_ids: list[str]
    node_names: list[str]
    relationships: list[str]
