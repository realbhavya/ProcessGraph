from pathlib import Path


SMOKE = Path(__file__).parents[3] / "tests" / "integration" / "action_governance_smoke.py"


def test_action_test_uses_real_investigation_workflow() -> None:
    text = SMOKE.read_text(encoding="utf-8")
    assert "/investigate" in text
    assert 'investigation["validated_findings"]' in text
    assert "g.query(" not in text
    assert "MERGE (f:Finding" not in text


def test_action_test_selects_maintenance_finding_by_category() -> None:
    text = SMOKE.read_text(encoding="utf-8")
    assert 'category"] == "maintenance"' in text
