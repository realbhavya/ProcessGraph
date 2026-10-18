from __future__ import annotations

from app.tools.contracts import AgentRole, EquipmentInput, EquipmentTraversalInput, MemoryInput


class AgentToolClient:
    """Permission-aware client used by agents instead of direct repositories."""

    def __init__(self, service, role: AgentRole, request_id: str):
        self.service=service; self.role=role; self.request_id=request_id

    def _base(self): return {"tenant_id":"TENANT-DEMO","agent_role":self.role,"request_id":self.request_id}

    def utility_path(self, equipment_id: str):
        p=EquipmentTraversalInput(**self._base(),equipment_id=equipment_id,max_depth=4)
        return self.service.execute("trace_utility_path",p,lambda:self.service.equipment.trace_utility_path(equipment_id,4),["equipment.utility_path"])

    def safeguards(self, equipment_id: str):
        p=EquipmentInput(**self._base(),equipment_id=equipment_id)
        return self.service.execute("find_related_safeguards",p,lambda:self.service.context.safeguards(equipment_id),["context.safeguards"])

    def findings(self, equipment_id: str):
        p=EquipmentTraversalInput(**self._base(),equipment_id=equipment_id,max_depth=4)
        return self.service.execute("find_open_maintenance_findings",p,lambda:self.service.context.open_findings(equipment_id,4),["context.open_findings"])

    def incidents(self, equipment_id: str):
        p=EquipmentInput(**self._base(),equipment_id=equipment_id)
        return self.service.execute("find_related_incidents",p,lambda:self.service.context.related_incidents(equipment_id),["context.related_incidents"])

    def memories(self, entity_id: str):
        p=MemoryInput(**self._base(),entity_id=entity_id,limit=10)
        return self.service.execute("retrieve_active_memories",p,lambda:self.service.context.active_memories(entity_id,10),["context.active_memories"])
