import os, time, httpx
from falkordb import FalkorDB
BASE=os.getenv("API_BASE_URL","http://backend:8000")
for _ in range(60):
    try:
        if httpx.get(f"{BASE}/ready",timeout=2).status_code==200: break
    except Exception: pass
    time.sleep(1)
else: raise RuntimeError("API unavailable")
payload={"summary":"R-101 temperature is high and cooling-water flow is falling.","equipment_names":["R-101"],"observations":[{"parameter":"temperature","qualifier":"high"},{"parameter":"cooling_water_flow","qualifier":"falling"}]}
r=httpx.post(f"{BASE}/api/v1/incidents",json=payload,headers={"Idempotency-Key":"m5-incident-0001"},timeout=20); assert r.status_code==201,r.text
incident=r.json()["id"]
r=httpx.post(f"{BASE}/api/v1/incidents/{incident}/investigate",headers={"Idempotency-Key":"m5-investigation-0001"},timeout=40); assert r.status_code==200,r.text
result=r.json(); assert result["status"]=="COMPLETED",result
assert len(result["validated_findings"])==3
assert len(result["handoff_ids"])==1
assert not result["failed_tasks"]
get=httpx.get(f"{BASE}/api/v1/incidents/{incident}/investigation/{result['investigation_id']}",timeout=10); assert get.status_code==200
state=get.json(); assert len(state["tasks"])==3 and len(state["findings"])>=3 and len(state["handoffs"])==1
g=FalkorDB(host=os.getenv("FALKORDB_HOST","falkordb"),port=6379,password=os.getenv("FALKORDB_PASSWORD")).select_graph(os.environ["FALKORDB_GRAPH_NAME"])
shared=g.ro_query("MATCH (:Handoff)-[:TO_AGENT]->(:Agent {id:'AGENT-MEM'}) RETURN count(*)").result_set[0][0]; assert shared==1
print("[M5] multi-agent workflow smoke test passed")
