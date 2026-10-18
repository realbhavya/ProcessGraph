import pytest

from app.tools.contracts import AgentRole
from app.tools.permissions import ToolAuthorizationError, authorize


def test_connectivity_agent_can_trace_but_not_propose_action():
    authorize("trace_utility_path", AgentRole.CONNECTIVITY)
    with pytest.raises(ToolAuthorizationError):
        authorize("propose_action", AgentRole.CONNECTIVITY)


def test_action_agent_cannot_record_specialist_finding():
    with pytest.raises(ToolAuthorizationError):
        authorize("record_finding", AgentRole.ACTION)


def test_orchestrator_can_create_tasks():
    authorize("create_investigation_task", AgentRole.ORCHESTRATOR)
