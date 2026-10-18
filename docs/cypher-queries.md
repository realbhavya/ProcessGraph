# Cypher Query Catalogue

Milestone 2 separates every graph operation into a named repository method. Reads use `Graph.ro_query`; writes use `Graph.query`. All runtime values are passed as parameters except bounded traversal depth, which is validated as an integer from 1 to 4 before controlled interpolation into Cypher syntax.

## Read operations

- `equipment.resolve`
- `equipment.context`
- `equipment.process_impact`
- `equipment.utility_path`
- `equipment.sensors`
- `context.safeguards`
- `context.open_findings`
- `context.owner`
- `context.related_incidents`
- `context.active_memories`

## Write operations

- `workflow.create_session`
- `workflow.create_incident`
- `workflow.create_task`
- `workflow.record_finding`
- `workflow.create_handoff`
- `workflow.propose_action`
- `workflow.record_outcome`
- `memory.create_candidate`
- `memory.supersede`

Every write uses a stable idempotency key where repeated external requests could otherwise duplicate graph state.
