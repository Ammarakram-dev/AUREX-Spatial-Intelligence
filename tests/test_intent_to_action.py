"""
AUREX Spatial Intelligence
Intent-to-Action Integration

Phase 20
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from core.actions import (
    AUREXActionOrchestrator,
)

from core.actions.adapters import (
    register_default_actions,
)

from core.intent import (
    AUREXIntentEngine,
)


def main() -> None:

    print("=" * 78)
    print("AUREX — INTENT TO ACTION PIPELINE")
    print("=" * 78)

    intent_engine = (
        AUREXIntentEngine()
    )

    orchestrator = (
        AUREXActionOrchestrator()
    )

    register_default_actions(
        orchestrator
    )

    print()
    print("[1] Simulating multimodal intent...")

    intent = intent_engine.infer(
        gestures=[
            {
                "gesture": "air_draw",
                "confidence": 0.95,
            }
        ],
        voice_intents=[
            {
                "intent": "air_draw",
                "confidence": 0.92,
            }
        ],
    )

    print(
        f"Intent: "
        f"{intent.primary.intent_type.value}"
    )

    print(
        f"Confidence: "
        f"{intent.primary.confidence:.2f}"
    )

    print(
        f"Proposed action: "
        f"{intent.action.action_type.value}"
    )

    print()
    print("[2] Creating action request...")

    request = orchestrator.from_intent(
        intent
    )

    print(
        f"Action ID: "
        f"{request.action_id}"
    )

    print(
        f"Action: "
        f"{request.action_type}"
    )

    print(
        f"Risk: "
        f"{request.risk.value}"
    )

    print(
        f"Confirmation required: "
        f"{request.requires_confirmation}"
    )

    print()
    print("[3] Applying safety gate...")

    allowed = orchestrator.safety_check(
        request
    )

    print(
        f"Allowed immediately: "
        f"{allowed}"
    )

    print(
        f"Status: "
        f"{request.status.value}"
    )

    if not allowed:

        print()
        print(
            "[4] Action is waiting for confirmation."
        )

        print(
            "No action is executed automatically."
        )

        print()
        print(
            "Simulating explicit user confirmation..."
        )

        orchestrator.confirm(
            request.action_id
        )

    print()
    print("[5] Executing approved action...")

    result = orchestrator.execute(
        request.action_id
    )

    print(
        f"Success: "
        f"{result.success}"
    )

    print(
        f"Status: "
        f"{result.status.value}"
    )

    print(
        f"Message: "
        f"{result.message}"
    )

    print()
    print("=" * 78)
    print("AUREX INTENT → ACTION PIPELINE COMPLETE")
    print("=" * 78)


if __name__ == "__main__":
    main()