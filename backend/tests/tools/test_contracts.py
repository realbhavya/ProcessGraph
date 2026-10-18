import pytest
from pydantic import ValidationError

from app.tools.contracts import AgentRole, EquipmentTraversalInput, ProposeActionInput


def test_depth_and_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        EquipmentTraversalInput(tenant_id="TENANT-DEMO", agent_role=AgentRole.CONNECTIVITY, request_id="request-123", equipment_id="EQ-R-101", max_depth=9)
    with pytest.raises(ValidationError):
        EquipmentTraversalInput(tenant_id="TENANT-DEMO", agent_role=AgentRole.CONNECTIVITY, request_id="request-123", equipment_id="EQ-R-101", unexpected=True)


def test_action_type_is_allow_listed():
    with pytest.raises(ValidationError):
        ProposeActionInput(tenant_id="TENANT-DEMO", agent_role=AgentRole.ACTION, request_id="request-123", idempotency_key="idem-12345", finding_id="FIND-1", action_id="ACTION-1", team_id="TEAM-UTIL", action_type="CHANGE_SETPOINT", summary="This prohibited action must not validate")
