from app.graph.repositories.base import BaseRepository


class AuditRepository(BaseRepository):
    def record_tool_call(self, *, event_id: str, tool_name: str, agent_role: str, request_id: str, status: str, idempotency_key: str | None, error_code: str | None = None) -> None:
        self.executor.write(
            "audit.record_tool_call",
            """
            MERGE (event:AuditEvent {tenant_id:$tenant_id, id:$event_id})
            ON CREATE SET event.event_type='MCP_TOOL_CALL', event.tool_name=$tool_name,
                          event.agent_role=$agent_role, event.request_id=$request_id,
                          event.status=$status, event.idempotency_key=$idempotency_key,
                          event.error_code=$error_code, event.synthetic=true,
                          event.source='runtime', event.created_at=timestamp()
            """,
            self.params(event_id=event_id, tool_name=tool_name, agent_role=agent_role, request_id=request_id, status=status, idempotency_key=idempotency_key, error_code=error_code),
            result_limit=1,
        )
