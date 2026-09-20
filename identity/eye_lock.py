"""
AUREX Spatial Intelligence
EyeLock Security Layer

Phase 26
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from identity.eye_liveness import EyeLivenessResult


class EyeLockState(str, Enum):
    UNKNOWN = "unknown"
    WAITING = "waiting"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    REJECTED = "rejected"


@dataclass
class EyeLockDecision:
    state: EyeLockState
    confidence: float
    verified: bool
    requires_more_evidence: bool
    reasons: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "confidence": self.confidence,
            "verified": self.verified,
            "requires_more_evidence": (
                self.requires_more_evidence
            ),
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class AUREXEyeLock:
    """
    EyeLock combines identity matching with temporal liveness.

    It produces a verification decision only.
    It does not unlock devices or execute actions.
    """

    def __init__(
        self,
        identity_threshold: float = 0.90,
        liveness_threshold: float = 0.70,
    ):
        self.identity_threshold = identity_threshold
        self.liveness_threshold = liveness_threshold

        self.last_decision = None

    def evaluate(
        self,
        identity_matched: bool,
        identity_confidence: float,
        liveness: EyeLivenessResult,
    ) -> EyeLockDecision:

        identity_confidence = max(
            0.0,
            min(1.0, float(identity_confidence)),
        )

        combined = (
            identity_confidence * 0.55
            + liveness.confidence * 0.45
        )

        reasons = []

        if not identity_matched:
            reasons.append("Identity match was not established.")

            decision = EyeLockDecision(
                state=EyeLockState.REJECTED,
                confidence=combined,
                verified=False,
                requires_more_evidence=False,
                reasons=reasons,
            )

            self.last_decision = decision
            return decision

        if not liveness.live:
            reasons.append(
                "Eye/face liveness evidence is insufficient."
            )

            decision = EyeLockDecision(
                state=EyeLockState.VERIFYING,
                confidence=combined,
                verified=False,
                requires_more_evidence=True,
                reasons=reasons,
            )

            self.last_decision = decision
            return decision

        if (
            identity_confidence >= self.identity_threshold
            and liveness.confidence >= self.liveness_threshold
        ):
            reasons.append(
                "Identity and temporal liveness thresholds satisfied."
            )

            decision = EyeLockDecision(
                state=EyeLockState.VERIFIED,
                confidence=combined,
                verified=True,
                requires_more_evidence=False,
                reasons=reasons,
            )

            self.last_decision = decision
            return decision

        reasons.append(
            "Additional verification evidence is required."
        )

        decision = EyeLockDecision(
            state=EyeLockState.VERIFYING,
            confidence=combined,
            verified=False,
            requires_more_evidence=True,
            reasons=reasons,
        )

        self.last_decision = decision
        return decision

    def reset(self) -> None:
        self.last_decision = None

    def status(self) -> Dict[str, Any]:
        return {
            "identity_threshold": self.identity_threshold,
            "liveness_threshold": self.liveness_threshold,
            "last_decision": (
                self.last_decision.to_dict()
                if self.last_decision
                else None
            ),
        }