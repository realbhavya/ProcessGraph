# ADR 0001: Project Foundation

## Status

Accepted for Milestone 0.

## Context

The product must demonstrate graph-native connected-data action and persistent multi-agent memory within a short build window.

## Decisions

- Use Python 3.12 and FastAPI for the backend.
- Use React with Vite for the frontend.
- Use FalkorDB as the primary graph database and context layer.
- Use the official Python client beginning in Milestone 1.
- Use a modular monolith instead of microservices.
- Expose narrow graph tools through an MCP-compatible boundary.
- Store workflow coordination and durable memory in FalkorDB.
- Use Docker Compose for local deployment.
- Use only synthetic data in the default dataset.

## Consequences

Positive:

- Reduced operational complexity.
- Faster end-to-end testing.
- Clear graph centrality.
- Easier local demonstration.

Trade-offs:

- Components are not independently scalable.
- Initial authentication is demonstration-grade.
- Advanced ingestion and streaming are deferred.
