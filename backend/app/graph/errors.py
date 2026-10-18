from dataclasses import dataclass


@dataclass
class GraphError(Exception):
    code: str
    message: str
    retryable: bool = False

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class EntityNotFound(GraphError):
    def __init__(self, entity: str):
        super().__init__("ENTITY_NOT_FOUND", f"No graph entity matched {entity}")


class AmbiguousEntity(GraphError):
    def __init__(self, entity: str):
        super().__init__("AMBIGUOUS_ENTITY", f"Multiple graph entities matched {entity}")


class TenantMismatch(GraphError):
    def __init__(self):
        super().__init__("TENANT_MISMATCH", "The requested tenant is not available")


class InvalidInput(GraphError):
    def __init__(self, message: str):
        super().__init__("INVALID_INPUT", message)


class QueryTimeout(GraphError):
    def __init__(self):
        super().__init__("QUERY_TIMEOUT", "The graph query exceeded its time limit", True)


class DatabaseUnavailable(GraphError):
    def __init__(self):
        super().__init__("DATABASE_UNAVAILABLE", "FalkorDB is unavailable", True)
