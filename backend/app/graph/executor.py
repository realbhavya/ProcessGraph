from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any
from uuid import uuid4

from app.graph.errors import DatabaseUnavailable, GraphError, QueryTimeout


@dataclass(frozen=True)
class QueryExecution:
    query_id: str
    request_id: str
    rows: list[list[Any]]
    latency_ms: float
    read_only: bool


class GraphExecutor:
    """Enforces explicit read/write paths, parameters, timeouts, and result limits."""

    def __init__(self, graph, timeout_ms: int = 5000, result_limit: int = 100):
        self.graph = graph
        self.timeout_ms = timeout_ms
        self.result_limit = result_limit

    def read(
        self,
        query_id: str,
        cypher: str,
        params: dict[str, Any] | None = None,
        *,
        result_limit: int | None = None,
    ) -> QueryExecution:
        return self._execute(True, query_id, cypher, params, result_limit)

    def write(
        self,
        query_id: str,
        cypher: str,
        params: dict[str, Any] | None = None,
        *,
        result_limit: int | None = None,
    ) -> QueryExecution:
        return self._execute(False, query_id, cypher, params, result_limit)

    def _execute(self, read_only, query_id, cypher, params, result_limit):
        if not query_id or not query_id.replace("_", "").replace("-", "").replace(".", "").isalnum():
            raise ValueError("query_id must be a stable alphanumeric identifier")
        limit = result_limit or self.result_limit
        if not 1 <= limit <= 500:
            raise ValueError("result_limit must be between 1 and 500")
        request_id = str(uuid4())
        started = perf_counter()
        try:
            method = self.graph.ro_query if read_only else self.graph.query
            result = method(cypher, params=params or {}, timeout=self.timeout_ms)
            rows = list(result.result_set[:limit])
            return QueryExecution(
                query_id=query_id,
                request_id=request_id,
                rows=rows,
                latency_ms=round((perf_counter() - started) * 1000, 3),
                read_only=read_only,
            )
        except GraphError:
            raise
        except Exception as exc:
            text = str(exc).lower()
            if "timeout" in text:
                raise QueryTimeout() from exc
            if any(token in text for token in ("connection", "noauth", "refused", "unreachable")):
                raise DatabaseUnavailable() from exc
            raise
