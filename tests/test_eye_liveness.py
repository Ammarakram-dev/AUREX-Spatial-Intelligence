from identity.eye_liveness import (
    AUREXEyeLiveness,
    EyeState,
)

from identity.eye_lock import (
    AUREXEyeLock,
    EyeLockState,
)


def test_liveness_requires_multiple_signals():
    evaluator = AUREXEyeLiveness()

    result = evaluator.update(
        EyeState.OPEN,
        confidence=0.95,
    )

    assert result.live is False

    evaluator.update(
        EyeState.CLOSED,
        head_movement=True,
        confidence=0.95,
    )

    result = evaluator.update(
        EyeState.OPEN,
        facial_motion=True,
        confidence=0.95,
    )

    assert result.live is True
    assert result.blink_detected is True

    print("Multi-signal liveness: PASS")


def test_eye_lock_verified():
    evaluator = AUREXEyeLiveness()

    evaluator.update(EyeState.OPEN, confidence=0.95)
    evaluator.update(
        EyeState.CLOSED,
        head_movement=True,
        confidence=0.95,
    )

    liveness = evaluator.update(
        EyeState.OPEN,
        facial_motion=True,
        confidence=0.95,
    )

    lock = AUREXEyeLock()

    decision = lock.evaluate(
        identity_matched=True,
        identity_confidence=0.95,
        liveness=liveness,
    )

    assert decision.state == EyeLockState.VERIFIED
    assert decision.verified is True

    print("EyeLock verification: PASS")


def test_eye_lock_rejects_unknown_identity():
    evaluator = AUREXEyeLiveness()

    evaluator.update(EyeState.OPEN, confidence=0.95)
    evaluator.update(
        EyeState.CLOSED,
        head_movement=True,
        confidence=0.95,
    )

    liveness = evaluator.update(
        EyeState.OPEN,
        facial_motion=True,
        confidence=0.95,
    )

    lock = AUREXEyeLock()

    decision = lock.evaluate(
        identity_matched=False,
        identity_confidence=0.0,
        liveness=liveness,
    )

    assert decision.state == EyeLockState.REJECTED
    assert decision.verified is False

    print("Unknown identity rejection: PASS")


def test_eye_lock_waits_for_liveness():
    evaluator = AUREXEyeLiveness()

    liveness = evaluator.update(
        EyeState.OPEN,
        confidence=0.95,
    )

    lock = AUREXEyeLock()

    decision = lock.evaluate(
        identity_matched=True,
        identity_confidence=0.95,
        liveness=liveness,
    )

    assert decision.state == EyeLockState.VERIFYING
    assert decision.requires_more_evidence is True

    print("Liveness verification gate: PASS")


if __name__ == "__main__":
    test_liveness_requires_multiple_signals()
    test_eye_lock_verified()
    test_eye_lock_rejects_unknown_identity()
    test_eye_lock_waits_for_liveness()

    print()
    print("PHASE 26 UNIT TEST: PASS")