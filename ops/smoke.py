import os,httpx
base=os.getenv('BASE_URL','http://localhost:8000')
for path in ('/health','/ready','/api/v1/system/capabilities','/metrics'):
 r=httpx.get(base+path,timeout=10); assert r.status_code==200,(path,r.status_code,r.text)
print('[M10] production smoke passed')
