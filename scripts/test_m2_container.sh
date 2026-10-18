#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace
TEST_GRAPH="${FALKORDB_GRAPH_NAME:?FALKORDB_GRAPH_NAME is required}"
cleanup() {
  local code=$?
  set +e
  echo "[RESTORE] Removing isolated test graph: $TEST_GRAPH"
  python graph/reset.py >/dev/null 2>&1 || true
  if [[ $code -eq 0 ]]; then
    echo "[M2-CONTAINER] TESTS PASSED"
  else
    echo "[M2-CONTAINER] TESTS FAILED with exit code $code"
  fi
  exit $code
}
trap cleanup EXIT INT TERM

echo "[TEST] Unit tests"
python -m pytest -q backend

echo "[TEST] Seed and validate isolated graph"
python graph/seed/seed.py --reset
python graph/validate.py

echo "[TEST] Repository integration"
python tests/integration/repository_smoke.py

echo "[TEST] Idempotent reseed"
BEFORE_RESEED="$(python -c "import json,os; from falkordb import FalkorDB; g=FalkorDB(host=os.getenv('FALKORDB_HOST','falkordb'),port=6379,password=os.getenv('FALKORDB_PASSWORD')).select_graph(os.environ['FALKORDB_GRAPH_NAME']); row=g.ro_query('MATCH (n) OPTIONAL MATCH (n)-[r]->() RETURN count(DISTINCT n), count(r)').result_set[0]; print(json.dumps({'nodes':row[0],'relationships':row[1]}))")"
python graph/seed/seed.py
python graph/validate.py
AFTER_RESEED="$(python -c "import json,os; from falkordb import FalkorDB; g=FalkorDB(host=os.getenv('FALKORDB_HOST','falkordb'),port=6379,password=os.getenv('FALKORDB_PASSWORD')).select_graph(os.environ['FALKORDB_GRAPH_NAME']); row=g.ro_query('MATCH (n) OPTIONAL MATCH (n)-[r]->() RETURN count(DISTINCT n), count(r)').result_set[0]; print(json.dumps({'nodes':row[0],'relationships':row[1]}))")"
if [[ "$BEFORE_RESEED" != "$AFTER_RESEED" ]]; then
  echo "[ERROR] Reseed changed graph counts"
  echo "Before: $BEFORE_RESEED"
  echo "After:  $AFTER_RESEED"
  exit 1
fi
echo "[M2] idempotent reseed passed: $AFTER_RESEED"

echo "[TEST] Read-only enforcement"
python - <<'PY'
import os
from falkordb import FalkorDB
from app.graph.executor import GraphExecutor
g=FalkorDB(host=os.getenv('FALKORDB_HOST','falkordb'),port=6379,password=os.getenv('FALKORDB_PASSWORD')).select_graph(os.environ['FALKORDB_GRAPH_NAME'])
before=g.ro_query('MATCH (n) RETURN count(n)').result_set[0][0]
blocked=False
try:
    GraphExecutor(g).read('negative.read_only', 'CREATE (:Forbidden)')
except Exception:
    blocked=True
assert blocked
assert before == g.ro_query('MATCH (n) RETURN count(n)').result_set[0][0]
print('[M2] read-only enforcement passed')
PY
