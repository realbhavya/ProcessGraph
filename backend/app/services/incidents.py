from __future__ import annotations

from hashlib import sha256
from uuid import uuid4

from app.domain.incidents import ALLOWED_TRANSITIONS, IncidentCreate, IncidentState, ObservationCreate
from app.graph.errors import InvalidInput


class IncidentService:
    def __init__(self, equipment_repository, incident_repository):
        self.equipment = equipment_repository
        self.incidents = incident_repository

    @staticmethod
    def stable_id(prefix: str, idempotency_key: str, discriminator: str = "") -> str:
        digest = sha256(f"{idempotency_key}:{discriminator}".encode()).hexdigest()[:16].upper()
        return f"{prefix}-{digest}"

    def create(self, payload: IncidentCreate, *, idempotency_key: str, request_id: str) -> dict:
        resolved = [self.equipment.resolve(name) for name in payload.equipment_names]
        incident_id = self.stable_id("INC", idempotency_key)
        session_id = self.stable_id("SESSION", idempotency_key)
        observations = []
        for index, observation in enumerate(payload.observations):
            data = observation.model_dump()
            data.update({
                "id": self.stable_id("OBS", idempotency_key, str(index)),
                "idempotency_key": f"{idempotency_key}:observation:{index}",
            })
            observations.append(data)
        return self.incidents.create_incident_bundle(
            session_id=session_id,
            incident_id=incident_id,
            summary=payload.summary,
            equipment=resolved,
            observations=observations,
            idempotency_key=idempotency_key,
            request_id=request_id,
        )

    def add_observation(self, incident_id: str, payload: ObservationCreate, *, idempotency_key: str, request_id: str) -> dict:
        data = payload.model_dump()
        data["id"] = self.stable_id("OBS", idempotency_key)
        return self.incidents.add_observation(incident_id=incident_id, observation=data, idempotency_key=idempotency_key, request_id=request_id)

    def transition(self, incident_id: str, target: IncidentState, reason: str, *, idempotency_key: str, request_id: str) -> dict:
        current = IncidentState(self.incidents.current_state(incident_id))
        if target not in ALLOWED_TRANSITIONS[current]:
            raise InvalidInput(f"Transition from {current} to {target} is not allowed")
        return self.incidents.transition(
            incident_id=incident_id,
            expected_state=current.value,
            target_state=target.value,
            reason=reason,
            event_id=self.stable_id("EVENT", idempotency_key),
            idempotency_key=idempotency_key,
            request_id=request_id,
        )
