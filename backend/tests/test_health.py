from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "ProcessGraph Sentinel"
    assert response.headers["X-Request-ID"]


def test_ready_when_falkordb_is_available() -> None:
    with patch("app.main.check_falkordb", return_value=(True, "ok")):
        response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "checks": {"api": "ok", "falkordb": "ok"}}


def test_not_ready_when_falkordb_is_unavailable() -> None:
    with patch("app.main.check_falkordb", return_value=(False, "unavailable:ConnectionError")):
        response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
