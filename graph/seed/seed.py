from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from falkordb import FalkorDB

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataset import NODES, RELATIONSHIPS, SOURCE, TENANT_ID  # noqa: E402

GRAPH_NAME = os.getenv("FALKORDB_GRAPH_NAME", "processgraph_tenant_demo")


def connect():
    kwargs: dict[str, Any] = {
        "host": os.getenv("FALKORDB_HOST", "localhost"),
        "port": int(os.getenv("FALKORDB_PORT", "6379")),
    }
    password = os.getenv("FALKORDB_PASSWORD", "local-falkordb-password")
    if password:
        kwargs["password"] = password
    return FalkorDB(**kwargs).select_graph(GRAPH_NAME)


def create_indexes(graph) -> None:
    labels = sorted(NODES)
    for label in labels:
        try:
            graph.query(f"CREATE INDEX FOR (n:{label}) ON (n.id)")
        except Exception as exc:
            text = str(exc).lower()
            if "already indexed" not in text and "already exists" not in text:
                raise


def seed(reset: bool = False) -> None:
    graph = connect()
    if reset:
        try:
            graph.delete()
        except Exception as exc:
            # FalkorDB returns different messages across versions when deleting a
            # graph that has not been created yet. Both cases mean there is
            # nothing to reset and are safe to ignore.
            message = str(exc).lower()
            missing_graph_messages = (
                "does not exist",
                "invalid graph operation on empty key",
                "empty key",
            )
            if not any(token in message for token in missing_graph_messages):
                raise

    for label, rows in NODES.items():
        query = f"""
        UNWIND $rows AS row
        MERGE (n:{label} {{tenant_id: $tenant_id, id: row.id}})
        SET n += row,
            n.synthetic = true,
            n.source = $source,
            n.tenant_id = $tenant_id
        """
        graph.query(query, params={"rows": rows, "tenant_id": TENANT_ID, "source": SOURCE})

    for start_label, start_id, rel_type, end_label, end_id, props in RELATIONSHIPS:
        query = f"""
        MATCH (a:{start_label} {{tenant_id: $tenant_id, id: $start_id}})
        MATCH (b:{end_label} {{tenant_id: $tenant_id, id: $end_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $props,
            r.synthetic = true,
            r.source = $source,
            r.tenant_id = $tenant_id
        """
        graph.query(query, params={
            "tenant_id": TENANT_ID,
            "start_id": start_id,
            "end_id": end_id,
            "props": props,
            "source": SOURCE,
        })

    create_indexes(graph)
    print(f"Seeded graph {GRAPH_NAME}: {sum(map(len, NODES.values()))} nodes, {len(RELATIONSHIPS)} relationships")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Delete the graph before seeding")
    args = parser.parse_args()
    seed(reset=args.reset)
