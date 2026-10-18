from app.actions.service import ActionService
from app.domain.actions import ActionProposal,ActionType
class Repo:
 def propose(self,*args): return args
def test_action_id_is_idempotent():
 s=ActionService(Repo()); p=ActionProposal(finding_id="FIND-1",team_id="TEAM-UTIL",action_type=ActionType.CREATE_INSPECTION_TASK,summary="Create a synthetic inspection workflow task.",rationale="Validated evidence supports an inspection request.",reversibility="administrative")
 assert s.propose(p,"action-key-001")[0]==s.propose(p,"action-key-001")[0]
