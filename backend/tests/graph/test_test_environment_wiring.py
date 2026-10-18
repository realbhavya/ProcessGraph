from pathlib import Path


def test_m3_runner_sets_graph_before_backend_start() -> None:
    text = (Path(__file__).parents[3] / "test_m3.ps1").read_text(encoding="utf-8")
    assignment = text.index("$env:FALKORDB_TEST_GRAPH = $TestGraph")
    startup = text.index("up -d falkordb backend")
    assert assignment < startup


def test_compose_override_routes_backend_to_isolated_graph() -> None:
    text = (Path(__file__).parents[3] / "docker-compose.test.yml").read_text(encoding="utf-8")
    assert "FALKORDB_GRAPH_NAME: ${FALKORDB_TEST_GRAPH}" in text
