"""
AUREX Spatial Intelligence
Intent Intelligence Tests

Phase 19
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from core.intent.intent import (
    ActionType,
    IntentType,
)

from core.intent.intent_engine import (
    AUREXIntentEngine,
)


class FakeContext:

    def __init__(
        self,
        context_type="normal",
        confidence=0.90,
    ):
        self.context_type = context_type
        self.confidence = confidence


class FakePerson:

    def __init__(
        self,
        person_id="person_1",
        movement_distance=0.0,
        movement_direction="stationary",
        confidence=0.90,
    ):
        self.person_id = person_id
        self.movement_distance = movement_distance
        self.movement_direction = movement_direction
        self.detection_confidence = confidence


class FakeRelationship:

    def __init__(
        self,
        relationship="near",
        confidence=0.90,
    ):
        self.relationship = relationship
        self.confidence = confidence


def test_no_signal():

    engine = AUREXIntentEngine()

    result = engine.infer()

    assert result.primary.intent_type == (
        IntentType.OBSERVE
    )

    assert result.action is not None


def test_air_draw_gesture():

    engine = AUREXIntentEngine()

    result = engine.infer(
        gestures=[
            {
                "gesture": "air_draw",
                "confidence": 0.95,
            }
        ]
    )

    assert result.primary.intent_type == (
        IntentType.AIR_DRAW
    )

    assert result.action.action_type == (
        ActionType.AIR_CANVAS
    )


def test_air_select_gesture():

    engine = AUREXIntentEngine()

    result = engine.infer(
        gestures=[
            {
                "gesture": "select",
                "confidence": 0.90,
            }
        ]
    )

    assert result.primary.intent_type == (
        IntentType.AIR_SELECT
    )


def test_clear_gesture():

    engine = AUREXIntentEngine()

    result = engine.infer(
        gestures=[
            {
                "gesture": "clear",
                "confidence": 0.95,
            }
        ]
    )

    assert result.primary.intent_type == (
        IntentType.AIR_CLEAR
    )


def test_help_intent():

    engine = AUREXIntentEngine()

    result = engine.infer(
        voice_intents=[
            {
                "intent": "help",
                "confidence": 0.90,
            }
        ]
    )

    assert result.primary.intent_type == (
        IntentType.REQUEST_HELP
    )

    assert result.action.action_type == (
        ActionType.NOTIFY
    )


def test_emergency_intent():

    engine = AUREXIntentEngine()

    result = engine.infer(
        voice_intents=[
            {
                "intent": "emergency",
                "confidence": 0.98,
            }
        ]
    )

    assert result.primary.intent_type == (
        IntentType.EMERGENCY
    )

    assert result.action.action_type == (
        ActionType.EMERGENCY_WORKFLOW
    )

    assert result.action.requires_confirmation


def test_approaching_context():

    engine = AUREXIntentEngine()

    context = FakeContext(
        context_type="person_approaching",
        confidence=0.90,
    )

    result = engine.infer(
        context=context
    )

    assert result.primary.intent_type == (
        IntentType.APPROACH
    )


def test_approaching_person():

    engine = AUREXIntentEngine()

    person = FakePerson(
        movement_distance=0.50,
        movement_direction="approaching",
    )

    result = engine.infer(
        human_states=[person]
    )

    assert result.primary.intent_type == (
        IntentType.APPROACH
    )


def test_approaching_relationship():

    engine = AUREXIntentEngine()

    relationship = FakeRelationship(
        relationship="approaching",
        confidence=0.95,
    )

    result = engine.infer(
        relationships=[relationship]
    )

    assert result.primary.intent_type == (
        IntentType.APPROACH
    )


def test_multimodal_evidence():

    engine = AUREXIntentEngine()

    result = engine.infer(
        gestures=[
            {
                "gesture": "air_draw",
                "confidence": 0.90,
            }
        ],
        voice_intents=[
            {
                "intent": "air_draw",
                "confidence": 0.92,
            }
        ],
    )

    assert result.primary.intent_type == (
        IntentType.AIR_DRAW
    )

    assert len(result.primary.evidence) >= 2

    assert result.primary.confidence > 0.80


def test_action_requires_safety_gate():

    engine = AUREXIntentEngine()

    result = engine.infer(
        gestures=[
            {
                "gesture": "air_clear",
                "confidence": 0.90,
            }
        ]
    )

    assert result.action is not None

    assert result.action.approved is False

    assert result.action.requires_confirmation


def test_approval_gate():

    engine = AUREXIntentEngine()

    result = engine.infer(
        gestures=[
            {
                "gesture": "air_draw",
                "confidence": 0.99,
            }
        ]
    )

    action = engine.approve(result)

    assert action.approved is False

    assert (
        "confirmation"
        in action.reason.lower()
    )


def test_serialization():

    engine = AUREXIntentEngine()

    result = engine.infer(
        gestures=[
            {
                "gesture": "select",
                "confidence": 0.90,
            }
        ]
    )

    data = result.to_dict()

    assert isinstance(data, dict)

    assert "primary" in data

    assert "candidates" in data

    assert "action" in data


def test_engine_status():

    engine = AUREXIntentEngine()

    status = engine.status()

    assert status["engine"] == (
        "AUREXIntentEngine"
    )

    assert status["status"] == "ready"


if __name__ == "__main__":

    test_no_signal()
    test_air_draw_gesture()
    test_air_select_gesture()
    test_clear_gesture()
    test_help_intent()
    test_emergency_intent()
    test_approaching_context()
    test_approaching_person()
    test_approaching_relationship()
    test_multimodal_evidence()
    test_action_requires_safety_gate()
    test_approval_gate()
    test_serialization()
    test_engine_status()

    print("=" * 75)
    print("AUREX PHASE 19 INTENT INTELLIGENCE TESTS")
    print("=" * 75)
    print("All tests passed.")
    print("=" * 75)