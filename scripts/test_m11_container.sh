#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace
cleanup(){ code=$?; set +e; echo "[RESTORE] Removing isolated test graph: $FALKORDB_GRAPH_NAME"; python graph/reset.py >/dev/null 2>&1 || true; [[ $code -eq 0 ]] && echo "[M11-CONTAINER] TESTS PASSED" || echo "[M11-CONTAINER] TESTS FAILED with exit code $code"; exit $code; }
trap cleanup EXIT INT TERM
echo "[TEST] Complete regression and real-data contracts"; python -m pytest -q backend
echo "[TEST] PostgreSQL importer contract"; python tests/integration/realdata_import_smoke.py
echo "[TEST] Seed and final graph regression"; python graph/seed/seed.py --reset; python graph/validate.py
