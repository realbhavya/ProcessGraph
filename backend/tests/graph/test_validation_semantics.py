from pathlib import Path


VALIDATOR = Path(__file__).parents[3] / "graph" / "validate.py"


def test_seed_baseline_is_filtered_by_seed_source() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    assert 'SEED_SOURCE = "processgraph-sentinel-seed-v1"' in text
    assert "source=SEED_SOURCE" in text
    assert '"seed_baseline_exact"' in text


def test_runtime_observations_are_validated_structurally() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    assert "orphan_observations" in text
    assert "HAS_OBSERVATION" in text
    assert "runtime_observations_linked" in text


def test_runtime_incidents_require_session_and_equipment() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    assert "incidents_without_session" in text
    assert "incidents_without_equipment" in text
    assert "runtime_incidents_have_session" in text
    assert "runtime_incidents_have_equipment" in text


def test_all_graph_data_requires_provenance() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    assert "nodes_missing_source" in text
    assert "relationships_missing_source" in text
    assert "node_provenance_complete" in text
    assert "relationship_provenance_complete" in text
