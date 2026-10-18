def test_action_repository_is_importable_from_public_repository_package() -> None:
    from app.graph.repositories import ActionGovernanceRepository
    from app.graph.repositories.action_governance import ActionGovernanceRepository as DirectRepository

    assert ActionGovernanceRepository is DirectRepository
