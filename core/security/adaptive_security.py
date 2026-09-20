"""
AUREX Spatial Intelligence
Adaptive Multi-Signal Security
Phase 24
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .security_engine import AUREXSecurityEngine
from .security_state import (
    SecurityDecision,
    SecurityState,
)


@dataclass
class AdaptiveSecurityDecision:
    """
    History-aware security decision.
    """

    state: SecurityState
    confidence: float
    authorized: bool
    stable: bool
    consecutive_trusted: int
    consecutive_suspicious: int
    reasons: List[str] = field(
        default_factory=list
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "state": self.state.value,
            "confidence": self.confidence,
            "authorized": self.authorized,
            "stable": self.stable,
            "consecutive_trusted": (
                self.consecutive_trusted
            ),
            "consecutive_suspicious": (
                self.consecutive_suspicious
            ),
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class AUREXAdaptiveSecurity:

    """
    Adds temporal stability and adaptive state reasoning
    around the existing AUREXSecurityEngine.

    This component does not unlock devices or execute
    physical security actions.
    """

    def __init__(
        self,
        engine: Optional[
            AUREXSecurityEngine
        ] = None,
        trusted_stability: int = 3,
        suspicious_stability: int = 2,
        history_limit: int = 30,
    ) -> None:

        self.engine = (
            engine
            or AUREXSecurityEngine()
        )

        self.trusted_stability = max(
            1,
            int(trusted_stability),
        )

        self.suspicious_stability = max(
            1,
            int(suspicious_stability),
        )

        self.history_limit = max(
            1,
            int(history_limit),
        )

        self.decision_history: List[
            SecurityDecision
        ] = []

        self.last_adaptive_decision: Optional[
            AdaptiveSecurityDecision
        ] = None

    def evaluate(
        self,
        presence: Optional[bool] = None,
        liveness: Optional[bool] = None,
        identity: Optional[bool] = None,
        face_detected: Optional[bool] = None,
        behavior: Any = None,
        presence_confidence: float = 1.0,
        liveness_confidence: float = 1.0,
        identity_confidence: float = 1.0,
        face_confidence: float = 1.0,
        behavior_confidence: float = 1.0,
    ) -> AdaptiveSecurityDecision:

        decision = self.engine.analyze_values(
            presence=presence,
            liveness=liveness,
            identity=identity,
            face_detected=face_detected,
            behavior=behavior,
            presence_confidence=(
                presence_confidence
            ),
            liveness_confidence=(
                liveness_confidence
            ),
            identity_confidence=(
                identity_confidence
            ),
            face_confidence=(
                face_confidence
            ),
            behavior_confidence=(
                behavior_confidence
            ),
        )

        self.decision_history.append(
            decision
        )

        if len(self.decision_history) > (
            self.history_limit
        ):

            self.decision_history.pop(0)

        trusted_count = (
            self._consecutive_state_count(
                SecurityState.TRUSTED
            )
        )

        suspicious_count = (
            self._consecutive_state_count(
                SecurityState.SUSPICIOUS
            )
        )

        stable = False
        authorized = False
        final_state = decision.state
        reasons = list(
            decision.reasons
        )

        if decision.state == SecurityState.TRUSTED:

            if trusted_count >= (
                self.trusted_stability
            ):

                stable = True
                authorized = True

                reasons.append(
                    "Trusted state is temporally stable."
                )

            else:

                final_state = (
                    SecurityState.VERIFYING
                )

                authorized = False

                reasons.append(
                    "Trusted evidence is awaiting "
                    "temporal stability."
                )

        elif decision.state == SecurityState.SUSPICIOUS:

            if suspicious_count >= (
                self.suspicious_stability
            ):

                stable = True

                reasons.append(
                    "Suspicious state is temporally stable."
                )

        adaptive = AdaptiveSecurityDecision(
            state=final_state,
            confidence=decision.confidence,
            authorized=authorized,
            stable=stable,
            consecutive_trusted=trusted_count,
            consecutive_suspicious=(
                suspicious_count
            ),
            reasons=reasons,
            metadata={
                "base_state": (
                    decision.state.value
                ),
                "base_authorized": (
                    decision.authorized
                ),
                "history_size": len(
                    self.decision_history
                ),
            },
        )

        self.last_adaptive_decision = (
            adaptive
        )

        return adaptive

    def _consecutive_state_count(
        self,
        state: SecurityState,
    ) -> int:

        count = 0

        for decision in reversed(
            self.decision_history
        ):

            if decision.state != state:
                break

            count += 1

        return count

    def reset(self) -> None:

        self.decision_history.clear()
        self.last_adaptive_decision = None
        self.engine.history.clear()
        self.engine.last_decision = None

    def status(self) -> Dict[str, Any]:

        return {
            "engine": (
                "AUREXAdaptiveSecurity"
            ),
            "trusted_stability": (
                self.trusted_stability
            ),
            "suspicious_stability": (
                self.suspicious_stability
            ),
            "history_limit": (
                self.history_limit
            ),
            "history_size": len(
                self.decision_history
            ),
            "last_state": (
                self.last_adaptive_decision.state.value
                if self.last_adaptive_decision
                is not None
                else None
            ),
            "authorized": (
                self.last_adaptive_decision.authorized
                if self.last_adaptive_decision
                is not None
                else False
            ),
            "status": "ready",
        }