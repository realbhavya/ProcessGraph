from fastapi import APIRouter,Response
from app.observability.metrics import registry
router=APIRouter(tags=["operations"])
@router.get("/metrics",include_in_schema=False)
def metrics(): return Response(registry.render(),media_type="text/plain; version=0.0.4")
@router.get("/api/v1/system/capabilities")
def capabilities():
 return {"graph":"FalkorDB","tenant_mode":"isolated-demo","synthetic_only":True,"max_traversal_depth":4,"action_execution":"simulation-only","human_approval_required":True,"arbitrary_cypher_exposed":False}
