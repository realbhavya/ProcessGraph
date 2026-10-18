from pathlib import Path


SERVICE = Path(__file__).parents[2] / "app" / "tools" / "service.py"


def test_audit_identity_is_distinct_from_request_correlation_identity() -> None:
    text = SERVICE.read_text(encoding="utf-8")
    assert "uuid4().hex.upper()" in text
    assert "sha256" not in text
    assert "payload.request_id" not in text.split("def _audit_id", 1)[1].split("def execute", 1)[0]
