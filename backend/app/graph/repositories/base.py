from app.graph.errors import InvalidInput, TenantMismatch

SUPPORTED_TENANT = "TENANT-DEMO"


class BaseRepository:
    def __init__(self, executor, tenant_id: str = SUPPORTED_TENANT):
        if tenant_id != SUPPORTED_TENANT:
            raise TenantMismatch()
        self.executor = executor
        self.tenant_id = tenant_id

    def params(self, **values):
        return {"tenant_id": self.tenant_id, **values}

    @staticmethod
    def validate_depth(depth: int) -> int:
        if not isinstance(depth, int) or not 1 <= depth <= 4:
            raise InvalidInput("Traversal depth must be an integer from 1 to 4")
        return depth

    @staticmethod
    def require_id(value: str, prefix: str) -> str:
        if not isinstance(value, str) or not value.startswith(prefix) or len(value) > 100:
            raise InvalidInput(f"Identifier must start with {prefix}")
        return value
