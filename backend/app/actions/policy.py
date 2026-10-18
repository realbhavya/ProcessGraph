from app.domain.actions import ActionProposal, ActionType
from app.graph.errors import InvalidInput

class ActionPolicy:
    ALLOWED=set(ActionType)
    FORBIDDEN_TERMS={"open valve","close valve","change setpoint","trip","shutdown","start pump","stop pump","bypass interlock"}
    def validate(self, proposal:ActionProposal):
        if proposal.action_type not in self.ALLOWED: raise InvalidInput("Action type is not allowed")
        text=f"{proposal.summary} {proposal.rationale}".lower()
        blocked=sorted(term for term in self.FORBIDDEN_TERMS if term in text)
        if blocked: raise InvalidInput(f"Direct plant-control instruction is forbidden: {blocked[0]}")
