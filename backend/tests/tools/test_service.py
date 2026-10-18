from app.graph.errors import EntityNotFound
from app.tools.contracts import AgentRole, ResolveEquipmentInput
from app.tools.service import ToolService


class Audit:
    def __init__(self): self.events=[]
    def record_tool_call(self, **kwargs): self.events.append(kwargs)


class Equipment:
    def resolve(self, name):
        if name == "UNKNOWN": raise EntityNotFound(name)
        return {"id":"EQ-R-101","name":name}


class Empty: pass


def make_service():
    audit=Audit()
    service=ToolService(equipment=Equipment(), context=Empty(), incidents=Empty(), workflow=Empty(), memory=Empty(), audit=audit, graph_name="isolated")
    return service,audit


def test_success_envelope_and_audit():
    service,audit=make_service()
    payload=ResolveEquipmentInput(tenant_id="TENANT-DEMO",agent_role=AgentRole.CONNECTIVITY,request_id="request-123",equipment_name="R-101")
    result=service.execute("resolve_equipment",payload,lambda:service.equipment.resolve(payload.equipment_name),["equipment.resolve"])
    assert result["status"]=="success" and result["evidence"]["graph_name"]=="isolated"
    assert audit.events[0]["status"]=="success"


def test_error_envelope_does_not_leak_exception_and_is_audited():
    service,audit=make_service()
    payload=ResolveEquipmentInput(tenant_id="TENANT-DEMO",agent_role=AgentRole.CONNECTIVITY,request_id="request-456",equipment_name="UNKNOWN")
    result=service.execute("resolve_equipment",payload,lambda:service.equipment.resolve(payload.equipment_name),["equipment.resolve"])
    assert result["error"]["code"]=="ENTITY_NOT_FOUND"
    assert audit.events[0]["error_code"]=="ENTITY_NOT_FOUND"


def test_repeated_invocations_create_distinct_audit_events():
    service, audit = make_service()
    payload = ResolveEquipmentInput(
        tenant_id="TENANT-DEMO",
        agent_role=AgentRole.CONNECTIVITY,
        request_id="retry-request-123",
        equipment_name="R-101",
    )
    service.execute("resolve_equipment", payload, lambda: service.equipment.resolve("R-101"), ["equipment.resolve"])
    service.execute("resolve_equipment", payload, lambda: service.equipment.resolve("R-101"), ["equipment.resolve"])
    assert len(audit.events) == 2
    assert audit.events[0]["event_id"] != audit.events[1]["event_id"]


def test_authorization_denial_has_its_own_audit_event():
    service, audit = make_service()
    payload = ResolveEquipmentInput(
        tenant_id="TENANT-DEMO",
        agent_role=AgentRole.ACTION,
        request_id="denied-request-123",
        equipment_name="R-101",
    )
    result = service.execute("resolve_equipment", payload, lambda: service.equipment.resolve("R-101"), ["equipment.resolve"])
    assert result["status"] == "error"
    assert result["error"]["code"] == "UNAUTHORIZED_TOOL"
    assert audit.events[0]["status"] == "error"
    assert audit.events[0]["error_code"] == "UNAUTHORIZED_TOOL"
