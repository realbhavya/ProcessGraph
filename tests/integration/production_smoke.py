import os,httpx
base=os.getenv('API_BASE_URL','http://backend:8000')
for path in ('/health','/ready','/api/v1/system/capabilities','/metrics'):
 r=httpx.get(base+path,timeout=10); assert r.status_code==200,(path,r.text)
c=httpx.get(base+'/api/v1/system/capabilities').json(); assert c=={'graph':'FalkorDB','tenant_mode':'isolated-demo','synthetic_only':True,'max_traversal_depth':4,'action_execution':'simulation-only','human_approval_required':True,'arbitrary_cypher_exposed':False}
metrics=httpx.get(base+'/metrics').text; assert 'processgraph_http_requests_total' in metrics and 'processgraph_http_request_duration_seconds_count' in metrics
print('[M10] operational smoke passed')
