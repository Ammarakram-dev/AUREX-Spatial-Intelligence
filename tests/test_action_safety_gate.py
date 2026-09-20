from core.actions.action import (
    ActionRequest,
    ActionRisk,
)

from core.security import (
    AUREXActionSafetyGate,
    SafetyDecision,
    SecurityState,
    SecurityLevel,
)


def make_request(risk):
    return ActionRequest(
        action_id="test-action",
        action_type="display",
        source_intent="observe",
        confidence=0.95,
        risk=risk,
        requires_confirmation=False,
        parameters={},
        reason="Phase 25 test",
    )


def test_low_risk_trusted_security():
    gate = AUREXActionSafetyGate()

    request = make_request(ActionRisk.LOW)

    result = gate.evaluate(
        action_request=request,
        security_state=SecurityState.TRUSTED,
        security_level=SecurityLevel.LOW,
        security_confidence=0.95,
        authorized=True,
    )

    assert result.decision == SafetyDecision.ALLOW
    assert result.allowed is True

    print("Low-risk trusted action: PASS")


def test_high_risk_requires_confirmation():
    gate = AUREXActionSafetyGate()

    request = make_request(ActionRisk.HIGH)

    result = gate.evaluate(
        action_request=request,
        security_state=SecurityState.TRUSTED,
        security_level=SecurityLevel.HIGH,
        security_confidence=0.95,
        authorized=True,
    )

    assert result.decision == SafetyDecision.REQUIRE_CONFIRMATION
    assert result.requires_confirmation is True

    print("High-risk confirmation gate: PASS")


def test_suspicious_blocks_action():
    gate = AUREXActionSafetyGate()

    request = make_request(ActionRisk.LOW)

    result = gate.evaluate(
        action_request=request,
        security_state=SecurityState.SUSPICIOUS,
        security_level=SecurityLevel.HIGH,
        security_confidence=0.95,
        authorized=False,
    )

    assert result.decision == SafetyDecision.BLOCK
    assert result.allowed is False

    print("Suspicious security block: PASS")


def test_denied_blocks_action():
    gate = AUREXActionSafetyGate()

    request = make_request(ActionRisk.MEDIUM)

    result = gate.evaluate(
        action_request=request,
        security_state=SecurityState.DENIED,
        security_level=SecurityLevel.HIGH,
        security_confidence=0.95,
        authorized=False,
    )

    assert result.decision == SafetyDecision.BLOCK
    assert result.allowed is False

    print("Denied security block: PASS")


def test_low_confidence_requires_confirmation():
    gate = AUREXActionSafetyGate()

    request = make_request(ActionRisk.LOW)

    result = gate.evaluate(
        action_request=request,
        security_state=SecurityState.TRUSTED,
        security_level=SecurityLevel.LOW,
        security_confidence=0.50,
        authorized=True,
    )

    assert result.decision == SafetyDecision.REQUIRE_CONFIRMATION
    assert result.requires_confirmation is True

    print("Low-confidence confirmation: PASS")


def test_status():
    gate = AUREXActionSafetyGate()

    request = make_request(ActionRisk.LOW)

    gate.evaluate(
        action_request=request,
        security_state=SecurityState.TRUSTED,
        security_level=SecurityLevel.LOW,
        security_confidence=0.95,
        authorized=True,
    )

    status = gate.status()

    assert status["history_size"] == 1
    assert status["last_result"] is not None

    print("Status reporting: PASS")


if __name__ == "__main__":
    test_low_risk_trusted_security()
    test_high_risk_requires_confirmation()
    test_suspicious_blocks_action()
    test_denied_blocks_action()
    test_low_confidence_requires_confirmation()
    test_status()

    print()
    print("PHASE 25 UNIT TEST: PASS")