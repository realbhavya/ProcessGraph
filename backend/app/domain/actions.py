from enum import StrEnum
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class ActionType(StrEnum):
    CREATE_INSPECTION_TASK="CREATE_INSPECTION_TASK"
    REQUEST_ADDITIONAL_OBSERVATION="REQUEST_ADDITIONAL_OBSERVATION"
    ESCALATE_TO_TEAM="ESCALATE_TO_TEAM"
    REVIEW_SAFEGUARD_STATUS="REVIEW_SAFEGUARD_STATUS"
    ATTACH_RELEVANT_PROCEDURE="ATTACH_RELEVANT_PROCEDURE"
    MARK_EVIDENCE_INSUFFICIENT="MARK_EVIDENCE_INSUFFICIENT"

class ActionProposal(BaseModel):
    model_config=ConfigDict(extra="forbid")
    finding_id:str=Field(pattern=r"^FIND-[A-Z0-9-]+$")
    team_id:str=Field(pattern=r"^TEAM-[A-Z0-9-]+$")
    action_type:ActionType
    summary:str=Field(min_length=15,max_length=1000)
    rationale:str=Field(min_length=15,max_length=1000)
    reversibility:Literal["reversible","administrative"]

class ActionDecision(BaseModel):
    model_config=ConfigDict(extra="forbid")
    decision:Literal["approve","reject"]
    reviewer_id:str=Field(min_length=3,max_length=100)
    reason:str=Field(min_length=10,max_length=500)

class ActionExecutionRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    executor_id:str=Field(min_length=3,max_length=100)
    mode:Literal["simulation"]="simulation"
