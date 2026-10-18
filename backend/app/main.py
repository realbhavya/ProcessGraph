from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.actions import router as actions_router
from app.api.errors import graph_error_handler, unexpected_error_handler
from app.api.incidents import router as incidents_router
from app.api.memories import router as memories_router
from app.api.operations import router as operations_router
from app.observability.middleware import MetricsMiddleware
from app.config import get_settings
from app.graph.errors import GraphError
from app.graph.client import check_falkordb
from app.logging_config import configure_logging
from app.middleware import RequestIdMiddleware
from app.schemas import HealthResponse, ReadinessResponse

settings = get_settings()
configure_logging(settings.app_log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Foundation API for a graph-native, synthetic chemical-process incident-triage "
        "and agent-memory demonstration."
    ),
    lifespan=lifespan,
)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_exception_handler(GraphError, graph_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)
app.include_router(incidents_router)
app.include_router(actions_router)
app.include_router(memories_router)
app.include_router(operations_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID", "Idempotency-Key"],
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )


@app.get("/ready", response_model=ReadinessResponse, tags=["system"])
async def ready(response: Response) -> ReadinessResponse:
    graph_ready, graph_status = check_falkordb()
    if not graph_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(status="not_ready", checks={"api": "ok", "falkordb": graph_status})
    return ReadinessResponse(status="ready", checks={"api": "ok", "falkordb": "ok"})
