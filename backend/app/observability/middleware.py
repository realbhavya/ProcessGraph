from time import perf_counter
from starlette.middleware.base import BaseHTTPMiddleware
from app.observability.metrics import registry

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request,call_next):
        started=perf_counter()
        try:
            response=await call_next(request); status=str(response.status_code); return response
        except Exception:
            status="500"; raise
        finally:
            route=getattr(request.scope.get("route"),"path",request.url.path)
            labels={"method":request.method,"route":route,"status":status}
            registry.increment("processgraph_http_requests_total",labels)
            registry.observe("processgraph_http_request_duration_seconds",perf_counter()-started,labels)
