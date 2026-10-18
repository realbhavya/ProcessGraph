import pytest
from app.actions.policy import ActionPolicy
from app.domain.actions import ActionProposal,ActionType
from app.graph.errors import InvalidInput
def proposal(**x):
 d={"finding_id":"FIND-1","team_id":"TEAM-UTIL","action_type":ActionType.CREATE_INSPECTION_TASK,"summary":"Create a synthetic inspection workflow task.","rationale":"Validated evidence supports an inspection request.","reversibility":"administrative"}; d.update(x); return ActionProposal(**d)
def test_allowed_action_passes(): ActionPolicy().validate(proposal())
def test_direct_control_language_rejected():
 with pytest.raises(InvalidInput): ActionPolicy().validate(proposal(summary="Close valve immediately at the cooling header."))
