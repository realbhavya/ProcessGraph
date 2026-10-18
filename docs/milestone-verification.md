# Milestone Verification Guide

A milestone is accepted only when all four gates pass:

1. **Implementation:** required files and functionality exist.
2. **Automated verification:** tests and validation scripts pass.
3. **Runtime demonstration:** the main outcome can be shown from a clean setup.
4. **Documentation:** setup, expected outputs, limits, and troubleshooting are recorded.

A milestone must not be marked complete merely because its source files exist.

---

## Milestone 0 verification

### Purpose

Verify the repository foundation, backend shell, frontend shell, configuration, documentation, and automated test setup.

### Clean setup

From the repository root:

```bash
cp .env.example .env
docker compose up --build -d
```

### Automated checks

Install local backend development dependencies once:

```bash
cd backend
python -m pip install -e '.[dev]'
cd ..
```

Run:

```bash
./scripts/check_m0.sh
```

Expected final line:

```text
[M0] Milestone 0 checks passed
```

### Runtime checks

Check API health:

```bash
curl -i http://localhost:8000/health
```

Expected:

- HTTP status `200`
- JSON field `"status": "ok"`
- Response header `X-Request-ID`

Open the frontend:

```text
http://localhost:3001
```

Expected:

- Page displays `ProcessGraph Sentinel`
- Backend status changes to `connected`
- No internal competition-track labels are shown
- Safety disclaimer is visible

Open API documentation:

```text
http://localhost:8000/docs
```

Expected:

- `/health` and `/ready` are listed

### Milestone 0 acceptance criteria

- Repository structure exists.
- `.env.example` exists and `.env` is ignored by Git.
- Backend starts.
- Frontend starts.
- Health endpoint passes.
- Automated tests pass.
- Requirements, architecture, and safety documents exist.
- No secrets are committed.

---

## Milestone 1 verification

### Purpose

Verify the real FalkorDB connection, graph-aware readiness, repeatable seed data, required graph relationships, tenant metadata, synthetic-data metadata, and graph validation.

### Start the stack

```bash
docker compose up --build -d
```

Inspect service status:

```bash
docker compose ps
```

Expected:

- `processgraph-falkordb` is running and healthy
- `processgraph-backend` is running and healthy
- `processgraph-frontend` is running

If a service is not healthy:

```bash
docker compose logs --tail=200 falkordb backend frontend
```

### Seed and validate the graph

```bash
./scripts/seed.sh
```

Expected:

- Seed script reports the graph name and seeded counts
- Validation JSON ends with `"valid": true`
- Every item under `assertions` is `true`

Run the complete milestone check:

```bash
./scripts/check_m1.sh
```

Expected final line:

```text
[M1] Milestone 1 checks passed
```

### Verify graph-aware readiness

```bash
curl -i http://localhost:8000/ready
```

Expected:

```json
{
  "status": "ready",
  "checks": {
    "api": "ok",
    "falkordb": "ok"
  }
}
```

The endpoint must return HTTP `503` rather than a false success when FalkorDB is unavailable. Test this deliberately:

```bash
docker compose stop falkordb
curl -i http://localhost:8000/ready
docker compose start falkordb
```

Expected while FalkorDB is stopped:

- HTTP status `503`
- `"status": "not_ready"`
- FalkorDB check begins with `unavailable:`

### Verify the central graph path

Open FalkorDB Browser:

```text
http://localhost:3000
```

Connect using the password configured in `.env`, select graph:

```text
processgraph_tenant_demo
```

Run:

```cypher
MATCH path =
  (reactor:Equipment {
    tenant_id: 'TENANT-DEMO',
    id: 'EQ-R-101'
  })
  -[:COOLED_BY|SUPPLIED_BY|DEPENDS_ON*1..5]-
  (pump:Equipment {
    tenant_id: 'TENANT-DEMO',
    id: 'EQ-P-201'
  })
RETURN path
```

Expected path includes:

```text
R-101 → E-101 → Cooling Water CW-201 → P-201
```

