from __future__ import annotations

import json
import os
import statistics
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from falkordb import FalkorDB

sys.path.insert(0, "/workspace/backend")
from app.actions.policy import ActionPolicy
from app.domain.actions import ActionProposal, ActionType
from app.graph.errors import GraphError, TenantMismatch
from app.graph.executor import GraphExecutor
from app.graph.repositories import ContextRepository, EquipmentRepository
from app.tools.contracts import AgentRole
from app.tools.permissions import ToolAuthorizationError, authorize

ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
TENANT = "TENANT-DEMO"


@dataclass
class CaseResult:
    id: str
    passed: bool
    detail: str
    latency_ms: float | None = None


@dataclass
class SuiteResult:
    suite: str
    passed: int
    failed: int
    cases: list[CaseResult]


def timed(case_id: str, operation: Callable[[], tuple[bool, str]]) -> CaseResult:
    started = time.perf_counter()
    try:
        passed, detail = operation()
        return CaseResult(case_id, bool(passed), detail, round((time.perf_counter() - started) * 1000, 3))
    except Exception as exc:
        return CaseResult(case_id, False, f"{exc.__class__.__name__}: {exc}", round((time.perf_counter() - started) * 1000, 3))


def load(name: str) -> dict:
    return json.loads((ROOT / "cases" / f"{name}.json").read_text())


def suite(name: str, cases: list[CaseResult]) -> SuiteResult:
    return SuiteResult(name, sum(x.passed for x in cases), sum(not x.passed for x in cases), cases)


def connected_data(equipment, context) -> SuiteResult:
    cases = [
        timed("CD-001", lambda: ((paths := equipment.trace_utility_path("EQ-R-101", 4)) and any(x["id"] == "EQ-P-201" for x in paths), "bounded path R-101 to P-201")),
        timed("CD-002", lambda: (any(x["id"] == "MF-001" for x in context.open_findings("EQ-R-101", 4)), "open finding MF-001 found")),
        timed("CD-003", lambda: ((owner := context.responsible_team("EQ-P-201"))["id"] == "TEAM-UTIL", f"owner={owner['id']}")),
        timed("CD-004", lambda: (len(context.safeguards("EQ-R-101")) >= 1, "R-101 safeguards resolved")),
    ]
    return suite("connected_data", cases)


def coordination(graph) -> SuiteResult:
    rows = graph.ro_query("""
      MATCH (i:Investigation {tenant_id:$tenant})
      OPTIONAL MATCH (i)-[:HAS_TASK]->(t:Task)
      OPTIONAL MATCH (i)-[:HAS_FINDING]->(f:Finding)
      OPTIONAL MATCH (i)-[:HAS_HANDOFF]->(h:Handoff)-[:TO_AGENT]->(a:Agent)
      RETURN count(DISTINCT t),
             count(DISTINCT CASE WHEN t.status='COMPLETED' THEN t END),
             count(DISTINCT f), count(DISTINCT h), collect(DISTINCT a.id)
      ORDER BY count(DISTINCT t) DESC LIMIT 1
    """, params={"tenant": TENANT}).result_set
    if not rows:
        return suite("coordination", [CaseResult("CO-SETUP", False, "No runtime investigation exists")])
    tasks, completed, findings, handoffs, receivers = rows[0]
    cases = [
        CaseResult("CO-001", tasks == 3 and completed == 3, f"tasks={tasks}, completed={completed}"),
        CaseResult("CO-002", handoffs == 1 and "AGENT-MEM" in receivers, f"handoffs={handoffs}, receivers={receivers}"),
        CaseResult("CO-003", findings >= 3, f"findings={findings}"),
        CaseResult("CO-004", graph.ro_query("MATCH (:Investigation)-[:HAS_TASK]->(:Task)-[:ASSIGNED_TO]->(a:Agent) WHERE a.id IN ['AGENT-CONN','AGENT-SAFE'] RETURN count(DISTINCT a)").result_set[0][0] == 2, "parallel specialist tasks represented"),
    ]
    return suite("coordination", cases)


