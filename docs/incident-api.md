# Incident Lifecycle API

## Endpoints

- `POST /api/v1/incidents`
- `GET /api/v1/incidents/{incident_id}`
- `POST /api/v1/incidents/{incident_id}/observations`
- `POST /api/v1/incidents/{incident_id}/state`
- `GET /api/v1/incidents/{incident_id}/timeline`
- `GET /api/v1/incidents/{incident_id}/paths`

All mutating requests require `Idempotency-Key`. Incident creation resolves all equipment before graph mutation. State changes are accepted only when permitted by the explicit state machine and when the stored state still matches the expected source state.
