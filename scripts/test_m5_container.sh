#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace
cleanup(){ code=$?; set +e; echo "[RESTORE] Removing isolated test graph: $FALKORDB_GRAPH_NAME"; python graph/reset.py >/dev/null 2>&1 || true; [[ $code -eq 0 ]] && echo "[M5-CONTAINER] TESTS PASSED" || echo "[M5-CONTAINER] TESTS FAILED with exit code $code"; exit $code; }
trap cleanup EXIT INT TERM
echo "[TEST] Unit and architecture tests"; python -m pytest -q backend
echo "[TEST] Seed isolated graph"; python graph/seed/seed.py --reset; python graph/validate.py
echo "[TEST] Multi-agent workflow"; python tests/integration/agent_workflow_smoke.py
echo "[TEST] Graph integrity after workflow"; python graph/validate.py
