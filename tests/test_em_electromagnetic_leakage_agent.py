"""
Automated Pytest Test Suite for Em Electromagnetic Leakage Agent.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_input_validation_rejects_nan():
    """NaN metric values must be rejected by the payload validator."""
    with pytest.raises(ValueError, match="finite"):
        SystemTaskPayload(task_id="T-NAN", target_identifier="KEY-NAN", primary_metric=float("nan"))


def test_input_validation_rejects_infinity():
    """Infinite metric values must be rejected by the payload validator."""
    with pytest.raises(ValueError, match="finite"):
        SystemTaskPayload(task_id="T-INF", target_identifier="KEY-INF", primary_metric=float("inf"))


def test_input_validation_rejects_empty_identifiers():
    """Empty or whitespace-only identifiers must be rejected."""
    with pytest.raises(ValueError, match="empty or whitespace"):
        SystemTaskPayload(task_id="   ", target_identifier="KEY-01", primary_metric=10.0)

    with pytest.raises(ValueError, match="empty or whitespace"):
        SystemTaskPayload(task_id="T1", target_identifier="", primary_metric=10.0)


def test_audit_trail_uses_secure_key_by_default():
    """AuditTrail should generate a secure random key when no secret is provided."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        trail = AuditTrail()
    # Key should be 32 bytes (256 bits) of random data, not a hardcoded string
    assert len(trail.secret_key) == 32
    assert trail.secret_key != b"em-electromagnetic-leakage-agent-master-audit-key-2026"


def test_audit_trail_accepts_explicit_key():
    """AuditTrail should use an explicitly provided key."""
    trail = AuditTrail(secret_key="my-test-key")
    assert trail.secret_key == b"my-test-key"


def test_batch_missing_file_returns_error_code():
    """CLI batch command should return non-zero exit code for missing file."""
    assert main(["batch", "-i", "nonexistent_file_xyz.csv"]) == 1
