# Product Requirements

## Product

ProcessGraph Sentinel is a graph-native multi-agent incident-triage and persistent-memory system for a synthetic chemical-process plant.

## Tracks

1. Agents That Act on Connected Data
2. Agent Memory and Coordination

## Primary user outcome

A user reports an abnormal condition. The system resolves the mentioned equipment, follows connected process and utility relationships, retrieves relevant ownership, safeguards, maintenance findings, incidents, and approved memories, coordinates specialist agents, and proposes a controlled action with an inspectable evidence path.

## MVP capabilities

1. Synthetic plant knowledge graph in FalkorDB.
2. Multi-hop process and utility traversal.
3. Parameterized graph tools exposed through MCP.
4. Orchestrator plus scoped specialist agents.
5. Persistent graph state for tasks, findings, and handoffs.
6. Episodic, semantic, and procedural memory.
7. Controlled actions with human approval.
8. Evidence-path explanation.
9. Cross-session memory reuse.
10. Repeatable local deployment, tests, and demo.

## Required demonstration

1. Submit a synthetic R-101 high-temperature and low-cooling-flow incident.
2. Traverse R-101 to its exchanger, cooling-water system, and P-201.
3. Retrieve an unresolved maintenance finding and responsible team.
4. Show an agent handoff stored in the graph.
5. Propose and approve a synthetic inspection task.
6. Record a synthetic outcome.
7. Promote reviewed memory.
8. Start a separate E-102 session and reuse the approved procedural memory.
9. Display every material evidence path.

## Non-functional requirements

- Evidence-first and fail-closed behavior.
- Parameterized graph operations only.
- Idempotent writes.
- Tenant-aware graph selection.
- Structured errors and audit events.
- Human approval for safety-sensitive actions.
- Clear synthetic-data and safety declarations.

## Explicitly deferred

- Real plant data or control-system integration.
- Automatic set-point or equipment changes.
- Kafka, microservices, GNNs, and enterprise SSO.
- Unrestricted text-to-Cypher.
- Full GraphRAG document ingestion.
- Production certification or real-world safety use.

## Definition of MVP success

The MVP succeeds only if removing FalkorDB eliminates multi-hop investigation, graph-derived assignment, agent shared state, persistent memory, and evidence-path explanation.
