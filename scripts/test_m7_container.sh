#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace
cleanup(){ code=$?; set +e; echo "[RESTORE] Removing isolated test graph: $FALKORDB_GRAPH_NAME"; python graph/reset.py >/dev/null 2>&1 || true; [[ $code -eq 0 ]] && echo "[M7-CONTAINER] TESTS PASSED" || echo "[M7-CONTAINER] TESTS FAILED with exit code $code"; exit $code; }
trap cleanup EXIT INT TERM
echo "[TEST] Unit and safety-policy tests"; python -m pytest -q backend
echo "[TEST] Seed isolated graph"; python graph/seed/seed.py --reset; python graph/validate.py
echo "[TEST] Human-gated action lifecycle"; python tests/integration/action_governance_smoke.py
echo "[TEST] Graph integrity after action lifecycle"; python graph/validate.py
