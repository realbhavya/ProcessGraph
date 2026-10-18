from pathlib import Path


REPOSITORY = Path(__file__).parents[2] / "app" / "graph" / "repositories" / "memory_governance.py"


def test_retrieval_uses_falkordb_compatible_supersession_anti_join() -> None:
    text = REPOSITORY.read_text(encoding="utf-8")
    assert "AND NOT (memory)-[:SUPERSEDES]->(:Memory)" not in text
    assert "OPTIONAL MATCH (replacement:Memory {tenant_id:$tenant_id})-[:SUPERSEDES]->(memory)" in text
    assert "replacement_count = 0" in text


def test_retrieval_excludes_replaced_memory_not_replacement_memory() -> None:
    text = REPOSITORY.read_text(encoding="utf-8")
    assert "(replacement:Memory {tenant_id:$tenant_id})-[:SUPERSEDES]->(memory)" in text
    assert "(memory)-[:SUPERSEDES]->(replacement" not in text
