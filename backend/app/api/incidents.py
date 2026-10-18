from fastapi import APIRouter, Depends, Query, Request, status

from app.api.dependencies import incident_service, require_idempotency_key
from app.domain.incidents import IncidentCreate, IncidentResponse, IncidentStateUpdate, ObservationCreate, ObservationResponse, PathResponse, TimelineEventResponse
from app.services.incidents import IncidentService

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, request: Request, key: str = Depends(require_idempotency_key), service: IncidentService = Depends(incident_service)):
    return service.create(payload, idempotency_key=key, request_id=request.state.request_id)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: str, service: IncidentService = Depends(incident_service)):
    return service.incidents.get(incident_id)


@router.post("/{incident_id}/observations", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
def add_observation(incident_id: str, payload: ObservationCreate, request: Request, key: str = Depends(require_idempotency_key), service: IncidentService = Depends(incident_service)):
    return service.add_observation(incident_id, payload, idempotency_key=key, request_id=request.state.request_id)


@router.post("/{incident_id}/state")
def transition_incident(incident_id: str, payload: IncidentStateUpdate, request: Request, key: str = Depends(require_idempotency_key), service: IncidentService = Depends(incident_service)):
    return service.transition(incident_id, payload.target_state, payload.reason, idempotency_key=key, request_id=request.state.request_id)


@router.get("/{incident_id}/timeline", response_model=list[TimelineEventResponse])
def incident_timeline(incident_id: str, service: IncidentService = Depends(incident_service)):
    return service.incidents.timeline(incident_id)


@router.get("/{incident_id}/paths", response_model=list[PathResponse])
def incident_paths(incident_id: str, depth: int = Query(default=4, ge=1, le=4), service: IncidentService = Depends(incident_service)):
    return service.incidents.paths(incident_id, depth)


@router.post("/{incident_id}/investigate")
def investigate_incident(incident_id: str, key: str = Depends(require_idempotency_key), workflow=Depends(__import__('app.api.dependencies', fromlist=['investigation_workflow']).investigation_workflow)):
    return workflow.run(incident_id, key)


@router.get("/{incident_id}/investigation/{investigation_id}")
def get_investigation(incident_id: str, investigation_id: str, workflow=Depends(__import__('app.api.dependencies', fromlist=['investigation_workflow']).investigation_workflow)):
    result = workflow.repo.get(investigation_id)
    if result["incident_id"] != incident_id:
        from app.graph.errors import EntityNotFound
        raise EntityNotFound(investigation_id)
    return result
