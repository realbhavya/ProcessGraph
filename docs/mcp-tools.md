# MCP Tool Catalogue

The server uses the official MCP Python SDK `FastMCP` interface. Tools are narrow domain capabilities, not arbitrary query execution.

## Read tools

- `resolve_equipment`
- `trace_process_impact`
- `trace_utility_path`
- `find_connected_sensors`
- `find_related_safeguards`
- `find_open_maintenance_findings`
- `find_responsible_team`
- `find_related_incidents`
- `retrieve_active_memories`
- `get_investigation_state`
- `get_evidence_paths`

## Write tools

- `create_investigation_task`
- `record_finding`
- `create_handoff`
- `propose_action`
- `record_action_outcome`
- `propose_memory`

Every tool validates a strict Pydantic input contract, authorizes an agent role, executes through repositories, returns a standard envelope, and writes an `AuditEvent`. Write tools require an idempotency key. No generic Cypher tool is exposed.

## Audit event identity

`request_id` is a correlation identifier and may be reused by an idempotent retry. It is therefore stored as audit metadata but is not used as the audit node identity. Every invocation receives a distinct UUID-based `AuditEvent.id`, preserving successful retries, authorization denials, domain errors, and unexpected failures as separate immutable attempts.
