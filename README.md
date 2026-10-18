# ProcessGraph Sentinel

Graph-native multi-agent incident triage and persistent memory for a **synthetic chemical-process plant**.

## Tracks

- Track 01: Agents That Act on Connected Data
- Track 02: Agent Memory and Coordination

## Milestone 1 status

Milestone 1 adds:

- FalkorDB connectivity and graph-aware readiness
- Repeatable synthetic plant graph seeding
- 24 equipment nodes, 14 streams, 12 sensors, 20 observations, 30 procedure steps, utilities, hazards, safeguards, teams, findings, incidents, outcomes, agents, and memories
- Idempotent `MERGE`-based seed operations
- Graph reset and validation utilities
- Central R-101 to P-201 cooling-path proof
- Complete graph-data-model and synthetic-data documentation

## Prerequisites

- Docker Engine 24+
- Docker Compose v2
- Optional script execution outside containers: Python 3.12+

## Quick start

```bash
cp .env.example .env
docker compose up --build -d
```

Install the backend package locally when running seed scripts from the host:

```bash
cd backend
python -m pip install -e '.[dev]'
cd ..
```

Seed and validate the graph:

```bash
./scripts/seed.sh
```

Open:

- Frontend: http://localhost:3001
- Backend health: http://localhost:8000/health
- Backend readiness: http://localhost:8000/ready
- OpenAPI: http://localhost:8000/docs
- FalkorDB Browser: http://localhost:3000

Run validation again:

```bash
python graph/validate.py
```

Run tests:

```bash
python -m pytest -q backend
```

## Expected critical graph path

```text
R-101
→ COOLED_BY → E-101
→ SUPPLIED_BY → Cooling Water CW-201
→ SUPPLIED_BY → P-201
```

The graph also shows that P-201 has an open vibration finding and is owned by the Utilities Team.

## Safety

This is a synthetic decision-support demonstration. It must not be used to control equipment or replace qualified personnel. See `docs/safety-boundaries.md`.

## Verify implementation

Use the complete verification guide:

```text
docs/milestone-verification.md
```

For the current project state:

```bash
./scripts/check_m0.sh
./scripts/seed.sh
./scripts/check_m1.sh
```

Do not accept a milestone based only on file presence. Its automated checks, runtime demonstration, negative test, and documentation gate must all pass.

## Milestone 2: one-command verification

```bash
./scripts/test_m2.sh
```

The test suite uses a unique isolated graph and restores the previous project state when it finishes, whether it passes or fails.

### If the test command appears to show no output

Use the platform launcher in the repository root:

- Windows: double-click `test_m2.bat`
- PowerShell: `powershell -ExecutionPolicy Bypass -File .\test_m2.ps1`
- macOS/Linux: `./scripts/test_m2.sh`

The runner prints progress immediately and writes a live log to `test-results/milestone-2-latest.log`.

### Windows test prerequisites

On Windows, the milestone test runs Python and Bash inside Docker. Host Python, Git Bash, and WSL are not required. Start Docker Desktop, then run:

```powershell
.\test_m2.bat
```

## Milestone 3 verification

Windows:

```powershell
.\test_m3.bat
```

The test runs the real API against an isolated graph, verifies idempotency, state-transition safety, timeline creation, path retrieval, graph integrity, and restores the previous service state.

## Milestone 4 verification

```powershell
.\test_m4.bat
```

The test validates typed MCP tools, role authorization, real FalkorDB reads and writes, idempotency, audit events, absence of arbitrary Cypher exposure, graph integrity, test-graph cleanup, and service-state restoration.

## Milestone 5 verification

```powershell
.\test_m5.bat
```

The test creates a real incident, runs parallel specialists through permission-aware tools, records an explicit graph handoff, validates evidence, retrieves shared investigation state, validates graph integrity, deletes the isolated graph, and restores prior services.

## Milestone 6 verification
```powershell
.\test_m6.bat
```
The test verifies candidate isolation, policy thresholds, approval, active retrieval, replacement, supersession, provenance, graph integrity, cleanup, and restoration.

## Milestone 7 verification
```powershell
.\test_m7.bat
```
This verifies human-gated, simulation-only action execution, plus safety policy, provenance, cleanup, and restoration.

## Milestone 8 verification
```powershell
.\test_m8.bat
```
After verification, run `docker compose up -d --build` and open `http://localhost:8080` for the evidence-first operator workspace.

## Milestone 9 verification
```powershell
.\test_m9.bat
```
The deterministic evaluation report is written to `evals/results/milestone-9-report.json` inside the test workspace and printed in full to `test-results/milestone-9-latest.log`.

## Milestone 10 release gate
```powershell
.\test_m10.bat
```
This is the final operational-hardening gate: regression tests, production smoke, formal evaluations, metrics, security assertions, graph integrity, cleanup, and restoration.

## Milestone 11: published real-data foundation

Start PostgreSQL, then use the containerized loader to download the CC0 Rieth Tennessee Eastman dataset from Harvard Dataverse:
```powershell
docker compose up -d timeseries
docker compose --profile data run --rm realdata-loader python realdata/cli.py download
```
Import the original RData files into PostgreSQL:
```powershell
docker compose --profile data run --rm realdata-loader python realdata/cli.py import
```
The system records source DOI, URL, timestamp, archive checksum, file checksums, split, run, fault, sample, tag, value, unit mapping, and quality status. It never labels this benchmark as live commercial-plant data.

## Milestone 12: OPC UA live replay

After importing the real TEP benchmark, start the read-only replay and collector:
```powershell
docker compose --profile live up -d --build opcua-replay opcua-collector
```
The local endpoint is `opc.tcp://localhost:4840/processgraph/tep/`. Process variables are read-only. This development endpoint is not configured for external exposure; production OT use requires certificates, trust lists, authentication, and network segmentation.
