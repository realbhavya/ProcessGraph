from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MemoryType(StrEnum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemoryStatus(StrEnum):
    CANDIDATE = "candidate"
    ACTIVE = "active"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"


class MemoryCandidateCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    outcome_id: str = Field(pattern=r"^OUT-[A-Z0-9-]+$")
    entity_id: str = Field(min_length=3, max_length=100)
    memory_type: MemoryType
    summary: str = Field(min_length=20, max_length=1500)
    confidence: float = Field(ge=0, le=1)
    evidence_ids: list[str] = Field(min_length=1, max_length=20)
    valid_until: int | None = Field(default=None, gt=0)


class MemoryReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: Literal["approve", "reject"]
    reason: str = Field(min_length=10, max_length=500)
    reviewer_id: str = Field(min_length=3, max_length=100)


class MemorySupersedeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    replacement_memory_id: str = Field(pattern=r"^MEM-[A-Z0-9-]+$")
    reason: str = Field(min_length=10, max_length=500)
    reviewer_id: str = Field(min_length=3, max_length=100)


class MemorySearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entity_id: str = Field(min_length=3, max_length=100)
    memory_types: list[MemoryType] = Field(default_factory=lambda: list(MemoryType), min_length=1)
    limit: int = Field(default=10, ge=1, le=50)
    min_confidence: float = Field(default=0.0, ge=0, le=1)
