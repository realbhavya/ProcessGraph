"""Compatibility regression tests for the graph validator.

This filename is retained deliberately so upgrades extracted over an earlier
project directory overwrite the former count-threshold test instead of leaving
stale test code behind.
"""

from pathlib import Path


VALIDATOR = Path(__file__).parents[3] / "graph" / "validate.py"


def test_seed_reference_counts_are_exact_and_source_scoped() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    assert 'SEED_SOURCE = "processgraph-sentinel-seed-v1"' in text
    assert "source=SEED_SOURCE" in text
    assert '"seed_baseline_exact"' in text


def test_runtime_growth_is_validated_by_relationship_invariants() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    assert "orphan_observations" in text
    assert "orphan_timeline_events" in text
    assert "incidents_without_session" in text
    assert "incidents_without_equipment" in text


def test_validator_does_not_use_mutable_total_thresholds_as_integrity_rules() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    assert 'report["incidents"] >= 8' not in text
    assert 'report["memories"] >= 3' not in text
    assert 'report["observations"] == 20' not in text
