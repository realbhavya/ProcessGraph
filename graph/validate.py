from __future__ import annotations

import json
import os
from typing import Any

from falkordb import FalkorDB

GRAPH_NAME = os.getenv("FALKORDB_GRAPH_NAME", "processgraph_tenant_demo")
TENANT_ID = "TENANT-DEMO"
SEED_SOURCE = "processgraph-sentinel-seed-v1"


def connect():
    kwargs: dict[str, Any] = {
        "host": os.getenv("FALKORDB_HOST", "localhost"),
        "port": int(os.getenv("FALKORDB_PORT", "6379")),
    }
    password = os.getenv("FALKORDB_PASSWORD", "local-falkordb-password")
    if password:
        kwargs["password"] = password
    return FalkorDB(**kwargs).select_graph(GRAPH_NAME)


def scalar(graph, query: str, params: dict | None = None):
    return graph.ro_query(query, params=params or {}).result_set[0][0]


def count_label(graph, label: str, *, source: str | None = None) -> int:
    if source is None:
        return scalar(graph, f"MATCH (n:{label} {{tenant_id:$tenant}}) RETURN count(n)", {"tenant": TENANT_ID})
    return scalar(
        graph,
        f"MATCH (n:{label} {{tenant_id:$tenant, source:$source}}) RETURN count(n)",
        {"tenant": TENANT_ID, "source": source},
    )


