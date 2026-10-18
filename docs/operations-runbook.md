# Operations Runbook

## Start
`docker compose up -d --build`

## Verify
Check `/health`, `/ready`, `/api/v1/system/capabilities`, and `/metrics`. Open the UI at `http://localhost:8080`.

## Observability
Start Prometheus with `docker compose --profile observability up -d prometheus`, then open `http://localhost:9090`.

## Incident response
Capture `docker compose ps`, backend logs, request ID, graph name, and capability response. Do not reset or reseed an application graph during diagnosis.

## Backup
Run `python ops/backup_graph.py` with the desired graph and backup path. The export is a diagnostic node snapshot, not a transactional restore image.

## Recovery
Restore infrastructure from controlled deployment artifacts, verify credentials, validate graph integrity, run the complete milestone gate, and only then return traffic.
