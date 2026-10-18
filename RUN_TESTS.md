# Run Milestone 2 Tests

## Windows

From PowerShell, run:

```powershell
.\test_m2.bat
```

or:

```powershell
powershell -ExecutionPolicy Bypass -File .\test_m2.ps1
```

The Windows test runner now uses Docker for Python and Bash. You do **not** need Python, Git Bash, or WSL installed. You only need Docker Desktop with the Linux container engine running.

## macOS or Linux

```bash
./scripts/test_m2.sh
```

## Successful result

```text
[RESULT] ALL TESTS PASSED
[RESTORE] Project state restored successfully
```

The detailed output is saved to:

```text
test-results/milestone-2-latest.log
```

### Docker capability warnings

Messages such as `No blkio throttle.read_bps_device support` can be emitted by Docker Desktop as non-fatal capability warnings. The Windows runner captures stderr separately and uses Docker's process exit code, so these warnings no longer cause a false test failure.

### Docker Compose progress on stderr

Docker Compose writes normal status messages such as `Container processgraph-falkordb Running` to stderr. The Windows runner executes the test command through `cmd.exe`, captures stdout and stderr separately, prints both, and determines success only from Docker's numeric exit code. Normal progress output no longer becomes a PowerShell exception.

### Empty temporary graph reset

A newly generated test graph does not exist until its first write. Some FalkorDB versions return `Invalid graph operation on empty key` when asked to delete that not-yet-created graph. The seed and cleanup utilities treat this specific response as an idempotent no-op, while still raising unexpected deletion errors.

### Baseline validation versus runtime growth

The integration test intentionally adds runtime workflow nodes. Validation therefore checks that the required seed baseline is still present (`incidents >= 8`, `memories >= 3`). Reseed idempotency is tested separately by comparing total node and relationship counts immediately before and after reseeding; those counts must be identical.

### Graph selection isolation

Tenant mapping is now a pure function and deployment graph overrides are applied only at the graph-selection boundary. The Windows runner exports the unique test graph before Docker Compose creates the backend container, ensuring the API and test runner use the same isolated graph. Regression tests verify both behaviors and prevent ambient environment variables from changing tenant-mapping unit tests.

### Domain-aware graph validation

The validator now separates immutable seeded reference data from mutable runtime data. Seeded labels are counted exactly using `source='processgraph-sentinel-seed-v1'`. Runtime observations, incidents, and timeline events are allowed to grow and are validated through structural invariants: observations must belong to incidents, incidents must belong to sessions and affect equipment, timeline events must belong to incidents, and every node and relationship must retain tenant and source provenance. This avoids weakening validation while correctly supporting normal application growth.

### Upgrading over an older extracted folder

The compatibility regression-test filename is intentionally retained and now contains the current domain-aware assertions. This allows a newer package extracted over an older working directory to overwrite the superseded test rather than leave a stale file behind. For the cleanest upgrade, extracting into a new directory remains recommended.

### FalkorDB-compatible orphan detection

Runtime orphan checks use an `OPTIONAL MATCH` anti-join followed by grouped link counts. This is compatible with the FalkorDB Cypher parser used by the Docker image and preserves tenant-scoped structural validation. The validator does not use Neo4j-style `EXISTS { MATCH ... }` subquery syntax.

### Audit completeness

The MCP test executes eight tool invocations, including an idempotent write retry and an authorization denial. It requires exactly eight audit events, three task-creation audit records, two successful task attempts, and one `UNAUTHORIZED_TOOL` denial. Audit event identity is distinct from request correlation identity.

### Supersession-aware retrieval compatibility

Active-memory search uses a FalkorDB-compatible `OPTIONAL MATCH` anti-join to detect an incoming `SUPERSEDES` relationship. A memory is excluded only when another active replacement points to it. The replacement memory remains retrievable even though it has an outgoing `SUPERSEDES` edge. Integration failures now report HTTP status, content type, and body instead of failing with an opaque JSON decoder error.

### Candidate isolation with seeded active memory

The seed graph intentionally contains approved baseline memories for `EQ-R-101`. Candidate isolation is therefore verified by identity: the newly created candidate must not appear before approval, while existing active baseline memories must remain retrievable. After approval, the new memory must appear without removing the baseline memories. This tests the actual governance invariant without assuming an empty memory store.

### Action test provenance

The action lifecycle test now creates an incident and runs the real multi-agent investigation workflow, then selects its validated maintenance finding. It no longer injects a privileged `Finding` directly with raw Cypher. This verifies the full chain from observations to evidence validation to human-gated action execution. Unexpected API failures are logged with request correlation and returned as structured `INTERNAL_ERROR` responses without exposing internal exception text.

### FalkorDB-compatible action proposal write

The action proposal repository now uses the established repository query shape already used by the workflow layer: prerequisite `MATCH` clauses, an explicit validated-status predicate, idempotent action `MERGE`, and provenance relationship merges. Parameters are projected explicitly rather than expanded from an unbounded mapping. On any future container failure, the Windows runner appends the final 200 backend log lines to the milestone log before restoring services.

### Repository package export regression

The action repository is now imported into `app.graph.repositories.__init__`, not merely named in `__all__`. A regression test performs the same public-package import used by the FastAPI dependency factory, ensuring image builds cannot pass while runtime dependency resolution fails.

### Windows PowerShell image-pull output

Docker Compose writes normal image-pull progress to stderr. Windows PowerShell 5.1 can convert stderr emitted through a native pipeline into a terminating `NativeCommandError` when `$ErrorActionPreference` is `Stop`. The Milestone 8 runner now invokes the frontend Compose command through `Start-Process` with separately redirected stdout and stderr, prints both streams, and evaluates the real process exit code. A line such as `Image node:22-alpine Pulling` is therefore treated as progress, not failure.

### Psycopg 3 batch execution

`executemany()` belongs to a Psycopg 3 cursor rather than the connection object. Tag registration and observation insertion now open transaction-scoped cursors and execute batches through those cursors. Regression tests exercise the exact API boundary and reject any future `connection.executemany` usage.

### Unique pytest module names

The backend test directories are intentionally not Python packages. Pytest therefore imports same-named test files as the same top-level module. The OPC UA contract test now has a domain-specific unique filename, and a repository-wide regression test rejects duplicate `test_*.py` basenames before they can cause an import-file mismatch.

### Pytest import isolation

The backend suite now enforces `--import-mode=importlib`. This prevents same-basename tests in different directories from being imported as one top-level module, and also makes verification robust when a corrected archive is accidentally overlaid onto an older extraction containing a stale test file. The release archive itself contains only the uniquely named OPC UA contract test.

### Archive-overlay migration

Milestone 12 now performs an explicit migration before building test images. It removes only two obsolete test files from earlier corrected M12 archives: `backend/tests/opcua/test_contracts.py` and `backend/tests/test_test_module_names.py`. It also clears backend test caches. This makes an in-place upgrade behave like a clean extraction without deleting current tests or weakening the full regression suite.
