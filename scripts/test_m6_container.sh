#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace
cleanup(){ code=$?; set +e; echo "[RESTORE] Removing isolated test graph: $FALKORDB_GRAPH_NAME"; python graph/reset.py >/dev/null 2>&1 || true; [[ $code -eq 0 ]] && echo "[M6-CONTAINER] TESTS PASSED" || echo "[M6-CONTAINER] TESTS FAILED with exit code $code"; exit $code; }
trap cleanup EXIT INT TERM
echo "[TEST] Unit and governance tests"; python -m pytest -q backend
echo "[TEST] Seed isolated graph"; python graph/seed/seed.py --reset; python graph/validate.py
echo "[TEST] Governed memory lifecycle"; python tests/integration/memory_lifecycle_smoke.py
echo "[TEST] Graph integrity after memory lifecycle"; python graph/validate.py
