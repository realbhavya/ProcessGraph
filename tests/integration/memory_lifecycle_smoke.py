import os,time,httpx
from falkordb import FalkorDB
BASE=os.getenv("API_BASE_URL","http://backend:8000")

def expect_json(response, expected_status=200):
 assert response.status_code == expected_status, f"HTTP {response.status_code}: {response.text}"
 content_type=response.headers.get("content-type","")
 assert "application/json" in content_type, f"Expected JSON, got {content_type}: {response.text}"
 return response.json()
for _ in range(60):
 try:
  if httpx.get(f"{BASE}/ready",timeout=2).status_code==200: break
 except Exception: pass
 time.sleep(1)
else: raise RuntimeError("API unavailable")
base={"outcome_id":"OUT-HIST-001","entity_id":"EQ-R-101","memory_type":"episodic","summary":"Historical cooling-path evidence should be reviewed during similar R-101 investigations.","confidence":.91,"evidence_ids":["INC-HIST-001","EQ-P-201"]}
r=httpx.post(f"{BASE}/api/v1/memories/candidates",json=base,headers={"Idempotency-Key":"m6-memory-old-001"},timeout=10); assert r.status_code==201,r.text
old=r.json()["id"]
# The seed graph intentionally contains approved baseline memories for R-101.
# Candidate isolation therefore means the new candidate is absent from active
# retrieval, not that the complete result set must be empty.
before_approval=expect_json(httpx.post(
 f"{BASE}/api/v1/memories/search",
 json={"entity_id":"EQ-R-101"}, timeout=10,
))
assert all(item["id"] != old for item in before_approval), before_approval
baseline_ids={item["id"] for item in before_approval}
assert baseline_ids, "Seeded active memories should remain available"

httpx.post(f"{BASE}/api/v1/memories/{old}/review",json={"decision":"approve","reason":"Evidence and provenance were reviewed and accepted.","reviewer_id":"PERSON-H"},headers={"Idempotency-Key":"m6-review-old-001"},timeout=10).raise_for_status()
after_approval=expect_json(httpx.post(
 f"{BASE}/api/v1/memories/search",
 json={"entity_id":"EQ-R-101","min_confidence":.8}, timeout=10,
))
assert any(item["id"] == old for item in after_approval), after_approval
assert baseline_ids.issubset({item["id"] for item in after_approval}), after_approval
new_payload={**base,"summary":"Updated reviewed memory: inspect connected P-201 maintenance evidence without treating it as confirmed causality.","confidence":.95}
r=httpx.post(f"{BASE}/api/v1/memories/candidates",json=new_payload,headers={"Idempotency-Key":"m6-memory-new-001"},timeout=10); assert r.status_code==201,r.text
new=r.json()["id"]
httpx.post(f"{BASE}/api/v1/memories/{new}/review",json={"decision":"approve","reason":"Updated evidence-bounded wording approved for future retrieval.","reviewer_id":"PERSON-H"},headers={"Idempotency-Key":"m6-review-new-001"},timeout=10).raise_for_status()
httpx.post(f"{BASE}/api/v1/memories/{old}/supersede",json={"replacement_memory_id":new,"reason":"Replacement provides clearer causality limitations.","reviewer_id":"PERSON-H"},headers={"Idempotency-Key":"m6-supersede-001"},timeout=10).raise_for_status()
assert httpx.get(f"{BASE}/api/v1/memories/{old}",timeout=10).json()["status"]=="superseded"
found=expect_json(httpx.post(f"{BASE}/api/v1/memories/search",json={"entity_id":"EQ-R-101"},timeout=10)); assert any(x["id"]==new for x in found) and all(x["id"]!=old for x in found)
g=FalkorDB(host=os.getenv("FALKORDB_HOST","falkordb"),port=6379,password=os.getenv("FALKORDB_PASSWORD")).select_graph(os.environ["FALKORDB_GRAPH_NAME"])
assert g.ro_query("MATCH (:Memory {id:$new})-[:SUPERSEDES]->(:Memory {id:$old}) RETURN count(*)",params={"new":new,"old":old}).result_set[0][0]==1
print("[M6] memory lifecycle smoke test passed")
