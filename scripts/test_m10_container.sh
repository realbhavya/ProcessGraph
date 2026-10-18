#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace
cleanup(){ code=$?; set +e; echo "[RESTORE] Removing isolated test graph: $FALKORDB_GRAPH_NAME"; python graph/reset.py >/dev/null 2>&1 || true; [[ $code -eq 0 ]] && echo "[M10-CONTAINER] TESTS PASSED" || echo "[M10-CONTAINER] TESTS FAILED with exit code $code"; exit $code; }
trap cleanup EXIT INT TERM
echo "[TEST] Complete regression suite"; python -m pytest -q backend
echo "[TEST] Seed and baseline validation"; python graph/seed/seed.py --reset; python graph/validate.py
echo "[TEST] Production operational smoke"; python tests/integration/production_smoke.py
echo "[TEST] Evaluation fixture and formal harness"; python tests/integration/eval_fixture.py; python evals/run.py
echo "[TEST] Final graph integrity"; python graph/validate.py
