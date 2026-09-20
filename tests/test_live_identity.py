"""
AUREX Spatial Intelligence
Live Identity & Liveness Pipeline

Phase 22
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from identity import (
    AUREXIdentityEngine,
)


def main() -> None:

    print("=" * 78)
    print("AUREX — LIVE IDENTITY & LIVENESS")
    print("=" * 78)

    engine = AUREXIdentityEngine()

    print()
    print("[1] No face")

    result = engine.analyze_values(
        face_detected=False,
        face_confidence=0.98,
    )

    print(
        f"State: {result.state.value}"
    )

    print(
        f"Verified: {result.verified}"
    )

    print()
    print("[2] Face detected")

    result = engine.analyze_values(
        face_detected=True,
        face_confidence=0.96,
    )

    print(
        f"State: {result.state.value}"
    )

    print(
        f"Liveness: "
        f"{result.liveness_state.value}"
    )

    print()
    print("[3] Liveness verification")

    result = engine.analyze_values(
        face_detected=True,
        face_confidence=0.96,
        blink=True,
        head_movement=True,
        facial_motion=True,
        temporal_consistency=True,
        depth_consistency=True,
        challenge_response=True,
        liveness_confidence=0.96,
    )

    print(
        f"State: {result.state.value}"
    )

    print(
        f"Liveness: "
        f"{result.liveness_state.value}"
    )

    print(
        f"Confidence: "
        f"{result.confidence:.2f}"
    )

    print()
    print("[4] Identity verification")

    result = engine.analyze_values(
        face_detected=True,
        face_confidence=0.98,
        identity_match=True,
        identity_confidence=0.97,
        blink=True,
        head_movement=True,
        facial_motion=True,
        temporal_consistency=True,
        depth_consistency=True,
        challenge_response=True,
        liveness_confidence=0.97,
    )

    print(
        f"State: {result.state.value}"
    )

    print(
        f"Liveness: "
        f"{result.liveness_state.value}"
    )

    print(
        f"Verified: {result.verified}"
    )

    print(
        f"Confidence: "
        f"{result.confidence:.2f}"
    )

    print()
    print("[5] Spoof simulation")

    result = engine.analyze_values(
        face_detected=True,
        face_confidence=0.98,
        identity_match=True,
        identity_confidence=0.98,
        blink=False,
        head_movement=False,
        facial_motion=False,
        temporal_consistency=False,
        depth_consistency=False,
        challenge_response=False,
        liveness_confidence=0.95,
    )

    print(
        f"State: {result.state.value}"
    )

    print(
        f"Liveness: "
        f"{result.liveness_state.value}"
    )

    print(
        f"Verified: {result.verified}"
    )

    print()
    print("Engine status:")
    print(engine.status())

    print()
    print("=" * 78)
    print("AUREX PHASE 22 IDENTITY PIPELINE COMPLETE")
    print("=" * 78)


if __name__ == "__main__":
    main()