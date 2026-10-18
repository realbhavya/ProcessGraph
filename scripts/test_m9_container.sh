#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace
cleanup(){ code=$?; set +e; echo "[RESTORE] Removing isolated test graph: $FALKORDB_GRAPH_NAME"; python graph/reset.py >/dev/null 2>&1 || true; [[ $code -eq 0 ]] && echo "[M9-CONTAINER] TESTS PASSED" || echo "[M9-CONTAINER] TESTS FAILED with exit code $code"; exit $code; }
trap cleanup EXIT INT TERM
echo "[TEST] Regression and evaluation-contract tests"; python -m pytest -q backend
echo "[TEST] Seed isolated graph"; python graph/seed/seed.py --reset; python graph/validate.py
echo "[TEST] Create evaluation fixture through public APIs"; python tests/integration/eval_fixture.py
echo "[TEST] Deterministic evaluation harness"; python evals/run.py
echo "[TEST] Final graph integrity"; python graph/validate.py
