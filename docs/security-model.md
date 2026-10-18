# Security Model

The application is synthetic-only and single-tenant by design. Repository construction rejects unsupported tenants. MCP tools are role-scoped and expose no generic Cypher. All writes require bounded schemas and idempotency. Agent actions are allow-listed, direct-control language is blocked, human approval is required, and execution is simulation-only. Secrets are environment-provided and must not be committed. Logs expose request correlation but not exception details to clients.
