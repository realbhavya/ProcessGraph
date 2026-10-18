#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace
cleanup(){ code=$?; set +e; echo "[RESTORE] Removing isolated test graph: $FALKORDB_GRAPH_NAME"; python graph/reset.py >/dev/null 2>&1 || true; [[ $code -eq 0 ]] && echo "[M4-CONTAINER] TESTS PASSED" || echo "[M4-CONTAINER] TESTS FAILED with exit code $code"; exit $code; }
trap cleanup EXIT INT TERM

echo "[TEST] Unit and contract tests"
python -m pytest -q backend

echo "[TEST] No arbitrary Cypher MCP tool"
if grep -R "def execute_cypher\|@mcp.tool.*execute_cypher" mcp-server backend/app/tools; then
  echo "[ERROR] generic execute_cypher tool detected"; exit 1
fi

echo "[TEST] Seed isolated graph"
python graph/seed/seed.py --reset
python graph/validate.py

echo "[TEST] Real graph-backed MCP tools"
python tests/integration/mcp_tool_smoke.py

echo "[TEST] Graph integrity after MCP calls"
python graph/validate.py
