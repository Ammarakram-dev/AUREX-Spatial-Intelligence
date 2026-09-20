"""
AUREX Spatial Intelligence
Identity & Liveness Tests

Phase 22
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from identity import (
    AUREXIdentityEngine,
    AUREXLivenessEvaluator,
    IdentityState,
    LivenessEvidence,
    LivenessState,
)


def test_no_face():

    engine = AUREXIdentityEngine()

    result = engine.analyze(
        face_detected=False,
        face_confidence=0.95,
    )

    assert result.state == (
        IdentityState.NO_FACE
    )

    assert result.verified is False


def test_face_requires_liveness():

    engine = AUREXIdentityEngine()

    result = engine.analyze(
        face_detected=True,
        face_confidence=0.95,
    )

    assert result.state == (
        IdentityState.LIVENESS_CHECK
    )

    assert result.verified is False


def test_liveness_pass():

    evaluator = (
        AUREXLivenessEvaluator()
    )

    state = evaluator.evaluate_values(
        blink=True,
        head_movement=True,
        facial_motion=True,
        temporal_consistency=True,
        depth_consistency=True,
        challenge_response=True,
    )

    assert state == (
        LivenessState.LIVE
    )


def test_possible_spoof():

    evaluator = (
        AUREXLivenessEvaluator()
    )

    state = evaluator.evaluate_values(
        blink=False,
        head_movement=False,
        facial_motion=False,
        temporal_consistency=False,
        depth_consistency=False,
        challenge_response=False,
    )

    assert state == (
        LivenessState.POSSIBLE_SPOOF
    )


def test_verified_identity():

    engine = AUREXIdentityEngine()

    evidence = [
        LivenessEvidence(
            "blink",
            True,
            0.95,
            1.0,
        ),
        LivenessEvidence(
            "head_movement",
            True,
            0.95,
            1.0,
        ),
        LivenessEvidence(
            "temporal",
            True,
            0.95,
            1.2,
        ),
        LivenessEvidence(
            "depth",
            True,
            0.95,
            1.2,
        ),
        LivenessEvidence(
            "challenge",
            True,
            0.95,
            1.5,
        ),
    ]

    result = engine.analyze(
        face_detected=True,
        face_confidence=0.95,
        identity_match=True,
        identity_confidence=0.95,
        liveness_evidence=evidence,
    )

    assert result.state == (
        IdentityState.VERIFIED
    )

    assert result.verified is True


def test_identity_rejected():

    engine = AUREXIdentityEngine()

    evidence = [
        LivenessEvidence(
            "blink",
            True,
            0.95,
        ),
        LivenessEvidence(
            "head",
            True,
            0.95,
        ),
        LivenessEvidence(
            "temporal",
            True,
            0.95,
        ),
    ]

    result = engine.analyze(
        face_detected=True,
        face_confidence=0.95,
        identity_match=False,
        identity_confidence=0.95,
        liveness_evidence=evidence,
    )

    assert result.state == (
        IdentityState.REJECTED
    )

    assert result.verified is False


def test_serialization():

    engine = AUREXIdentityEngine()

    result = engine.analyze(
        face_detected=True,
        face_confidence=0.90,
    )

    data = result.to_dict()

    assert isinstance(data, dict)
    assert "state" in data
    assert "liveness_state" in data
    assert "verified" in data
    assert "confidence" in data


def test_status():

    engine = AUREXIdentityEngine()

    status = engine.status()

    assert (
        status["engine"]
        == "AUREXIdentityEngine"
    )

    assert status["status"] == "ready"


if __name__ == "__main__":

    test_no_face()
    test_face_requires_liveness()
    test_liveness_pass()
    test_possible_spoof()
    test_verified_identity()
    test_identity_rejected()
    test_serialization()
    test_status()

    print("=" * 78)
    print("AUREX PHASE 22 IDENTITY & LIVENESS TESTS")
    print("=" * 78)
    print("All tests passed.")
    print("=" * 78)