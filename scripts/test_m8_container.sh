#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace
cleanup(){ code=$?; set +e; echo "[RESTORE] Removing isolated test graph: $FALKORDB_GRAPH_NAME"; python graph/reset.py >/dev/null 2>&1 || true; [[ $code -eq 0 ]] && echo "[M8-CONTAINER] TESTS PASSED" || echo "[M8-CONTAINER] TESTS FAILED with exit code $code"; exit $code; }
trap cleanup EXIT INT TERM
echo "[TEST] Backend regression suite"; python -m pytest -q backend
echo "[TEST] Frontend source contract"; test -f frontend/src/main.jsx; test -f frontend/src/api.js; grep -q "validated_findings" frontend/src/main.jsx; grep -q "Idempotency-Key" frontend/src/api.js
echo "[TEST] Seed and validate isolated graph"; python graph/seed/seed.py --reset; python graph/validate.py
echo "[TEST] Dashboard API workflow"; python tests/integration/agent_workflow_smoke.py
echo "[TEST] Final graph integrity"; python graph/validate.py
