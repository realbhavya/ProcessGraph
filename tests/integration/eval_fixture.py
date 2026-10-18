"""Create real workflow, memory lifecycle, and action lifecycle state for M9 evals."""
import os, time, httpx
BASE=os.getenv("API_BASE_URL","http://backend:8000")
def j(r,code=200): assert r.status_code==code,f"{r.status_code}: {r.text}"; return r.json()
for _ in range(60):
 try:
  if httpx.get(f"{BASE}/ready",timeout=2).status_code==200: break
 except Exception: pass
 time.sleep(1)
else: raise RuntimeError("API unavailable")
inc=j(httpx.post(f"{BASE}/api/v1/incidents",json={"summary":"R-101 temperature high and cooling-water flow falling.","equipment_names":["R-101"],"observations":[{"parameter":"temperature","qualifier":"high"},{"parameter":"cooling_water_flow","qualifier":"falling"}]},headers={"Idempotency-Key":"m9-inc-001"}),201)
inv=j(httpx.post(f"{BASE}/api/v1/incidents/{inc['id']}/investigate",headers={"Idempotency-Key":"m9-inv-001"},timeout=40))
finding=next(x["finding"]["finding_id"] for x in inv["validated_findings"] if x["finding"]["category"]=="maintenance")
action=j(httpx.post(f"{BASE}/api/v1/actions/proposals",json={"finding_id":finding,"team_id":"TEAM-UTIL","action_type":"CREATE_INSPECTION_TASK","summary":"Create synthetic P-201 inspection workflow task.","rationale":"Validated evidence supports a non-control inspection workflow.","reversibility":"administrative"},headers={"Idempotency-Key":"m9-action-001"}),201)
j(httpx.post(f"{BASE}/api/v1/actions/{action['id']}/decision",json={"decision":"approve","reviewer_id":"PERSON-H","reason":"Evaluation approval after evidence review."},headers={"Idempotency-Key":"m9-action-review"}))
out=j(httpx.post(f"{BASE}/api/v1/actions/{action['id']}/execute",json={"executor_id":"SYSTEM-SIM"},headers={"Idempotency-Key":"m9-action-exec"}))
# Outcome is required as governed memory source.
from falkordb import FalkorDB
g=FalkorDB(host=os.getenv("FALKORDB_HOST","falkordb"),port=6379,password=os.getenv("FALKORDB_PASSWORD")).select_graph(os.environ["FALKORDB_GRAPH_NAME"])
g.query("MATCH (a:Action {id:$action}) MERGE (o:Outcome {tenant_id:'TENANT-DEMO',id:'OUT-M9-001'}) SET o.summary='Evaluation action outcome',o.effectiveness='helpful',o.synthetic=true,o.source='runtime' MERGE (a)-[:PRODUCED {tenant_id:'TENANT-DEMO',synthetic:true,source:'runtime'}]->(o)",params={"action":action["id"]})
base={"outcome_id":"OUT-M9-001","entity_id":"EQ-R-101","memory_type":"episodic","summary":"Reviewed evaluation memory for R-101 cooling-path investigation.","confidence":.91,"evidence_ids":[finding,"EQ-P-201"]}
old=j(httpx.post(f"{BASE}/api/v1/memories/candidates",json=base,headers={"Idempotency-Key":"m9-mem-old"}),201)
j(httpx.post(f"{BASE}/api/v1/memories/{old['id']}/review",json={"decision":"approve","reviewer_id":"PERSON-H","reason":"Evaluation evidence and provenance approved."},headers={"Idempotency-Key":"m9-mem-old-review"}))
new=j(httpx.post(f"{BASE}/api/v1/memories/candidates",json={**base,"summary":"Updated reviewed evaluation memory with explicit causality limitation.","confidence":.95},headers={"Idempotency-Key":"m9-mem-new"}),201)
j(httpx.post(f"{BASE}/api/v1/memories/{new['id']}/review",json={"decision":"approve","reviewer_id":"PERSON-H","reason":"Updated bounded wording approved for evaluation."},headers={"Idempotency-Key":"m9-mem-new-review"}))
j(httpx.post(f"{BASE}/api/v1/memories/{old['id']}/supersede",json={"replacement_memory_id":new["id"],"reason":"Replacement has clearer causality limitations.","reviewer_id":"PERSON-H"},headers={"Idempotency-Key":"m9-mem-supersede"}))
print("[M9] evaluation fixture created")
