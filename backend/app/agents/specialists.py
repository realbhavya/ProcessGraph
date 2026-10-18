from __future__ import annotations

from app.domain.investigations import EvidenceReference, SpecialistFinding
from app.tools.contracts import AgentRole


class ConnectivityAgent:
    agent_id="AGENT-CONN"; role=AgentRole.CONNECTIVITY
    def run(self, task_id, equipment_id, client):
        result=client.utility_path(equipment_id)
        if result["status"]!="success": raise RuntimeError(result["error"]["code"])
        target=next((x for x in result["data"] if x["id"]=="EQ-P-201"),None)
        if not target: raise RuntimeError("NO_UTILITY_PATH")
        evidence=EvidenceReference(entity_id=target["id"],entity_type="Equipment",source="current_graph",path_node_ids=target["node_ids"],path_relationships=target["relationships"])
        return SpecialistFinding(finding_id=f"FIND-{task_id.removeprefix('TASK-')}",task_id=task_id,agent_id=self.agent_id,category="connectivity",summary="R-101 is connected to cooling-water pump P-201 through E-101 and the cooling-water utility system.",confidence=.97,evidence=[evidence])


class SafetyContextAgent:
    agent_id="AGENT-SAFE"; role=AgentRole.SAFETY
    def run(self, task_id, equipment_id, client):
        result=client.safeguards(equipment_id)
        if result["status"]!="success": raise RuntimeError(result["error"]["code"])
        if not result["data"]: raise RuntimeError("NO_SAFEGUARDS")
        evidence=[EvidenceReference(entity_id=x["id"],entity_type="Safeguard",source="current_graph") for x in result["data"]]
        return SpecialistFinding(finding_id=f"FIND-{task_id.removeprefix('TASK-')}",task_id=task_id,agent_id=self.agent_id,category="safety",summary="R-101 has designed temperature, pressure, and relief safeguards represented in the graph; their current field availability is not asserted.",confidence=.90,evidence=evidence,limitations=["Graph design status is not proof of current operational availability"])


class MaintenanceMemoryAgent:
    agent_id="AGENT-MEM"; role=AgentRole.MAINTENANCE_MEMORY
    def run(self, task_id, equipment_id, client):
        findings=client.findings(equipment_id)
        incidents=client.incidents(equipment_id)
        memories=client.memories(equipment_id)
        if findings["status"]!="success": raise RuntimeError(findings["error"]["code"])
        current=next((x for x in findings["data"] if x["id"]=="MF-001"),None)
        if not current: raise RuntimeError("NO_RELEVANT_MAINTENANCE_FINDING")
        evidence=[EvidenceReference(entity_id=current["id"],entity_type="MaintenanceFinding",source="current_graph")]
        for historical in incidents.get("data") or []:
            evidence.append(EvidenceReference(entity_id=historical["id"],entity_type="Incident",source="historical_incident"))
        for memory in memories.get("data") or []:
            evidence.append(EvidenceReference(entity_id=memory["id"],entity_type="Memory",source="memory"))
        return SpecialistFinding(finding_id=f"FIND-{task_id.removeprefix('TASK-')}",task_id=task_id,agent_id=self.agent_id,category="maintenance",summary="P-201 has an open high-severity vibration finding on the connected cooling path; historical evidence is supporting context, not proof of the current cause.",confidence=.92,evidence=evidence,limitations=["Maintenance finding indicates relevance, not confirmed causality"])
