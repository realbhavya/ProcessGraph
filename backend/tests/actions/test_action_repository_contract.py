from pathlib import Path


REPOSITORY = Path(__file__).parents[2] / "app" / "graph" / "repositories" / "action_governance.py"


def test_proposal_query_uses_established_falkordb_structure() -> None:
    text = REPOSITORY.read_text(encoding="utf-8")
    assert "MATCH (finding:Finding {tenant_id: $tenant_id, id: $finding_id})" in text
    assert "WHERE finding.status = 'validated'" in text
    assert "MATCH (team:Team {tenant_id: $tenant_id, id: $team_id})" in text
    assert "MERGE (action:Action {tenant_id: $tenant_id, idempotency_key: $idempotency_key})" in text
    assert "MERGE (action)-[:ADDRESSES" in text
    assert "MERGE (action)-[:ASSIGNED_TO" in text


def test_proposal_parameters_are_explicitly_projected() -> None:
    text = REPOSITORY.read_text(encoding="utf-8")
    assert "**proposal" not in text
    for field in ("finding_id", "team_id", "action_type", "summary", "rationale", "reversibility"):
        assert f'{field}=proposal["{field}"]' in text
