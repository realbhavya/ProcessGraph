from pathlib import Path


SMOKE_TEST = Path(__file__).parents[3] / "tests" / "integration" / "memory_lifecycle_smoke.py"


def test_candidate_isolation_checks_candidate_identity_not_empty_database() -> None:
    text = SMOKE_TEST.read_text(encoding="utf-8")
    assert 'all(item["id"] != old for item in before_approval)' in text
    assert 'assert baseline_ids' in text
    assert 'baseline_ids.issubset' in text
    assert 'assert not expect_json' not in text