def main() -> None:
    graph = connect()
    report: dict[str, Any] = {
        "totals": {
            "nodes": scalar(graph, "MATCH (n) RETURN count(n)"),
            "relationships": scalar(graph, "MATCH ()-[r]->() RETURN count(r)"),
        },
        "seed_baseline": {},
        "runtime": {},
        "provenance": {},
        "critical_paths": {},
    }

    expected_seed_counts = {
        "Equipment": 24,
        "Sensor": 12,
        "Incident": 8,
        "Observation": 20,
        "ProcedureStep": 30,
        "ProcessStream": 14,
        "Memory": 3,
    }
    for label, expected in expected_seed_counts.items():
        actual = count_label(graph, label, source=SEED_SOURCE)
        report["seed_baseline"][label] = {"expected": expected, "actual": actual, "valid": actual == expected}

    report["runtime"]["incidents"] = count_label(graph, "Incident") - expected_seed_counts["Incident"]
    report["runtime"]["observations"] = count_label(graph, "Observation") - expected_seed_counts["Observation"]
    report["runtime"]["memories"] = count_label(graph, "Memory") - expected_seed_counts["Memory"]

    # Runtime integrity checks validate structure rather than prohibit legitimate growth.
    report["runtime"]["orphan_observations"] = scalar(
        graph,
        """
        MATCH (o:Observation {tenant_id:$tenant, source:'runtime'})
        OPTIONAL MATCH (incident:Incident {tenant_id:$tenant})-[:HAS_OBSERVATION]->(o)
        WITH o, count(incident) AS parent_count
        WHERE parent_count = 0
        RETURN count(o)
        """,
        {"tenant": TENANT_ID},
    )
    report["runtime"]["orphan_timeline_events"] = scalar(
        graph,
        """
        MATCH (e:TimelineEvent {tenant_id:$tenant, source:'runtime'})
        OPTIONAL MATCH (incident:Incident {tenant_id:$tenant})-[:HAS_EVENT]->(e)
        WITH e, count(incident) AS parent_count
        WHERE parent_count = 0
        RETURN count(e)
        """,
        {"tenant": TENANT_ID},
    )
    report["runtime"]["incidents_without_session"] = scalar(
        graph,
        """
        MATCH (i:Incident {tenant_id:$tenant, source:'runtime'})
        OPTIONAL MATCH (session:Session {tenant_id:$tenant})-[:CREATED]->(i)
        WITH i, count(session) AS session_count
        WHERE session_count = 0
        RETURN count(i)
        """,
        {"tenant": TENANT_ID},
    )
    report["runtime"]["incidents_without_equipment"] = scalar(
        graph,
        """
        MATCH (i:Incident {tenant_id:$tenant, source:'runtime'})
        OPTIONAL MATCH (i)-[:AFFECTS]->(equipment:Equipment {tenant_id:$tenant})
        WITH i, count(equipment) AS equipment_count
        WHERE equipment_count = 0
        RETURN count(i)
        """,
        {"tenant": TENANT_ID},
    )


    report["runtime"]["orphan_tasks"] = scalar(graph, """
        MATCH (t:Task {tenant_id:$tenant, source:'runtime'})
        OPTIONAL MATCH (i:Investigation {tenant_id:$tenant})-[:HAS_TASK]->(t)
        WITH t, count(i) AS parent_count WHERE parent_count=0 RETURN count(t)
    """, {"tenant": TENANT_ID})
    report["runtime"]["findings_without_evidence"] = scalar(graph, """
        MATCH (f:Finding {tenant_id:$tenant, source:'runtime'})
        OPTIONAL MATCH (f)-[:SUPPORTED_BY]->(e)
        WITH f, count(e) AS evidence_count WHERE evidence_count=0 RETURN count(f)
    """, {"tenant": TENANT_ID})
    report["runtime"]["orphan_handoffs"] = scalar(graph, """
        MATCH (h:Handoff {tenant_id:$tenant, source:'runtime'})
        OPTIONAL MATCH (i:Investigation {tenant_id:$tenant})-[:HAS_HANDOFF]->(h)
        WITH h, count(i) AS parent_count WHERE parent_count=0 RETURN count(h)
    """, {"tenant": TENANT_ID})


    report["runtime"]["memories_without_source"] = scalar(graph, """
        MATCH (m:Memory {tenant_id:$tenant, source:'runtime'})
        OPTIONAL MATCH (m)-[:DERIVED_FROM]->(source)
        WITH m, count(source) AS source_count WHERE source_count=0 RETURN count(m)
    """, {"tenant": TENANT_ID})
    report["runtime"]["memories_without_evidence"] = scalar(graph, """
        MATCH (m:Memory {tenant_id:$tenant, source:'runtime'})
        OPTIONAL MATCH (m)-[:SUPPORTED_BY]->(evidence)
        WITH m, count(evidence) AS evidence_count WHERE evidence_count=0 RETURN count(m)
    """, {"tenant": TENANT_ID})
    report["runtime"]["active_memories_without_review"] = scalar(graph, """
        MATCH (m:Memory {tenant_id:$tenant, source:'runtime', status:'active'})
        OPTIONAL MATCH (m)-[:HAS_REVIEW]->(review:MemoryReview {decision:'approve'})
        WITH m, count(review) AS review_count WHERE review_count=0 RETURN count(m)
    """, {"tenant": TENANT_ID})


    report["runtime"]["executed_actions_without_approval"] = scalar(graph, """
        MATCH (a:Action {tenant_id:$tenant,source:'runtime',status:'EXECUTED'})
        OPTIONAL MATCH (a)-[:HAS_REVIEW]->(r:ActionReview {decision:'approve'})
        WITH a,count(r) AS approvals WHERE approvals=0 RETURN count(a)
    """, {"tenant": TENANT_ID})
    report["runtime"]["executions_not_simulated"] = scalar(graph, """
        MATCH (e:ActionExecution {tenant_id:$tenant,source:'runtime'})
        WHERE e.mode <> 'simulation' RETURN count(e)
    """, {"tenant": TENANT_ID})

    report["provenance"]["nodes_missing_tenant"] = scalar(graph, "MATCH (n) WHERE n.tenant_id IS NULL RETURN count(n)")
    report["provenance"]["nodes_not_synthetic"] = scalar(graph, "MATCH (n) WHERE n.synthetic <> true RETURN count(n)")
    report["provenance"]["nodes_missing_source"] = scalar(graph, "MATCH (n) WHERE n.source IS NULL RETURN count(n)")
    report["provenance"]["relationships_missing_tenant"] = scalar(graph, "MATCH ()-[r]->() WHERE r.tenant_id IS NULL RETURN count(r)")
    report["provenance"]["relationships_not_synthetic"] = scalar(graph, "MATCH ()-[r]->() WHERE r.synthetic <> true RETURN count(r)")
    report["provenance"]["relationships_missing_source"] = scalar(graph, "MATCH ()-[r]->() WHERE r.source IS NULL RETURN count(r)")

    report["critical_paths"]["r101_to_p201"] = scalar(
        graph,
        """
        MATCH p=(r:Equipment {id:'EQ-R-101', tenant_id:$tenant})
          -[:COOLED_BY|SUPPLIED_BY|DEPENDS_ON*1..5]-
          (:Equipment {id:'EQ-P-201', tenant_id:$tenant})
        RETURN count(p)
        """,
        {"tenant": TENANT_ID},
    )
    report["critical_paths"]["p201_open_findings"] = scalar(
        graph,
        """
        MATCH (f:MaintenanceFinding {tenant_id:$tenant})-[:ABOUT]->
              (:Equipment {id:'EQ-P-201', tenant_id:$tenant})
        WHERE f.status IN ['open','monitoring']
        RETURN count(f)
        """,
        {"tenant": TENANT_ID},
    )
    report["critical_paths"]["p201_utilities_owner"] = scalar(
        graph,
        """
        MATCH (:Team {id:'TEAM-UTIL', tenant_id:$tenant})-[:OWNS]->
              (:Equipment {id:'EQ-P-201', tenant_id:$tenant})
        RETURN count(*)
        """,
        {"tenant": TENANT_ID},
    )

    assertions = {
        "seed_baseline_exact": all(item["valid"] for item in report["seed_baseline"].values()),
        "runtime_observations_linked": report["runtime"]["orphan_observations"] == 0,
        "runtime_timeline_events_linked": report["runtime"]["orphan_timeline_events"] == 0,
        "runtime_incidents_have_session": report["runtime"]["incidents_without_session"] == 0,
        "runtime_incidents_have_equipment": report["runtime"]["incidents_without_equipment"] == 0,
        "runtime_tasks_linked": report["runtime"]["orphan_tasks"] == 0,
        "runtime_findings_have_evidence": report["runtime"]["findings_without_evidence"] == 0,
        "runtime_handoffs_linked": report["runtime"]["orphan_handoffs"] == 0,
        "runtime_memories_have_source": report["runtime"]["memories_without_source"] == 0,
        "runtime_memories_have_evidence": report["runtime"]["memories_without_evidence"] == 0,
        "active_memories_have_approval": report["runtime"]["active_memories_without_review"] == 0,
        "executed_actions_have_approval": report["runtime"]["executed_actions_without_approval"] == 0,
        "executions_are_simulated": report["runtime"]["executions_not_simulated"] == 0,
        "node_provenance_complete": all(report["provenance"][key] == 0 for key in (
            "nodes_missing_tenant", "nodes_not_synthetic", "nodes_missing_source"
        )),
        "relationship_provenance_complete": all(report["provenance"][key] == 0 for key in (
            "relationships_missing_tenant", "relationships_not_synthetic", "relationships_missing_source"
        )),
        "critical_path_exists": report["critical_paths"]["r101_to_p201"] >= 1,
        "open_finding_exists": report["critical_paths"]["p201_open_findings"] >= 1,
        "ownership_exists": report["critical_paths"]["p201_utilities_owner"] == 1,
    }
    report["assertions"] = assertions
    report["valid"] = all(assertions.values())
    print(json.dumps(report, indent=2))
    if not report["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
