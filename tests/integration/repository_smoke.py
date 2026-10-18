from __future__ import annotations

import os

from falkordb import FalkorDB

from app.graph.executor import GraphExecutor
from app.graph.repositories import ContextRepository, EquipmentRepository, MemoryRepository, WorkflowRepository


def main():
    graph_name = os.environ["FALKORDB_GRAPH_NAME"]
    db = FalkorDB(
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", "6379")),
        password=os.getenv("FALKORDB_PASSWORD", "local-falkordb-password"),
    )
    graph = db.select_graph(graph_name)
    executor = GraphExecutor(graph, timeout_ms=5000, result_limit=100)
    equipment = EquipmentRepository(executor)
    context = ContextRepository(executor)
    workflow = WorkflowRepository(executor)
    memory = MemoryRepository(executor)

    resolved = equipment.resolve("R-101")
    assert resolved["id"] == "EQ-R-101"
    utility = equipment.trace_utility_path("EQ-R-101", 4)
    assert any(row["id"] == "EQ-P-201" for row in utility)
    findings = context.open_findings("EQ-R-101", 4)
    assert any(row["id"] == "MF-001" for row in findings)
    assert context.responsible_team("EQ-P-201")["id"] == "TEAM-UTIL"
    assert context.related_incidents("EQ-R-101")
    assert context.active_memories("EQ-R-101")

    s1 = workflow.create_session("SESSION-TEST-1", "idem-session")
    s2 = workflow.create_session("SESSION-TEST-2", "idem-session")
    assert s1["id"] == s2["id"] == "SESSION-TEST-1"
    incident = workflow.create_incident(s1["id"], "INC-TEST-1", "Synthetic repository test", "EQ-R-101", "idem-incident")
    assert incident["id"] == "INC-TEST-1"
    task = workflow.create_task(incident["id"], "TASK-TEST-1", "AGENT-CONN", "connectivity", "idem-task")
    finding = workflow.record_finding(task["id"], "FIND-TEST-1", "P-201 lies on cooling path", 0.95, "EQ-P-201", "idem-finding")
    handoff = workflow.create_handoff(task["id"], "HANDOFF-TEST-1", "AGENT-CONN", "AGENT-MEM", "Review open findings", "idem-handoff")
    action = workflow.propose_action(finding["id"], "ACTION-TEST-1", "TEAM-UTIL", "CREATE_INSPECTION_TASK", "Inspect synthetic P-201", "idem-action")
    outcome = workflow.record_outcome(action["id"], "OUT-TEST-1", "Synthetic test completed", "helpful", "idem-outcome")
    candidate = memory.create_candidate(outcome["id"], "MEM-TEST-1", "episodic", "Synthetic repository integration memory", 0.9, "EQ-R-101", "idem-memory")
    assert handoff["status"] == "created"
    assert candidate["status"] == "candidate"

    counts = graph.ro_query("MATCH (n {tenant_id:'TENANT-DEMO'}) RETURN count(n)").result_set[0][0]
    assert counts > 187
    print("[M2] repository integration smoke test passed")


if __name__ == "__main__":
    main()
