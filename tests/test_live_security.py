"""
AUREX Spatial Intelligence
Live Security Intelligence Test

Phase 21
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from core.security import (
    AUREXSecurityEngine,
)


def main() -> None:

    print("=" * 78)
    print("AUREX — LIVE SECURITY INTELLIGENCE")
    print("=" * 78)

    engine = AUREXSecurityEngine()

    print()
    print("[1] No presence")

    decision = engine.analyze_values(
        presence=False,
        presence_confidence=0.98,
    )

    print(
        f"State: {decision.state.value}"
    )

    print(
        f"Authorized: {decision.authorized}"
    )

    print()
    print("[2] Presence detected")

    decision = engine.analyze_values(
        presence=True,
        presence_confidence=0.96,
    )

    print(
        f"State: {decision.state.value}"
    )

    print(
        f"Verification required: "
        f"{decision.requires_verification}"
    )

    print()
    print("[3] Presence + liveness")

    decision = engine.analyze_values(
        presence=True,
        liveness=True,
        face_detected=True,
        presence_confidence=0.96,
        liveness_confidence=0.94,
        face_confidence=0.93,
    )

    print(
        f"State: {decision.state.value}"
    )

    print(
        f"Confidence: "
        f"{decision.confidence:.2f}"
    )

    print()
    print("[4] Trusted identity")

    decision = engine.analyze_values(
        presence=True,
        liveness=True,
        identity=True,
        face_detected=True,
        presence_confidence=0.98,
        liveness_confidence=0.97,
        identity_confidence=0.98,
        face_confidence=0.96,
    )

    print(
        f"State: {decision.state.value}"
    )

    print(
        f"Authorized: {decision.authorized}"
    )

    print(
        f"Confidence: "
        f"{decision.confidence:.2f}"
    )

    print()
    print("[5] Suspicious behavior")

    decision = engine.analyze_values(
        presence=True,
        liveness=True,
        identity=True,
        behavior="suspicious",
        presence_confidence=0.97,
        liveness_confidence=0.96,
        identity_confidence=0.96,
        behavior_confidence=0.94,
    )

    print(
        f"State: {decision.state.value}"
    )

    print(
        f"Security level: "
        f"{decision.level.value}"
    )

    print(
        f"Authorized: {decision.authorized}"
    )

    print()
    print("Engine status:")
    print(engine.status())

    print()
    print("=" * 78)
    print("AUREX PHASE 21 SECURITY PIPELINE COMPLETE")
    print("=" * 78)


if __name__ == "__main__":
    main()