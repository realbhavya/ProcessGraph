from __future__ import annotations

import os
import time

import httpx

BASE = os.getenv("API_BASE_URL", "http://backend:8000")


def wait_ready():
    for _ in range(60):
        try:
            if httpx.get(f"{BASE}/ready", timeout=2).status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("API did not become ready")


def main():
    wait_ready()
    key = "m3-create-incident-0001"
    payload = {
        "summary": "R-101 temperature is high and cooling-water flow is falling.",
        "equipment_names": ["R-101"],
        "observations": [
            {"parameter": "temperature", "qualifier": "high"},
            {"parameter": "cooling_water_flow", "qualifier": "falling"},
        ],
    }
    first = httpx.post(f"{BASE}/api/v1/incidents", json=payload, headers={"Idempotency-Key": key}, timeout=10)
    assert first.status_code == 201, first.text
    incident = first.json()
    second = httpx.post(f"{BASE}/api/v1/incidents", json=payload, headers={"Idempotency-Key": key}, timeout=10)
    assert second.status_code == 201 and second.json()["id"] == incident["id"]

    fetched = httpx.get(f"{BASE}/api/v1/incidents/{incident['id']}", timeout=10)
    assert fetched.status_code == 200
    assert len(fetched.json()["observations"]) == 2

    missing_key = httpx.post(f"{BASE}/api/v1/incidents", json=payload, timeout=10)
    assert missing_key.status_code == 400

    invalid = httpx.post(
        f"{BASE}/api/v1/incidents/{incident['id']}/state",
        json={"target_state": "COMPLETED", "reason": "illegal jump"},
        headers={"Idempotency-Key": "m3-invalid-transition"}, timeout=10,
    )
    assert invalid.status_code == 400

    valid = httpx.post(
        f"{BASE}/api/v1/incidents/{incident['id']}/state",
        json={"target_state": "VALIDATING", "reason": "begin validation"},
        headers={"Idempotency-Key": "m3-valid-transition"}, timeout=10,
    )
    assert valid.status_code == 200 and valid.json()["status"] == "VALIDATING"

    timeline = httpx.get(f"{BASE}/api/v1/incidents/{incident['id']}/timeline", timeout=10)
    assert timeline.status_code == 200 and len(timeline.json()) >= 2

    paths = httpx.get(f"{BASE}/api/v1/incidents/{incident['id']}/paths?depth=4", timeout=10)
    assert paths.status_code == 200
    assert any(item["target_id"] == "EQ-P-201" for item in paths.json())
    print(f"[M3] incident API smoke test passed for {incident['id']}")


if __name__ == "__main__":
    main()
