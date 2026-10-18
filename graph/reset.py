import os
from typing import Any

from falkordb import FalkorDB

kwargs: dict[str, Any] = {
    "host": os.getenv("FALKORDB_HOST", "localhost"),
    "port": int(os.getenv("FALKORDB_PORT", "6379")),
}
password = os.getenv("FALKORDB_PASSWORD", "local-falkordb-password")
if password:
    kwargs["password"] = password
name = os.getenv("FALKORDB_GRAPH_NAME", "processgraph_tenant_demo")
graph = FalkorDB(**kwargs).select_graph(name)
try:
    graph.delete()
    print(f"Deleted graph {name}")
except Exception as exc:
    message = str(exc).lower()
    missing_graph_messages = (
        "does not exist",
        "invalid graph operation on empty key",
        "empty key",
    )
    if any(token in message for token in missing_graph_messages):
        print(f"Graph {name} was already absent")
    else:
        raise
