from fastapi.testclient import TestClient
from app.main import app
def test_capabilities_are_explicit():
 d=TestClient(app).get('/api/v1/system/capabilities').json(); assert d['synthetic_only'] is True and d['action_execution']=='simulation-only' and d['arbitrary_cypher_exposed'] is False
def test_metrics_endpoint_is_prometheus_text():
 r=TestClient(app).get('/metrics'); assert r.status_code==200 and 'processgraph_http_requests_total' in r.text
