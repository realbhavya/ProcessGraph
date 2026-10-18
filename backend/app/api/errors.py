from fastapi import Request
from fastapi.responses import JSONResponse

from app.graph.errors import GraphError


async def graph_error_handler(request: Request, exc: GraphError) -> JSONResponse:
    status_code = 404 if exc.code == "ENTITY_NOT_FOUND" else 409 if exc.code in {"AMBIGUOUS_ENTITY", "TENANT_MISMATCH"} else 400
    if exc.code in {"DATABASE_UNAVAILABLE", "QUERY_TIMEOUT"}:
        status_code = 503
    return JSONResponse(status_code=status_code, content={"error": {"code": exc.code, "message": exc.message, "retryable": exc.retryable}, "request_id": getattr(request.state, "request_id", None)})


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    import logging
    logging.getLogger("processgraph.api").exception(
        "Unhandled API error request_id=%s path=%s",
        getattr(request.state, "request_id", None),
        request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {"code": "INTERNAL_ERROR", "message": "The request could not be completed", "retryable": False},
            "request_id": getattr(request.state, "request_id", None),
        },
    )
