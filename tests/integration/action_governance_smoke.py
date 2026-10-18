import os
import time

import httpx

BASE = os.getenv("API_BASE_URL", "http://backend:8000")


def expect(response, expected_status):
    assert response.status_code == expected_status, f"HTTP {response.status_code}: {response.text}"
    return response.json()


for _ in range(60):
    try:
        if httpx.get(f"{BASE}/ready", timeout=2).status_code == 200:
            break
    except Exception:
        pass
    time.sleep(1)
else:
    raise RuntimeError("API unavailable")

# Produce the validated finding through the real incident and investigation
# workflow. The action test does not inject privileged fixture nodes directly.
incident = expect(
    httpx.post(
        f"{BASE}/api/v1/incidents",
        json={
            "summary": "R-101 temperature is high and cooling-water flow is falling.",
            "equipment_names": ["R-101"],
            "observations": [
                {"parameter": "temperature", "qualifier": "high"},
                {"parameter": "cooling_water_flow", "qualifier": "falling"},
            ],
        },
        headers={"Idempotency-Key": "m7-incident-001"},
        timeout=20,
    ),
    201,
)
investigation = expect(
    httpx.post(
        f"{BASE}/api/v1/incidents/{incident['id']}/investigate",
        headers={"Idempotency-Key": "m7-investigation-001"},
        timeout=40,
    ),
    200,
)
validated = investigation["validated_findings"]
assert validated, investigation
finding_id = next(
    item["finding"]["finding_id"]
    for item in validated
    if item["finding"]["category"] == "maintenance"
)

payload = {
    "finding_id": finding_id,
    "team_id": "TEAM-UTIL",
    "action_type": "CREATE_INSPECTION_TASK",
    "summary": "Create a synthetic P-201 inspection workflow task.",
    "rationale": "Validated finding supports a non-control inspection workflow.",
    "reversibility": "administrative",
}
action = expect(
    httpx.post(
        f"{BASE}/api/v1/actions/proposals",
        json=payload,
        headers={"Idempotency-Key": "m7-action-001"},
        timeout=10,
    ),
    201,
)["id"]

denied = httpx.post(
    f"{BASE}/api/v1/actions/{action}/execute",
    json={"executor_id": "SYSTEM-SIM"},
    headers={"Idempotency-Key": "m7-exec-denied"},
    timeout=10,
)
assert denied.status_code == 400, denied.text

expect(
    httpx.post(
        f"{BASE}/api/v1/actions/{action}/decision",
        json={
            "decision": "approve",
            "reviewer_id": "PERSON-H",
            "reason": "Synthetic inspection workflow approved after evidence review.",
        },
        headers={"Idempotency-Key": "m7-review-001"},
        timeout=10,
    ),
    200,
)
executed = expect(
    httpx.post(
        f"{BASE}/api/v1/actions/{action}/execute",
        json={"executor_id": "SYSTEM-SIM", "mode": "simulation"},
        headers={"Idempotency-Key": "m7-exec-001"},
        timeout=10,
    ),
    200,
)
assert executed["mode"] == "simulation"
assert "no plant control performed" in executed["output"]

state = expect(httpx.get(f"{BASE}/api/v1/actions/{action}", timeout=10), 200)
assert state["status"] == "EXECUTED"
assert len(state["reviews"]) == 1
assert len(state["executions"]) == 1
print("[M7] action governance smoke test passed")
