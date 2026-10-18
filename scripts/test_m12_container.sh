#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace
# Exact migration for users who overlaid M12 onto an older extraction. These
# files are obsolete and conflict with the importlib-based test policy.
rm -f backend/tests/opcua/test_contracts.py backend/tests/test_test_module_names.py
find backend/tests -type d \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +
cleanup(){ code=$?; set +e; echo "[RESTORE] Removing isolated test graph: $FALKORDB_GRAPH_NAME"; python graph/reset.py >/dev/null 2>&1 || true; [[ $code -eq 0 ]] && echo "[M12-CONTAINER] TESTS PASSED" || echo "[M12-CONTAINER] TESTS FAILED with exit code $code"; exit $code; }
trap cleanup EXIT INT TERM
echo "[CHECK] Pytest import isolation: importlib"; python -m pytest -q backend/tests/test_pytest_import_isolation.py
echo "[TEST] Full regression and OPC UA contracts"; python -m pytest -q backend
echo "[TEST] Load bounded telemetry fixture"; python tests/integration/realdata_import_smoke.py
echo "[TEST] OPC UA read-only replay"; python tests/integration/opcua_replay_smoke.py
echo "[TEST] Graph regression"; python graph/seed/seed.py --reset; python graph/validate.py