### Verify the connected maintenance finding

```cypher
MATCH
  (finding:MaintenanceFinding {
    tenant_id: 'TENANT-DEMO'
  })-[:ABOUT]->
  (pump:Equipment {
    tenant_id: 'TENANT-DEMO',
    id: 'EQ-P-201'
  })
WHERE finding.status IN ['open', 'monitoring']
RETURN pump.name, finding.id, finding.summary, finding.severity, finding.status
```

Expected result includes:

```text
P-201 | MF-001 | P-201 vibration increasing | high | open
```

### Verify graph-derived ownership

```cypher
MATCH
  (team:Team {
    tenant_id: 'TENANT-DEMO'
  })-[:OWNS]->
  (pump:Equipment {
    tenant_id: 'TENANT-DEMO',
    id: 'EQ-P-201'
  })
RETURN team.id, team.name, pump.name
```

Expected:

```text
TEAM-UTIL | Utilities Team | P-201
```

### Verify data quality

```cypher
MATCH (n)
RETURN count(n) AS total_nodes
```

Expected after a clean reset and seed:

```text
187
```

```cypher
MATCH ()-[r]->()
RETURN count(r) AS total_relationships
```

Expected after a clean reset and seed:

```text
244
```

```cypher
MATCH (n)
WHERE n.tenant_id IS NULL OR n.synthetic <> true OR n.source IS NULL
RETURN count(n) AS invalid_nodes
```

Expected:

```text
0
```

```cypher
MATCH ()-[r]->()
WHERE r.tenant_id IS NULL OR r.synthetic <> true OR r.source IS NULL
RETURN count(r) AS invalid_relationships
```

Expected:

```text
0
```

### Verify idempotency

Run the seed script twice without reset by calling the Python seeder directly:

```bash
python graph/seed/seed.py
python graph/validate.py
```

Expected:

- Node and relationship counts remain unchanged
- Validation remains `"valid": true`
- No duplicate stable IDs appear

Check duplicate IDs:

```cypher
MATCH (n)
WITH n.id AS id, count(n) AS occurrences
WHERE occurrences > 1
RETURN id, occurrences
```

Expected:

```text
No rows
```

### Milestone 1 acceptance criteria

- FalkorDB becomes healthy.
- `/ready` verifies a real graph query.
- Seed and validation commands complete successfully.
- Graph contains 187 nodes and 244 relationships after a clean seed.
- R-101 connects to P-201 through the cooling path.
- P-201 has the expected open finding.
- The Utilities Team owns P-201.
- All nodes and relationships contain tenant and synthetic provenance.
- Repeated seeding does not create duplicates.
- FalkorDB Browser displays the graph.
- Backend tests pass.

---

## Verification format for every later milestone

For each subsequent milestone, add a section containing:

### A. Automated command

One command that runs all milestone-specific tests.

### B. Expected output

Exact terminal markers, status codes, counts, or JSON fields that prove success.

### C. Runtime demonstration

A user-visible sequence that proves the milestone's main capability.

### D. Negative tests

At least one deliberate failure proving that safeguards work, such as an unknown entity, unauthorized tool, duplicate write, stale memory, or rejected approval.

### E. Acceptance checklist

A binary checklist. If any required item fails, the milestone remains incomplete.

---

## Milestone 2 verification

Run one command only:

```bash
./scripts/test_m2.sh
```

The script automatically:

1. Records which Docker Compose services were running before the test.
2. Starts only the services needed for testing.
3. Creates a unique isolated FalkorDB test graph.
4. Runs unit tests.
5. Seeds and validates the isolated graph.
6. Exercises read and write repository methods.
7. verifies idempotent writes and reseeding.
8. Proves the read-only executor rejects writes.
9. Confirms the main application graph was not modified.
10. Deletes the test graph.
11. Stops only services that were not running before the test.

Successful final output:

```text
[RESTORE] Project state restored successfully
[M2] ALL TESTS PASSED
```

If a test fails, cleanup still runs and the final output states that the previous project state was restored after failure.
