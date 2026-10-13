"""Regression tests for ledger integrity, input validation, and API isolation."""
import pytest
from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail, PHIGuard, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from em_leakage_agent.models import FrontierPayload


def test_hmac_detects_entry_tampering():
    trail = AuditTrail(secret_key="test-only-secret")
    trail.log("worker", "qc", "audit", {"status": "OK"})
    trail.log("worker", "qc", "audit", {"status": "WARN"})
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "forged"
    assert not trail.verify_integrity()


def test_hmac_detects_last_hash_tampering():
    trail = AuditTrail(secret_key="test-only-secret")
    trail.log("worker", "qc", "audit", {"status": "OK"})
    trail.logs[-1]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


def test_trail_snapshot_is_not_mutable_internal_state():
    trail = AuditTrail(secret_key="test-only-secret")
    trail.log("worker", "qc", "audit", {"status": "OK"})
    snapshot = trail.get_trail()
    snapshot[0]["event_type"] = "modified"
    assert trail.verify_integrity()
    assert trail.get_trail()[0]["event_type"] == "audit"


def test_nested_sensitive_identifier_is_rejected():
    payload = SystemTaskPayload(
        task_id="T1", target_identifier="KEY", primary_metric=3,
        attributes={"nested": ["MRN-123456"]}
    )
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(payload)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
def test_frontier_rejects_non_finite_metrics(bad):
    with pytest.raises(ValueError):
        FrontierPayload("T1", "KEY", bad, 0.0, "NOMINAL")


def test_frontier_rejects_blank_identifiers():
    with pytest.raises(ValueError):
        FrontierPayload("  ", "KEY", 1.0, 0.0, "NOMINAL")


def test_api_requires_configured_token(monkeypatch):
    monkeypatch.setenv("API_AUTH_TOKEN", "test-only-api-token")
    client = TestClient(app)
    payload = {"task_id": "TASK-A", "target_identifier": "KEY-A", "primary_metric": 2}
    assert client.post("/api/audit", json=payload).status_code == 401
    assert client.get("/api/audit/logs").status_code == 401
    assert client.post("/api/audit", json=payload,
                       headers={"X-API-Key": "test-only-api-token"}).status_code == 200


def test_api_rejects_sensitive_identifiers(monkeypatch):
    monkeypatch.delenv("API_AUTH_TOKEN", raising=False)
    client = TestClient(app)
    payload = {"task_id": "TASK-A", "target_identifier": "MRN-123456", "primary_metric": 2}
    assert client.post("/api/audit", json=payload).status_code == 422
