# Multi-Agent Investigation Workflow

The orchestrator creates graph-backed tasks for connectivity and safety specialists, executes them concurrently, records task states, creates an explicit connectivity-to-maintenance handoff, and then runs the maintenance/memory specialist from shared graph state. Every specialist uses the permission-aware tool client, not direct Cypher or repositories.

The evidence validator verifies entity existence, path structure, provenance type, and claim limits before findings become `validated`. Unsupported findings remain stored as rejected and auditable. Partial specialist failure produces a `PARTIAL` investigation rather than hiding successful evidence or claiming full completion.
