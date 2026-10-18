from app.domain.investigations import EvidenceReference, SpecialistFinding
from app.validation.evidence import EvidenceValidator


def finding(entity="EQ-P-201", nodes=None, rels=None):
    return SpecialistFinding(finding_id="FIND-1",task_id="TASK-1",agent_id="AGENT-CONN",category="connectivity",summary="Evidence-grounded connected equipment finding",confidence=.9,evidence=[EvidenceReference(entity_id=entity,entity_type="Equipment",source="current_graph",path_node_ids=nodes or [],path_relationships=rels or [])])


def test_valid_evidence_is_accepted():
    assert EvidenceValidator(lambda _:True).validate(finding()).status.value=="validated"


def test_nonexistent_evidence_is_rejected():
    result=EvidenceValidator(lambda _:False).validate(finding("EQ-X"))
    assert result.status.value=="rejected"


def test_inconsistent_path_is_rejected():
    result=EvidenceValidator(lambda _:True).validate(finding(nodes=["A","B"],rels=[]))
    assert result.status.value=="rejected"
