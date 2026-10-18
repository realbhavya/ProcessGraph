# Architecture Overview

## Decision

Use a modular monolith with a React frontend, FastAPI backend, separate MCP tool module, and FalkorDB as the primary context, coordination, memory, and evidence store.

## Runtime components

```text
Frontend
  → FastAPI API
      → Workflow orchestrator
          → Specialist agent modules
              → MCP tool interface
                  → Graph repositories
                      → FalkorDB
```

## Why this architecture

- Fast enough to build and debug during the hackathon.
- Clear module boundaries without distributed-system overhead.
- Deterministic, testable graph operations.
- Easy local deployment through Docker Compose.
- Agent permissions can be enforced through tool allow-lists.
- The graph remains central to reasoning and state.

## Components

### Frontend

Will host incident input, agent timeline, evidence paths, approvals, outcomes, and memory review.

### API

Owns authentication boundary, tenant context, validation, request IDs, idempotency, and public contracts.

### Workflow orchestrator

Owns state transitions, parallel specialist execution, deterministic merge, checkpoints, retries, and partial-failure reporting.

### MCP tool server

Exposes narrow, typed capabilities. A generic arbitrary-Cypher tool is prohibited.

### FalkorDB

Stores the synthetic plant domain, incidents, observations, tasks, findings, handoffs, actions, outcomes, provenance, and persistent memories.

## Architecture characteristics

- Graph-native
- Evidence-first
- Fail-closed
- Auditable
- Idempotent
- Tenant-aware
- Human-controlled
- Recoverable

## Milestone 0 boundary

The backend and frontend shells are runnable. FalkorDB is provisioned, but graph connectivity, schema, seed data, and graph-aware readiness are intentionally completed in Milestone 1.
