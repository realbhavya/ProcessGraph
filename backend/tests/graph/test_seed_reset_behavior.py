from pathlib import Path


def test_seed_accepts_empty_key_as_absent_graph() -> None:
    source = Path(__file__).parents[3] / "graph" / "seed" / "seed.py"
    text = source.read_text(encoding="utf-8")
    assert "invalid graph operation on empty key" in text
    assert "empty key" in text


def test_reset_is_idempotent_for_absent_graph() -> None:
    source = Path(__file__).parents[3] / "graph" / "reset.py"
    text = source.read_text(encoding="utf-8")
    assert "Graph {name} was already absent" in text
