from functools import lru_cache
from typing import Any

from falkordb import FalkorDB

from app.config import Settings, get_settings


class GraphConnectionError(RuntimeError):
    """Raised when FalkorDB cannot be reached or queried."""


def graph_name_for_tenant(tenant_id: str, settings: Settings | None = None) -> str:
    """Pure tenant-to-graph mapping.

    This function intentionally ignores deployment-level graph overrides so its
    result is deterministic and safe to unit test under any process environment.
    """
    cfg = settings or get_settings()
    normalized = tenant_id.strip().lower().replace("-", "_")
    if normalized != "tenant_demo":
        raise ValueError("Milestone 3 supports only TENANT-DEMO")
    return f"{cfg.falkordb_graph_prefix}_{normalized}"


def selected_graph_name(tenant_id: str = "TENANT-DEMO", settings: Settings | None = None) -> str:
    """Resolve an explicit deployment graph override or the tenant mapping.

    The override is useful for isolated deployments and test environments. It is
    applied at connection selection, not inside the tenant mapping function.
    """
    cfg = settings or get_settings()
    override = (cfg.falkordb_graph_name or "").strip()
    return override or graph_name_for_tenant(tenant_id, cfg)


@lru_cache
def get_database() -> FalkorDB:
    cfg = get_settings()
    kwargs: dict[str, Any] = {"host": cfg.falkordb_host, "port": cfg.falkordb_port}
    if cfg.falkordb_password:
        kwargs["password"] = cfg.falkordb_password
    return FalkorDB(**kwargs)


def get_graph(tenant_id: str = "TENANT-DEMO"):
    return get_database().select_graph(selected_graph_name(tenant_id))


def check_falkordb() -> tuple[bool, str]:
    """Run a real graph query to verify connectivity, authentication, and query execution."""
    try:
        result = get_graph().query("RETURN 1 AS ready")
        value = result.result_set[0][0]
        return (value == 1, "ok" if value == 1 else "unexpected_response")
    except Exception as exc:
        return False, f"unavailable:{exc.__class__.__name__}"