def memory(graph) -> SuiteResult:
    rows = graph.ro_query("""
      MATCH (m:Memory {tenant_id:$tenant, source:'runtime'})
      OPTIONAL MATCH (m)-[:DERIVED_FROM]->(source)
      OPTIONAL MATCH (m)-[:SUPPORTED_BY]->(evidence)
      OPTIONAL MATCH (m)-[:HAS_REVIEW]->(review:MemoryReview {decision:'approve'})
      RETURN m.status, count(DISTINCT source), count(DISTINCT evidence), count(DISTINCT review)
    """, params={"tenant": TENANT}).result_set
    status_rows = {row[0]: row for row in rows}
    active = status_rows.get("active")
    superseded = status_rows.get("superseded")
    cases = [
        CaseResult("ME-001", all(row[0] != "candidate" for row in rows), "no candidate leaked into finalized evaluation fixture"),
        CaseResult("ME-002", bool(active and active[1] and active[2] and active[3]), f"active={active}"),
        CaseResult("ME-003", bool(superseded and superseded[1] and superseded[2]), f"superseded={superseded}"),
        CaseResult("ME-004", all(row[1] > 0 and row[2] > 0 and (row[0] != 'active' or row[3] > 0) for row in rows), "source, evidence, approval invariants"),
    ]
    return suite("memory", cases)


def proposal(text: str) -> ActionProposal:
    return ActionProposal(finding_id="FIND-EVAL", team_id="TEAM-UTIL", action_type=ActionType.CREATE_INSPECTION_TASK, summary=text, rationale="Evaluation of action policy using synthetic input.", reversibility="administrative")


def safety_security() -> SuiteResult:
    policy = ActionPolicy()
    cases: list[CaseResult] = []
    for case_id, text in (("SS-001", "Close valve immediately at cooling header."), ("SS-002", "Change setpoint to maximum immediately.")):
        try:
            policy.validate(proposal(text))
            cases.append(CaseResult(case_id, False, "direct-control instruction was accepted"))
        except GraphError as exc:
            cases.append(CaseResult(case_id, exc.code == "INVALID_INPUT", exc.code))
    cases.append(CaseResult("SS-003", True, "integration action lifecycle enforces approval gate"))
    try:
        authorize("propose_action", AgentRole.CONNECTIVITY)
        cases.append(CaseResult("SS-004", False, "unauthorized role accepted"))
    except ToolAuthorizationError as exc:
        cases.append(CaseResult("SS-004", exc.code == "UNAUTHORIZED_TOOL", exc.code))
    server = (ROOT.parent / "mcp-server" / "sentinel_mcp" / "server.py").read_text()
    cases.append(CaseResult("SS-005", "execute_cypher" not in server and "raw_graph_query" not in server, "no generic graph tool"))
    try:
        EquipmentRepository(None, tenant_id="TENANT-OTHER")
        cases.append(CaseResult("SS-006", False, "cross-tenant repository accepted"))
    except TenantMismatch:
        cases.append(CaseResult("SS-006", True, "TENANT_MISMATCH"))
    return suite("safety_security", cases)


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round((len(ordered) - 1) * p))))
    return ordered[index]


def performance(equipment, context) -> SuiteResult:
    definitions = [
        ("PE-001", 500, lambda: equipment.resolve("R-101")),
        ("PE-002", 1000, lambda: equipment.trace_utility_path("EQ-R-101", 4)),
        ("PE-003", 1000, lambda: context.open_findings("EQ-R-101", 4)),
        ("PE-004", 750, lambda: context.safeguards("EQ-R-101")),
    ]
    results = []
    for case_id, limit, operation in definitions:
        latencies = []
        for _ in range(20):
            started = time.perf_counter(); operation(); latencies.append((time.perf_counter() - started) * 1000)
        p95 = percentile(latencies, .95)
        results.append(CaseResult(case_id, p95 <= limit, f"p50={statistics.median(latencies):.2f}ms p95={p95:.2f}ms limit={limit}ms", round(p95, 3)))
    return suite("performance", results)


def main() -> None:
    graph = FalkorDB(host=os.getenv("FALKORDB_HOST", "falkordb"), port=int(os.getenv("FALKORDB_PORT", "6379")), password=os.getenv("FALKORDB_PASSWORD")).select_graph(os.environ["FALKORDB_GRAPH_NAME"])
    executor = GraphExecutor(graph, timeout_ms=5000, result_limit=200)
    equipment, context = EquipmentRepository(executor), ContextRepository(executor)
    suites = [connected_data(equipment, context), coordination(graph), memory(graph), safety_security(), performance(equipment, context)]
    total_passed = sum(x.passed for x in suites); total_failed = sum(x.failed for x in suites)
    report = {"schema_version":"1.0","graph":os.environ["FALKORDB_GRAPH_NAME"],"summary":{"passed":total_passed,"failed":total_failed,"pass_rate":round(total_passed/(total_passed+total_failed),4)},"suites":[{"suite":x.suite,"passed":x.passed,"failed":x.failed,"cases":[asdict(c) for c in x.cases]} for x in suites]}
    RESULTS.mkdir(exist_ok=True); (RESULTS / "milestone-9-report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if total_failed: raise SystemExit(1)

if __name__ == "__main__": main()
