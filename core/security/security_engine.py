"""
AUREX Spatial Intelligence
Security Intelligence Engine

Phase 21
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from core.security.security_signal import (
    SecuritySignal,
    SecuritySignalType,
)

from core.security.security_state import (
    SecurityDecision,
    SecurityLevel,
    SecurityState,
)


class AUREXSecurityEngine:
    """
    Multisignal security reasoning engine.

    This engine does not directly unlock devices,
    send emergency messages, or perform physical
    security operations.

    It produces a structured security decision that
    can later be passed through the AUREX action gate.
    """

    def __init__(
        self,
        verification_threshold: float = 0.70,
        trust_threshold: float = 0.85,
    ) -> None:

        self.verification_threshold = float(
            verification_threshold
        )

        self.trust_threshold = float(
            trust_threshold
        )

        self.history: List[
            SecurityDecision
        ] = []

        self.last_decision: Optional[
            SecurityDecision
        ] = None

    def analyze(
        self,
        signals: Optional[
            Iterable[SecuritySignal]
        ] = None,
    ) -> SecurityDecision:

        signal_list = list(
            signals or []
        )

        if not signal_list:

            decision = SecurityDecision(
                state=SecurityState.UNKNOWN,
                level=SecurityLevel.LOW,
                confidence=0.0,
                authorized=False,
                requires_verification=True,
                reasons=[
                    "No security signals available."
                ],
            )

            return self._record(
                decision
            )

        presence = self._get_best(
            signal_list,
            SecuritySignalType.PRESENCE,
        )

        liveness = self._get_best(
            signal_list,
            SecuritySignalType.LIVENESS,
        )

        identity = self._get_best(
            signal_list,
            SecuritySignalType.IDENTITY,
        )

        behavior = self._get_best(
            signal_list,
            SecuritySignalType.BEHAVIOR,
        )

        face = self._get_best(
            signal_list,
            SecuritySignalType.FACE_DETECTED,
        )

        reasons: List[str] = []

        if presence is not None:
            if bool(presence.value):
                reasons.append(
                    "Physical presence detected."
                )
            else:
                reasons.append(
                    "No physical presence detected."
                )

        if face is not None and bool(face.value):
            reasons.append(
                "Face presence signal detected."
            )

        if liveness is not None:
            if bool(liveness.value):
                reasons.append(
                    "Liveness signal passed."
                )
            else:
                reasons.append(
                    "Liveness signal failed."
                )

        if identity is not None:
            if bool(identity.value):
                reasons.append(
                    "Identity signal matched."
                )
            else:
                reasons.append(
                    "Identity signal did not match."
                )

        if behavior is not None:
            reasons.append(
                "Behavioral security signal received."
            )

        presence_ok = (
            presence is not None
            and bool(presence.value)
            and presence.confidence
            >= self.verification_threshold
        )

        liveness_ok = (
            liveness is not None
            and bool(liveness.value)
            and liveness.confidence
            >= self.verification_threshold
        )

        identity_ok = (
            identity is not None
            and bool(identity.value)
            and identity.confidence
            >= self.verification_threshold
        )

        suspicious_behavior = (
            behavior is not None
            and (
                behavior.value is False
                or behavior.value == "suspicious"
            )
            and behavior.confidence
            >= self.verification_threshold
        )

        if not presence_ok:

            decision = SecurityDecision(
                state=SecurityState.NO_PRESENCE,
                level=SecurityLevel.LOW,
                confidence=(
                    presence.confidence
                    if presence is not None
                    else 0.0
                ),
                authorized=False,
                requires_verification=False,
                reasons=reasons,
            )

            return self._record(
                decision
            )

        if suspicious_behavior:

            decision = SecurityDecision(
                state=SecurityState.SUSPICIOUS,
                level=SecurityLevel.HIGH,
                confidence=behavior.confidence,
                authorized=False,
                requires_verification=True,
                reasons=reasons,
            )

            return self._record(
                decision
            )

        if not liveness_ok:

            decision = SecurityDecision(
                state=SecurityState.VERIFYING,
                level=SecurityLevel.MEDIUM,
                confidence=self._combined_confidence(
                    presence,
                    face,
                ),
                authorized=False,
                requires_verification=True,
                reasons=reasons,
            )

            return self._record(
                decision
            )

        if identity is not None and not identity_ok:

            decision = SecurityDecision(
                state=SecurityState.DENIED,
                level=SecurityLevel.HIGH,
                confidence=identity.confidence,
                authorized=False,
                requires_verification=True,
                reasons=reasons,
            )

            return self._record(
                decision
            )

        if identity_ok:

            confidence = self._combined_confidence(
                presence,
                liveness,
                identity,
                face,
            )

            if confidence >= self.trust_threshold:

                decision = SecurityDecision(
                    state=SecurityState.TRUSTED,
                    level=SecurityLevel.LOW,
                    confidence=confidence,
                    authorized=True,
                    requires_verification=False,
                    reasons=reasons,
                )

                return self._record(
                    decision
                )

        decision = SecurityDecision(
            state=SecurityState.VERIFYING,
            level=SecurityLevel.MEDIUM,
            confidence=self._combined_confidence(
                presence,
                liveness,
                identity,
                face,
            ),
            authorized=False,
            requires_verification=True,
            reasons=reasons,
        )

        return self._record(
            decision
        )

    def analyze_values(
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
    ) -> SecurityDecision:

        signals: List[
            SecuritySignal
        ] = []

        if presence is not None:
            signals.append(
                SecuritySignal(
                    SecuritySignalType.PRESENCE,
                    presence,
                    presence_confidence,
                    "direct",
                )
            )

        if liveness is not None:
            signals.append(
                SecuritySignal(
                    SecuritySignalType.LIVENESS,
                    liveness,
                    liveness_confidence,
                    "direct",
                )
            )

        if identity is not None:
            signals.append(
                SecuritySignal(
                    SecuritySignalType.IDENTITY,
                    identity,
                    identity_confidence,
                    "direct",
                )
            )

        if face_detected is not None:
            signals.append(
                SecuritySignal(
                    SecuritySignalType.FACE_DETECTED,
                    face_detected,
                    face_confidence,
                    "direct",
                )
            )

        if behavior is not None:
            signals.append(
                SecuritySignal(
                    SecuritySignalType.BEHAVIOR,
                    behavior,
                    behavior_confidence,
                    "direct",
                )
            )

        return self.analyze(
            signals
        )

    def _get_best(
        self,
        signals: List[SecuritySignal],
        signal_type: SecuritySignalType,
    ) -> Optional[SecuritySignal]:

        matching = [
            signal
            for signal in signals
            if signal.signal_type
            == signal_type
        ]

        if not matching:
            return None

        return max(
            matching,
            key=lambda signal: signal.confidence,
        )

    def _combined_confidence(
        self,
        *signals: Optional[SecuritySignal],
    ) -> float:

        valid = [
            signal.confidence
            for signal in signals
            if signal is not None
        ]

        if not valid:
            return 0.0

        return sum(valid) / len(valid)

    def _record(
        self,
        decision: SecurityDecision,
    ) -> SecurityDecision:

        self.last_decision = decision

        self.history.append(
            decision
        )

        return decision

    def status(self) -> Dict[str, Any]:

        return {
            "engine": "AUREXSecurityEngine",
            "verification_threshold": (
                self.verification_threshold
            ),
            "trust_threshold": (
                self.trust_threshold
            ),
            "history_count": len(
                self.history
            ),
            "last_state": (
                self.last_decision.state.value
                if self.last_decision is not None
                else None
            ),
            "status": "ready",
        }