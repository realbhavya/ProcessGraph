from __future__ import annotations

from dataclasses import dataclass

from app.domain.memory import MemoryCandidateCreate, MemoryType
from app.graph.errors import InvalidInput


@dataclass(frozen=True)
class MemoryPolicy:
    minimum_confidence: dict[MemoryType, float]
    require_expiry_for_semantic: bool = True

    @classmethod
    def default(cls) -> "MemoryPolicy":
        return cls({
            MemoryType.EPISODIC: 0.70,
            MemoryType.SEMANTIC: 0.85,
            MemoryType.PROCEDURAL: 0.90,
        })

    def validate_candidate(self, candidate: MemoryCandidateCreate) -> None:
        threshold = self.minimum_confidence[candidate.memory_type]
        if candidate.confidence < threshold:
            raise InvalidInput(
                f"{candidate.memory_type.value} memory requires confidence >= {threshold:.2f}"
            )
        if candidate.memory_type == MemoryType.SEMANTIC and self.require_expiry_for_semantic and candidate.valid_until is None:
            raise InvalidInput("Semantic memory requires valid_until to prevent indefinite stale facts")
        if len(set(candidate.evidence_ids)) != len(candidate.evidence_ids):
            raise InvalidInput("evidence_ids must be unique")
