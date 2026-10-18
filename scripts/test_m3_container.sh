#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace
cleanup() {
  local code=$?
  set +e
  echo "[RESTORE] Removing isolated test graph: $FALKORDB_GRAPH_NAME"
  python graph/reset.py >/dev/null 2>&1 || true
  [[ $code -eq 0 ]] && echo "[M3-CONTAINER] TESTS PASSED" || echo "[M3-CONTAINER] TESTS FAILED with exit code $code"
  exit $code
}
trap cleanup EXIT INT TERM

echo "[TEST] Backend unit tests"
python -m pytest -q backend

echo "[TEST] Seed isolated graph"
python graph/seed/seed.py --reset
python graph/validate.py

echo "[TEST] Incident API lifecycle"
python tests/integration/incident_api_smoke.py

echo "[TEST] Graph integrity after API workflow"
python graph/validate.py
