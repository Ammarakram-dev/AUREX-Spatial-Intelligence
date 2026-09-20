"""
AUREX Spatial Intelligence
Action Orchestration Tests

Phase 20
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from core.actions import (
    ActionRisk,
    ActionStatus,
    AUREXActionOrchestrator,
)

from core.actions.adapters import (
    register_default_actions,
)

from core.intent import (
    AUREXIntentEngine,
)


class FakeIntent:

    def __init__(
        self,
        action_type="display",
        intent_type="observe",
        confidence=0.90,
        requires_confirmation=False,
    ):

        class FakeAction:
            pass

        self.action = FakeAction()

        self.action.action_type = action_type
        self.action.intent_type = intent_type
        self.action.confidence = confidence
        self.action.requires_confirmation = (
            requires_confirmation
        )

        self.action.reason = (
            "Test intent."
        )


def test_orchestrator_status():

    orchestrator = (
        AUREXActionOrchestrator()
    )

    status = orchestrator.status()

    assert (
        status["engine"]
        == "AUREXActionOrchestrator"
    )

    assert status["status"] == "ready"


def test_action_registration():

    orchestrator = (
        AUREXActionOrchestrator()
    )

    def test_handler(**kwargs):
        return {"ok": True}

    orchestrator.register_action(
        "test",
        test_handler,
    )

    assert "test" in (
        orchestrator.adapters
    )


def test_risk_classification():

    orchestrator = (
        AUREXActionOrchestrator()
    )

    assert (
        orchestrator.determine_risk(
            "display"
        )
        == ActionRisk.MEDIUM
    )

    assert (
        orchestrator.determine_risk(
            "emergency_workflow"
        )
        == ActionRisk.CRITICAL
    )


def test_low_confidence_rejected():

    orchestrator = (
        AUREXActionOrchestrator(
            minimum_confidence=0.70
        )
    )

    request = orchestrator.create_request(
        action_type="display",
        source_intent="observe",
        confidence=0.30,
        requires_confirmation=False,
    )

    allowed = orchestrator.safety_check(
        request
    )

    assert allowed is False

    assert request.status == (
        ActionStatus.REJECTED
    )


def test_confirmation_gate():

    orchestrator = (
        AUREXActionOrchestrator()
    )

    request = orchestrator.create_request(
        action_type="display",
        source_intent="observe",
        confidence=0.95,
        requires_confirmation=True,
    )

    allowed = orchestrator.safety_check(
        request
    )

    assert allowed is False

    assert request.status == (
        ActionStatus.WAITING_CONFIRMATION
    )


def test_confirmation_allows_execution():

    orchestrator = (
        AUREXActionOrchestrator()
    )

    register_default_actions(
        orchestrator
    )

    request = orchestrator.create_request(
        action_type="display",
        source_intent="observe",
        confidence=0.95,
        requires_confirmation=True,
        parameters={
            "message": "AUREX test"
        },
    )

    orchestrator.safety_check(
        request
    )

    orchestrator.confirm(
        request.action_id
    )

    result = orchestrator.execute(
        request.action_id
    )

    assert result.success is True

    assert result.status == (
        ActionStatus.COMPLETED
    )


def test_rejected_action_cannot_execute():

    orchestrator = (
        AUREXActionOrchestrator()
    )

    register_default_actions(
        orchestrator
    )

    request = orchestrator.create_request(
        action_type="display",
        source_intent="observe",
        confidence=0.20,
        requires_confirmation=False,
    )

    result = orchestrator.execute(
        request.action_id
    )

    assert result.success is False

    assert result.status == (
        ActionStatus.REJECTED
    )


def test_missing_adapter_fails_cleanly():

    orchestrator = (
        AUREXActionOrchestrator()
    )

    request = orchestrator.create_request(
        action_type="unknown_action",
        source_intent="test",
        confidence=0.95,
        requires_confirmation=False,
    )

    result = orchestrator.execute(
        request.action_id
    )

    assert result.success is False

    assert result.status == (
        ActionStatus.FAILED
    )


def test_handler_exception():

    orchestrator = (
        AUREXActionOrchestrator()
    )

    def failing_handler(**kwargs):
        raise RuntimeError(
            "intentional test failure"
        )

    orchestrator.register_action(
        "failing",
        failing_handler,
    )

    request = orchestrator.create_request(
        action_type="failing",
        source_intent="test",
        confidence=0.95,
        requires_confirmation=False,
    )

    result = orchestrator.execute(
        request.action_id
    )

    assert result.success is False

    assert result.status == (
        ActionStatus.FAILED
    )


def test_intent_bridge():

    intent_engine = (
        AUREXIntentEngine()
    )

    intent = intent_engine.infer(
        gestures=[
            {
                "gesture": "air_draw",
                "confidence": 0.95,
            }
        ]
    )

    orchestrator = (
        AUREXActionOrchestrator()
    )

    request = orchestrator.from_intent(
        intent
    )

    assert request.action_type == (
        "air_canvas"
    )

    assert request.source_intent == (
        "air_draw"
    )

    assert request.confidence > 0.0


def test_emergency_requires_confirmation():

    orchestrator = (
        AUREXActionOrchestrator()
    )

    request = orchestrator.create_request(
        action_type="emergency_workflow",
        source_intent="emergency",
        confidence=0.99,
        requires_confirmation=False,
    )

    assert request.risk == (
        ActionRisk.CRITICAL
    )

    assert request.requires_confirmation


def test_serialization():

    orchestrator = (
        AUREXActionOrchestrator()
    )

    request = orchestrator.create_request(
        action_type="display",
        source_intent="observe",
        confidence=0.90,
    )

    data = request.to_dict()

    assert isinstance(data, dict)

    assert "action_id" in data

    assert "risk" in data

    assert "status" in data


if __name__ == "__main__":

    test_orchestrator_status()
    test_action_registration()
    test_risk_classification()
    test_low_confidence_rejected()
    test_confirmation_gate()
    test_confirmation_allows_execution()
    test_rejected_action_cannot_execute()
    test_missing_adapter_fails_cleanly()
    test_handler_exception()
    test_intent_bridge()
    test_emergency_requires_confirmation()
    test_serialization()

    print("=" * 78)
    print("AUREX PHASE 20 ACTION ORCHESTRATION TESTS")
    print("=" * 78)
    print("All tests passed.")
    print("=" * 78)