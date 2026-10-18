import pytest
from app.domain.memory import MemoryCandidateCreate, MemoryType
from app.graph.errors import InvalidInput
from app.memory.policy import MemoryPolicy

def candidate(**overrides):
 values={"outcome_id":"OUT-HIST-001","entity_id":"EQ-R-101","memory_type":MemoryType.EPISODIC,"summary":"A sufficiently detailed evidence-grounded memory candidate.","confidence":.9,"evidence_ids":["INC-HIST-001"]}; values.update(overrides); return MemoryCandidateCreate(**values)
def test_low_confidence_rejected():
 with pytest.raises(InvalidInput): MemoryPolicy.default().validate_candidate(candidate(confidence=.2))
def test_semantic_requires_expiry():
 with pytest.raises(InvalidInput): MemoryPolicy.default().validate_candidate(candidate(memory_type=MemoryType.SEMANTIC,confidence=.9))
def test_duplicate_evidence_rejected():
 with pytest.raises(InvalidInput): MemoryPolicy.default().validate_candidate(candidate(evidence_ids=["A","A"]))
