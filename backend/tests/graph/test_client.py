import pytest

from app.config import Settings
from app.graph.client import graph_name_for_tenant, selected_graph_name


def settings(**overrides) -> Settings:
    values = {
        "FALKORDB_GRAPH_PREFIX": "processgraph",
        "FALKORDB_GRAPH_NAME": None,
        **overrides,
    }
    return Settings(_env_file=None, **values)


def test_demo_tenant_maps_to_server_managed_graph_independent_of_environment() -> None:
    assert graph_name_for_tenant("TENANT-DEMO", settings()) == "processgraph_tenant_demo"


def test_explicit_graph_override_is_applied_only_at_selection_boundary() -> None:
    cfg = settings(FALKORDB_GRAPH_NAME="isolated_deployment_graph")
    assert graph_name_for_tenant("TENANT-DEMO", cfg) == "processgraph_tenant_demo"
    assert selected_graph_name("TENANT-DEMO", cfg) == "isolated_deployment_graph"


def test_blank_override_falls_back_to_tenant_mapping() -> None:
    cfg = settings(FALKORDB_GRAPH_NAME="   ")
    assert selected_graph_name("TENANT-DEMO", cfg) == "processgraph_tenant_demo"


def test_unknown_tenant_is_rejected() -> None:
    with pytest.raises(ValueError, match="only TENANT-DEMO"):
        graph_name_for_tenant("OTHER", settings())
