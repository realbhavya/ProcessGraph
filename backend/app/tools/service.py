from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Callable
from uuid import uuid4

from app.graph.errors import GraphError, InvalidInput
from app.tools.contracts import ToolContext, ToolError, ToolEvidence, ToolResult
from app.tools.permissions import authorize


class ToolService:
    def __init__(self, *, equipment, context, incidents, workflow, memory, audit, graph_name: str):
        self.equipment = equipment
        self.context = context
        self.incidents = incidents
        self.workflow = workflow
        self.memory = memory
        self.audit = audit
        self.graph_name = graph_name

    @staticmethod
    def _audit_id() -> str:
        """Create a distinct immutable event identity for every invocation.

        Request IDs correlate retries and related calls. They are not event IDs:
        two invocations may legitimately share a request ID, especially when a
        client retries an idempotent operation. Each attempt must remain visible
        in the audit trail, including authorization denials and failures.
        """
        return f"AUDIT-{uuid4().hex.upper()}"

    def execute(self, tool_name: str, payload: ToolContext, operation: Callable[[], Any], query_ids: list[str]) -> dict:
        error_code = None
        status = "success"
        try:
            authorize(tool_name, payload.agent_role)
            if payload.tenant_id != "TENANT-DEMO":
                raise InvalidInput("Only TENANT-DEMO is available")
            if tool_name in WRITE_TOOLS and not payload.idempotency_key:
                raise InvalidInput("Write tools require idempotency_key")
            data = operation()
            result = ToolResult(
                request_id=payload.request_id,
                tool_name=tool_name,
                status="success",
                data=data,
                evidence=ToolEvidence(query_ids=query_ids, graph_name=self.graph_name, executed_at=datetime.now(UTC).isoformat()),
            )
        except GraphError as exc:
            status = "error"
            error_code = exc.code
            result = ToolResult(
                request_id=payload.request_id,
                tool_name=tool_name,
                status="error",
                error=ToolError(code=exc.code, message=exc.message, retryable=exc.retryable),
            )
        except Exception as exc:
            status = "error"
            error_code = "INTERNAL_ERROR"
            result = ToolResult(
                request_id=payload.request_id,
                tool_name=tool_name,
                status="error",
                error=ToolError(code="INTERNAL_ERROR", message="Tool execution failed", retryable=False, details={"exception_type": exc.__class__.__name__}),
            )
        finally:
            self.audit.record_tool_call(
                event_id=self._audit_id(),
                tool_name=tool_name,
                agent_role=payload.agent_role.value,
                request_id=payload.request_id,
                status=status,
                idempotency_key=payload.idempotency_key,
                error_code=error_code,
            )
        return result.model_dump(mode="json")


WRITE_TOOLS = frozenset({
    "create_investigation_task", "record_finding", "create_handoff",
    "propose_action", "record_action_outcome", "propose_memory",
})
