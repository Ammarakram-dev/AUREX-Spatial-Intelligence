"""
AUREX Spatial Intelligence
Phase 24 Adaptive Security Tests
"""

from core.security import (
    AUREXAdaptiveSecurity,
    SecurityState,
)


def main() -> None:

    print("=" * 78)
    print("AUREX — PHASE 24 ADAPTIVE SECURITY TEST")
    print("=" * 78)

    security = AUREXAdaptiveSecurity(
        trusted_stability=3,
        suspicious_stability=2,
    )

    print()
    print("Testing trusted-state stabilization...")

    decisions = []

    for _ in range(3):

        decision = security.evaluate(
            presence=True,
            liveness=True,
            identity=True,
            face_detected=True,
            presence_confidence=0.95,
            liveness_confidence=0.95,
            identity_confidence=0.95,
            face_confidence=0.95,
        )

        decisions.append(decision)

    assert decisions[0].state == (
        SecurityState.VERIFYING
    )

    assert decisions[0].authorized is False

    assert decisions[-1].state == (
        SecurityState.TRUSTED
    )

    assert decisions[-1].authorized is True
    assert decisions[-1].stable is True
    assert decisions[-1].consecutive_trusted == 3

    print(
        "Trusted stabilization: PASS"
    )

    print()
    print("Testing suspicious-state stabilization...")

    security.reset()

    suspicious_decisions = []

    for _ in range(2):

        decision = security.evaluate(
            presence=True,
            liveness=True,
            identity=True,
            face_detected=True,
            behavior="suspicious",
            presence_confidence=0.95,
            liveness_confidence=0.95,
            identity_confidence=0.95,
            face_confidence=0.95,
            behavior_confidence=0.95,
        )

        suspicious_decisions.append(
            decision
        )

    assert suspicious_decisions[-1].state == (
        SecurityState.SUSPICIOUS
    )

    assert suspicious_decisions[-1].authorized is False
    assert suspicious_decisions[-1].stable is True

    print(
        "Suspicious stabilization: PASS"
    )

    print()
    print("Testing no-presence state...")

    security.reset()

    decision = security.evaluate(
        presence=False,
        liveness=False,
        identity=False,
        face_detected=False,
        presence_confidence=0.95,
        liveness_confidence=0.95,
        identity_confidence=0.95,
        face_confidence=0.95,
    )

    assert decision.state == (
        SecurityState.NO_PRESENCE
    )

    assert decision.authorized is False

    print(
        "No-presence handling: PASS"
    )

    print()
    print("Testing status reporting...")

    status = security.status()

    assert status["engine"] == (
        "AUREXAdaptiveSecurity"
    )

    assert status["status"] == "ready"

    print(
        "Status reporting: PASS"
    )

    print()
    print("PHASE 24 UNIT TEST: PASS")
    print("=" * 78)


if __name__ == "__main__":
    main()