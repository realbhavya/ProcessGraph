import pytest

from app.domain.incidents import IncidentCreate, IncidentState, ObservationCreate
from app.graph.errors import InvalidInput
from app.services.incidents import IncidentService


class EquipmentRepo:
    def resolve(self, name):
        return {"id": "EQ-R-101", "name": name, "type": "reactor", "criticality": "high", "status": "active"}


class IncidentRepo:
    def __init__(self):
        self.state = "RECEIVED"
        self.received = None

    def create_incident_bundle(self, **kwargs):
        self.received = kwargs
        return {"id": kwargs["incident_id"], "session_id": kwargs["session_id"], "summary": kwargs["summary"], "status": "RECEIVED", "equipment": kwargs["equipment"], "observations": kwargs["observations"], "created_at": 1}

    def current_state(self, incident_id):
        return self.state

    def transition(self, **kwargs):
        self.state = kwargs["target_state"]
        return {"id": kwargs["incident_id"], "status": self.state}


def test_create_uses_stable_ids_and_resolution():
    repository = IncidentRepo()
    service = IncidentService(EquipmentRepo(), repository)
    payload = IncidentCreate(summary="R-101 temperature is high", equipment_names=["R-101"], observations=[ObservationCreate(parameter="temperature", qualifier="high")])
    first = service.create(payload, idempotency_key="request-0001", request_id="req-1")
    second = service.create(payload, idempotency_key="request-0001", request_id="req-2")
    assert first["id"] == second["id"]
    assert first["session_id"] == second["session_id"]
    assert repository.received["equipment"][0]["id"] == "EQ-R-101"


def test_state_machine_blocks_invalid_jump():
    service = IncidentService(EquipmentRepo(), IncidentRepo())
    with pytest.raises(InvalidInput, match="not allowed"):
        service.transition("INC-1", IncidentState.COMPLETED, "invalid jump", idempotency_key="transition-1", request_id="req")


def test_state_machine_allows_valid_transition():
    repository = IncidentRepo()
    service = IncidentService(EquipmentRepo(), repository)
    result = service.transition("INC-1", IncidentState.VALIDATING, "begin validation", idempotency_key="transition-1", request_id="req")
    assert result["status"] == "VALIDATING"
