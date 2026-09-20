"""
AUREX Spatial Intelligence
Security Intelligence Tests

Phase 21
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from core.security import (
    AUREXSecurityEngine,
    SecurityLevel,
    SecuritySignal,
    SecuritySignalType,
    SecurityState,
)


def test_empty_signals():

    engine = AUREXSecurityEngine()

    decision = engine.analyze()

    assert decision.state == (
        SecurityState.UNKNOWN
    )

    assert decision.authorized is False


def test_presence_only():

    engine = AUREXSecurityEngine()

    decision = engine.analyze_values(
        presence=True,
        presence_confidence=0.95,
    )

    assert decision.state == (
        SecurityState.VERIFYING
    )

    assert decision.authorized is False


def test_presence_and_liveness():

    engine = AUREXSecurityEngine()

    decision = engine.analyze_values(
        presence=True,
        liveness=True,
        presence_confidence=0.95,
        liveness_confidence=0.95,
    )

    assert decision.state == (
        SecurityState.VERIFYING
    )

    assert decision.requires_verification


def test_trusted_identity():

    engine = AUREXSecurityEngine()

    decision = engine.analyze_values(
        presence=True,
        liveness=True,
        identity=True,
        face_detected=True,
        presence_confidence=0.95,
        liveness_confidence=0.95,
        identity_confidence=0.95,
        face_confidence=0.95,
    )

    assert decision.state == (
        SecurityState.TRUSTED
    )

    assert decision.authorized is True

    assert decision.level == (
        SecurityLevel.LOW
    )


def test_identity_failure():

    engine = AUREXSecurityEngine()

    decision = engine.analyze_values(
        presence=True,
        liveness=True,
        identity=False,
        presence_confidence=0.95,
        liveness_confidence=0.95,
        identity_confidence=0.95,
    )

    assert decision.state == (
        SecurityState.DENIED
    )

    assert decision.authorized is False


def test_liveness_failure():

    engine = AUREXSecurityEngine()

    decision = engine.analyze_values(
        presence=True,
        liveness=False,
        presence_confidence=0.95,
        liveness_confidence=0.95,
    )

    assert decision.state == (
        SecurityState.VERIFYING
    )

    assert decision.authorized is False


def test_suspicious_behavior():

    engine = AUREXSecurityEngine()

    decision = engine.analyze_values(
        presence=True,
        liveness=True,
        identity=True,
        behavior="suspicious",
        presence_confidence=0.95,
        liveness_confidence=0.95,
        identity_confidence=0.95,
        behavior_confidence=0.95,
    )

    assert decision.state == (
        SecurityState.SUSPICIOUS
    )

    assert decision.level == (
        SecurityLevel.HIGH
    )

    assert decision.authorized is False


def test_low_confidence():

    engine = AUREXSecurityEngine()

    decision = engine.analyze_values(
        presence=True,
        liveness=True,
        identity=True,
        presence_confidence=0.40,
        liveness_confidence=0.40,
        identity_confidence=0.40,
    )

    assert decision.authorized is False


def test_signal_serialization():

    signal = SecuritySignal(
        signal_type=SecuritySignalType.LIVENESS,
        value=True,
        confidence=0.91,
        source="test",
    )

    data = signal.to_dict()

    assert isinstance(data, dict)

    assert data["signal_type"] == (
        "liveness"
    )

    assert data["confidence"] == 0.91


def test_decision_serialization():

    engine = AUREXSecurityEngine()

    decision = engine.analyze_values(
        presence=True,
        liveness=True,
        identity=True,
        presence_confidence=0.95,
        liveness_confidence=0.95,
        identity_confidence=0.95,
    )

    data = decision.to_dict()

    assert isinstance(data, dict)

    assert "state" in data

    assert "level" in data

    assert "authorized" in data

    assert "confidence" in data


def test_engine_status():

    engine = AUREXSecurityEngine()

    status = engine.status()

    assert (
        status["engine"]
        == "AUREXSecurityEngine"
    )

    assert status["status"] == "ready"


if __name__ == "__main__":

    test_empty_signals()
    test_presence_only()
    test_presence_and_liveness()
    test_trusted_identity()
    test_identity_failure()
    test_liveness_failure()
    test_suspicious_behavior()
    test_low_confidence()
    test_signal_serialization()
    test_decision_serialization()
    test_engine_status()

    print("=" * 78)
    print("AUREX PHASE 21 SECURITY INTELLIGENCE TESTS")
    print("=" * 78)
    print("All tests passed.")
    print("=" * 78)