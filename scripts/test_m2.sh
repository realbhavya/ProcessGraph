#!/usr/bin/env bash
set -Eeuo pipefail
printf '%s\n' '============================================================'
printf '%s\n' ' ProcessGraph Sentinel - Milestone 2 Verification'
printf '%s\n' '============================================================'
printf '%s\n' '[START] Initializing test runner...'
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p test-results
LOG_FILE="$ROOT/test-results/milestone-2-latest.log"
exec > >(tee "$LOG_FILE") 2>&1
echo "[LOG] Live output is also saved to: $LOG_FILE"
TEST_GRAPH="processgraph_test_$(date +%s)_$$"
ORIGINAL_RUNNING=""
MAIN_SNAPSHOT=""
CLEANUP_DONE=0

cleanup() {
  local exit_code=$?
  if [[ "$CLEANUP_DONE" -eq 1 ]]; then exit "$exit_code"; fi
  CLEANUP_DONE=1
  set +e
  echo "[RESTORE] Removing isolated test graph: $TEST_GRAPH"
  FALKORDB_GRAPH_NAME="$TEST_GRAPH" python graph/reset.py >/dev/null 2>&1 || true
  [[ -n "$MAIN_SNAPSHOT" ]] && rm -f "$MAIN_SNAPSHOT"
  if command -v docker >/dev/null 2>&1; then
    local now_running
    now_running="$(docker compose ps --services --status running 2>/dev/null || true)"
    while IFS= read -r service; do
      [[ -z "$service" ]] && continue
      if ! grep -qx "$service" <<<"$ORIGINAL_RUNNING"; then
        echo "[RESTORE] Stopping service started by test: $service"
        docker compose stop "$service" >/dev/null 2>&1 || true
      fi
    done <<<"$now_running"
  fi
  if [[ "$exit_code" -eq 0 ]]; then
    echo "[RESTORE] Project state restored successfully"
    echo "[M2] ALL TESTS PASSED"
  else
    echo "[RESTORE] Project state restored after test failure"
    echo "[M2] TESTS FAILED with exit code $exit_code"
  fi
  exit "$exit_code"
}
trap cleanup EXIT INT TERM

echo "[CHECK] Verifying required commands..."
command -v docker >/dev/null 2>&1 || { echo "[ERROR] Docker was not found. Install Docker Desktop and reopen the terminal."; exit 2; }
command -v python >/dev/null 2>&1 || { echo "[ERROR] Python was not found in PATH."; exit 2; }
echo "[CHECK] Docker and Python found"
docker compose version || { echo "[ERROR] Docker Compose is unavailable"; exit 2; }
[[ -f .env ]] || cp .env.example .env
set -a
source ./.env
set +a
export FALKORDB_HOST=localhost
export FALKORDB_PORT="${FALKORDB_PORT:-6379}"
export FALKORDB_GRAPH_NAME="$TEST_GRAPH"
ORIGINAL_RUNNING="$(docker compose ps --services --status running 2>/dev/null || true)"
echo "[SETUP] Original running services: ${ORIGINAL_RUNNING:-none}"
echo "[SETUP] Building and starting containers. This can take several minutes on the first run..."
docker compose up --build -d falkordb backend frontend
echo "[SETUP] Containers started"

echo "[WAIT] Waiting for FalkorDB..."
for attempt in {1..30}; do
  echo "[WAIT] FalkorDB readiness attempt $attempt/30"
  if python -c "from falkordb import FalkorDB; FalkorDB(host='localhost',port=int('${FALKORDB_PORT}'),password='${FALKORDB_PASSWORD}').select_graph('${TEST_GRAPH}').query('RETURN 1')" >/dev/null 2>&1; then break; fi
  [[ "$attempt" == 30 ]] && { echo "FalkorDB did not become ready"; exit 3; }
  sleep 2
done

MAIN_SNAPSHOT="$(mktemp)"
echo "[SETUP] Snapshotting main graph"
python -c "import json; from falkordb import FalkorDB; db=FalkorDB(host='localhost',port=int('${FALKORDB_PORT}'),password='${FALKORDB_PASSWORD}'); g=db.select_graph('processgraph_tenant_demo'); print(json.dumps(g.ro_query('MATCH (n) OPTIONAL MATCH (n)-[r]->() RETURN count(DISTINCT n), count(r)').result_set[0]))" > "$MAIN_SNAPSHOT" 2>/dev/null || echo 'null' > "$MAIN_SNAPSHOT"

echo "[TEST] Unit tests"
python -m pytest -q backend

echo "[TEST] Seed and validate isolated graph"
python graph/seed/seed.py --reset
python graph/validate.py

echo "[TEST] Repository integration"
PYTHONPATH=backend python tests/integration/repository_smoke.py

echo "[TEST] Idempotent reseed"
python graph/seed/seed.py
python graph/validate.py

echo "[TEST] Read-only enforcement"
PYTHONPATH=backend python - <<'PY'
import os
from falkordb import FalkorDB
from app.graph.executor import GraphExecutor
g=FalkorDB(host='localhost',port=int(os.getenv('FALKORDB_PORT','6379')),password=os.getenv('FALKORDB_PASSWORD')).select_graph(os.environ['FALKORDB_GRAPH_NAME'])
before=g.ro_query('MATCH (n) RETURN count(n)').result_set[0][0]
blocked=False
try:
    GraphExecutor(g).read('negative.read_only', 'CREATE (:Forbidden)')
except Exception:
    blocked=True
assert blocked, 'Read-only path unexpectedly accepted a write'
after=g.ro_query('MATCH (n) RETURN count(n)').result_set[0][0]
assert before == after
print('[M2] read-only enforcement passed')
PY

echo "[TEST] Main graph isolation"
AFTER_SNAPSHOT="$(mktemp)"
python -c "import json; from falkordb import FalkorDB; db=FalkorDB(host='localhost',port=int('${FALKORDB_PORT}'),password='${FALKORDB_PASSWORD}'); g=db.select_graph('processgraph_tenant_demo'); print(json.dumps(g.ro_query('MATCH (n) OPTIONAL MATCH (n)-[r]->() RETURN count(DISTINCT n), count(r)').result_set[0]))" > "$AFTER_SNAPSHOT" 2>/dev/null || echo 'null' > "$AFTER_SNAPSHOT"
cmp -s "$MAIN_SNAPSHOT" "$AFTER_SNAPSHOT"
rm -f "$AFTER_SNAPSHOT"
echo "[M2] main graph isolation passed"
