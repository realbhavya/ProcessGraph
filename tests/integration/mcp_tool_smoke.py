from __future__ import annotations

import os
import sys

sys.path.insert(0, "/workspace/mcp-server")
from sentinel_mcp.server import (
    create_handoff, create_investigation_task, find_open_maintenance_findings,
    find_responsible_team, resolve_equipment, trace_utility_path,
)
from app.tools.contracts import (
    AgentRole, CreateHandoffInput, CreateTaskInput, EquipmentInput,
    EquipmentTraversalInput, ResolveEquipmentInput,
)
from falkordb import FalkorDB


def main():
    base={"tenant_id":"TENANT-DEMO","request_id":"mcp-request-0001"}
    resolved=resolve_equipment(ResolveEquipmentInput(**base,agent_role=AgentRole.CONNECTIVITY,equipment_name="R-101"))
    assert resolved["status"]=="success" and resolved["data"]["id"]=="EQ-R-101"
    path=trace_utility_path(EquipmentTraversalInput(**base,agent_role=AgentRole.CONNECTIVITY,equipment_id="EQ-R-101",max_depth=4))
    assert any(item["id"]=="EQ-P-201" for item in path["data"])
    findings=find_open_maintenance_findings(EquipmentTraversalInput(**base,agent_role=AgentRole.MAINTENANCE_MEMORY,equipment_id="EQ-R-101",max_depth=4))
    assert any(item["id"]=="MF-001" for item in findings["data"])
    owner=find_responsible_team(EquipmentInput(**base,agent_role=AgentRole.ACTION,equipment_id="EQ-P-201"))
    assert owner["data"]["id"]=="TEAM-UTIL"

    # Use the seeded historical incident for task creation.
    task_input=CreateTaskInput(**base,agent_role=AgentRole.ORCHESTRATOR,idempotency_key="mcp-task-idem-001",incident_id="INC-HIST-001",task_id="TASK-MCP-001",agent_id="AGENT-CONN",task_type="connectivity")
    first=create_investigation_task(task_input)
    second=create_investigation_task(task_input)
    assert first["data"]["id"]==second["data"]["id"]=="TASK-MCP-001"

    denied=create_investigation_task(CreateTaskInput(**base,agent_role=AgentRole.CONNECTIVITY,idempotency_key="mcp-denied-001",incident_id="INC-HIST-001",task_id="TASK-MCP-002",agent_id="AGENT-CONN",task_type="connectivity"))
    assert denied["status"]=="error" and denied["error"]["code"]=="UNAUTHORIZED_TOOL"

    handoff=create_handoff(CreateHandoffInput(**base,agent_role=AgentRole.CONNECTIVITY,idempotency_key="mcp-handoff-001",task_id="TASK-MCP-001",handoff_id="HANDOFF-MCP-001",from_agent_id="AGENT-CONN",to_agent_id="AGENT-MEM",reason="Review connected maintenance findings"))
    assert handoff["status"]=="success"

    graph=FalkorDB(host=os.getenv("FALKORDB_HOST","falkordb"),port=6379,password=os.getenv("FALKORDB_PASSWORD")).select_graph(os.environ["FALKORDB_GRAPH_NAME"])
    audit_count=graph.ro_query("MATCH (a:AuditEvent {tenant_id:'TENANT-DEMO'}) RETURN count(a)").result_set[0][0]
    assert audit_count == 8, f"Expected one audit event per invocation, found {audit_count}"
    task_audits=graph.ro_query("MATCH (a:AuditEvent {tenant_id:'TENANT-DEMO', tool_name:'create_investigation_task'}) RETURN a.status, a.error_code ORDER BY a.created_at").result_set
    assert len(task_audits) == 3, task_audits
    assert sum(1 for status, _ in task_audits if status == 'success') == 2
    assert sum(1 for status, code in task_audits if status == 'error' and code == 'UNAUTHORIZED_TOOL') == 1
    print("[M4] MCP tool smoke test passed")


if __name__=="__main__": main()
