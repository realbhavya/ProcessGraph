import pytest

from app.graph.executor import GraphExecutor
from app.graph.errors import QueryTimeout


class Result:
    result_set = [[1], [2], [3]]


class FakeGraph:
    def __init__(self):
        self.calls = []

    def ro_query(self, query, params, timeout):
        self.calls.append(("read", query, params, timeout))
        return Result()

    def query(self, query, params, timeout):
        self.calls.append(("write", query, params, timeout))
        return Result()


def test_read_uses_ro_query_and_limit():
    graph = FakeGraph()
    execution = GraphExecutor(graph, timeout_ms=123, result_limit=2).read("q.read", "RETURN 1")
    assert execution.rows == [[1], [2]]
    assert graph.calls[0][0] == "read"
    assert graph.calls[0][3] == 123


def test_write_uses_query():
    graph = FakeGraph()
    GraphExecutor(graph).write("q.write", "CREATE ()")
    assert graph.calls[0][0] == "write"


def test_timeout_is_structured():
    class TimeoutGraph(FakeGraph):
        def ro_query(self, query, params, timeout):
            raise RuntimeError("query timeout")
    with pytest.raises(QueryTimeout):
        GraphExecutor(TimeoutGraph()).read("q.timeout", "RETURN 1")
