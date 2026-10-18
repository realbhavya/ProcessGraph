from pathlib import Path


VALIDATOR = Path(__file__).parents[3] / "graph" / "validate.py"


def test_validator_uses_supported_optional_match_anti_join() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    assert "NOT EXISTS { MATCH" not in text
    assert text.count("OPTIONAL MATCH") >= 4
    assert "parent_count = 0" in text
    assert "session_count = 0" in text
    assert "equipment_count = 0" in text


def test_anti_join_queries_preserve_tenant_scope() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    assert "incident:Incident {tenant_id:$tenant}" in text
    assert "session:Session {tenant_id:$tenant}" in text
    assert "equipment:Equipment {tenant_id:$tenant}" in text
