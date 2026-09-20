from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.security.security_state import SecurityState, SecurityLevel
from core.actions.action import ActionRequest, ActionRisk


class SafetyDecision:
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REQUIRE_CONFIRMATION = "REQUIRE_CONFIRMATION"


@dataclass
class SafetyGateResult:
    decision: str
    allowed: bool
    requires_confirmation: bool
    reason: str
    security_state: str
    security_level: str
    action_risk: str
    confidence: float
    reasons: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "allowed": self.allowed,
            "requires_confirmation": self.requires_confirmation,
            "reason": self.reason,
            "security_state": self.security_state,
            "security_level": self.security_level,
            "action_risk": self.action_risk,
            "confidence": self.confidence,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class AUREXActionSafetyGate:
    """
    Security-aware safety gate between security intelligence
    and action execution.

    This component NEVER executes actions.

    It only determines whether an ActionRequest:
        - may proceed,
        - must wait for confirmation,
        - or must be blocked.
    """

    def __init__(
        self,
        minimum_confidence: float = 0.70,
        trusted_confidence: float = 0.85,
    ):
        self.minimum_confidence = minimum_confidence
        self.trusted_confidence = trusted_confidence

        self.last_result: Optional[SafetyGateResult] = None
        self.history: List[SafetyGateResult] = []

    def evaluate(
        self,
        action_request: ActionRequest,
        security_state: SecurityState,
        security_level: SecurityLevel,
        security_confidence: float,
        authorized: bool,
    ) -> SafetyGateResult:

        reasons: List[str] = []

        confidence = max(
            0.0,
            min(1.0, float(security_confidence)),
        )

        state_value = (
            security_state.value
            if hasattr(security_state, "value")
            else str(security_state)
        )

        level_value = (
            security_level.value
            if hasattr(security_level, "value")
            else str(security_level)
        )

        risk_value = (
            action_request.risk.value
            if hasattr(action_request.risk, "value")
            else str(action_request.risk)
        )

        # ---------------------------------------------------------
        # HARD BLOCK CONDITIONS
        # ---------------------------------------------------------

        if state_value in {
            SecurityState.NO_PRESENCE.value,
            SecurityState.DENIED.value,
            SecurityState.LOCKED.value,
        }:
            reasons.append(
                f"Security state '{state_value}' does not permit action execution."
            )

            result = SafetyGateResult(
                decision=SafetyDecision.BLOCK,
                allowed=False,
                requires_confirmation=False,
                reason="Security state blocks action.",
                security_state=state_value,
                security_level=level_value,
                action_risk=risk_value,
                confidence=confidence,
                reasons=reasons,
            )

            return self._record(result)

        # Suspicious activity is never silently executed.
        if state_value == SecurityState.SUSPICIOUS.value:
            reasons.append("Security state is suspicious.")

            result = SafetyGateResult(
                decision=SafetyDecision.BLOCK,
                allowed=False,
                requires_confirmation=False,
                reason="Suspicious security state blocks action.",
                security_state=state_value,
                security_level=level_value,
                action_risk=risk_value,
                confidence=confidence,
                reasons=reasons,
            )

            return self._record(result)

        # ---------------------------------------------------------
        # VERIFICATION CONDITIONS
        # ---------------------------------------------------------

        if not authorized:
            reasons.append("Security authorization is not established.")

            result = SafetyGateResult(
                decision=SafetyDecision.BLOCK,
                allowed=False,
                requires_confirmation=False,
                reason="Authorization is required before action execution.",
                security_state=state_value,
                security_level=level_value,
                action_risk=risk_value,
                confidence=confidence,
                reasons=reasons,
            )

            return self._record(result)

        if confidence < self.minimum_confidence:
            reasons.append(
                f"Security confidence {confidence:.2f} is below "
                f"minimum {self.minimum_confidence:.2f}."
            )

            result = SafetyGateResult(
                decision=SafetyDecision.REQUIRE_CONFIRMATION,
                allowed=False,
                requires_confirmation=True,
                reason="Security confidence is insufficient for automatic execution.",
                security_state=state_value,
                security_level=level_value,
                action_risk=risk_value,
                confidence=confidence,
                reasons=reasons,
            )

            return self._record(result)

        # ---------------------------------------------------------
        # HIGH / CRITICAL ACTIONS
        # ---------------------------------------------------------

        if action_request.risk in {
            ActionRisk.HIGH,
            ActionRisk.CRITICAL,
        }:
            if (
                state_value != SecurityState.TRUSTED.value
                or confidence < self.trusted_confidence
            ):
                reasons.append(
                    "High-risk action requires stable trusted security."
                )

                result = SafetyGateResult(
                    decision=SafetyDecision.REQUIRE_CONFIRMATION,
                    allowed=False,
                    requires_confirmation=True,
                    reason="High-risk action requires trusted security and confirmation.",
                    security_state=state_value,
                    security_level=level_value,
                    action_risk=risk_value,
                    confidence=confidence,
                    reasons=reasons,
                )

                return self._record(result)

            reasons.append(
                "High-risk action is permitted only under trusted security."
            )

            result = SafetyGateResult(
                decision=SafetyDecision.REQUIRE_CONFIRMATION,
                allowed=False,
                requires_confirmation=True,
                reason="High-risk action requires explicit confirmation.",
                security_state=state_value,
                security_level=level_value,
                action_risk=risk_value,
                confidence=confidence,
                reasons=reasons,
            )

            return self._record(result)

        # ---------------------------------------------------------
        # MEDIUM-RISK ACTIONS
        # ---------------------------------------------------------

        if action_request.risk == ActionRisk.MEDIUM:
            reasons.append(
                "Medium-risk action requires confirmation."
            )

            result = SafetyGateResult(
                decision=SafetyDecision.REQUIRE_CONFIRMATION,
                allowed=False,
                requires_confirmation=True,
                reason="Medium-risk action requires confirmation.",
                security_state=state_value,
                security_level=level_value,
                action_risk=risk_value,
                confidence=confidence,
                reasons=reasons,
            )

            return self._record(result)

        # ---------------------------------------------------------
        # LOW-RISK ACTION
        # ---------------------------------------------------------

        if state_value == SecurityState.TRUSTED.value:
            reasons.append(
                "Trusted security permits low-risk action."
            )

            result = SafetyGateResult(
                decision=SafetyDecision.ALLOW,
                allowed=True,
                requires_confirmation=False,
                reason="Low-risk action allowed under trusted security.",
                security_state=state_value,
                security_level=level_value,
                action_risk=risk_value,
                confidence=confidence,
                reasons=reasons,
            )

            return self._record(result)

        # Verified but not fully trusted.
        reasons.append(
            "Security is valid but not fully trusted."
        )

        result = SafetyGateResult(
            decision=SafetyDecision.REQUIRE_CONFIRMATION,
            allowed=False,
            requires_confirmation=True,
            reason="Action requires additional confirmation.",
            security_state=state_value,
            security_level=level_value,
            action_risk=risk_value,
            confidence=confidence,
            reasons=reasons,
        )

        return self._record(result)

    def _record(self, result: SafetyGateResult) -> SafetyGateResult:
        self.last_result = result

        self.history.append(result)

        if len(self.history) > 50:
            self.history = self.history[-50:]

        return result

    def reset(self) -> None:
        self.last_result = None
        self.history.clear()

    def status(self) -> Dict[str, Any]:
        return {
            "minimum_confidence": self.minimum_confidence,
            "trusted_confidence": self.trusted_confidence,
            "history_size": len(self.history),
            "last_result": (
                self.last_result.to_dict()
                if self.last_result
                else None
            ),
        }