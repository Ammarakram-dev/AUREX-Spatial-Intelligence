"""
AUREX Spatial Intelligence
Adaptive Identity Engine

Phase 22
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from identity.identity_state import (
    IdentityDecision,
    IdentityState,
    LivenessState,
)

from identity.liveness import (
    AUREXLivenessEvaluator,
    LivenessEvidence,
)


class AUREXIdentityEngine:
    """
    Adaptive identity reasoning layer.

    Identity is treated as a combination of:

    1. Face presence
    2. Liveness
    3. Identity match evidence
    4. Temporal consistency
    5. Confidence

    No real-world device unlock is performed here.
    """

    def __init__(
        self,
        verification_threshold: float = 0.75,
        trusted_threshold: float = 0.88,
    ) -> None:

        self.verification_threshold = float(
            verification_threshold
        )

        self.trusted_threshold = float(
            trusted_threshold
        )

        self.liveness = (
            AUREXLivenessEvaluator()
        )

        self.last_decision: Optional[
            IdentityDecision
        ] = None

        self.history: list[
            IdentityDecision
        ] = []

    def analyze(
        self,
        face_detected: bool,
        face_confidence: float,
        identity_match: Optional[bool] = None,
        identity_confidence: float = 0.0,
        liveness_evidence: Optional[
            list[LivenessEvidence]
        ] = None,
    ) -> IdentityDecision:

        if not face_detected:

            return self._record(
                IdentityDecision(
                    state=IdentityState.NO_FACE,
                    liveness_state=(
                        LivenessState.NOT_PRESENT
                    ),
                    confidence=(
                        max(
                            0.0,
                            min(
                                1.0,
                                float(
                                    face_confidence
                                ),
                            ),
                        )
                    ),
                    verified=False,
                    requires_more_evidence=False,
                    reasons=[
                        "No face detected."
                    ],
                )
            )

        face_confidence = max(
            0.0,
            min(
                1.0,
                float(face_confidence),
            ),
        )

        if face_confidence < (
            self.verification_threshold
        ):

            return self._record(
                IdentityDecision(
                    state=IdentityState.FACE_PRESENT,
                    liveness_state=(
                        LivenessState.UNKNOWN
                    ),
                    confidence=face_confidence,
                    verified=False,
                    requires_more_evidence=True,
                    reasons=[
                        "Face detection confidence "
                        "is below verification threshold."
                    ],
                )
            )

        liveness_state = (
            self.liveness.evaluate(
                liveness_evidence or []
            )
        )

        if liveness_state == (
            LivenessState.POSSIBLE_SPOOF
        ):

            return self._record(
                IdentityDecision(
                    state=IdentityState.REJECTED,
                    liveness_state=liveness_state,
                    confidence=self.liveness.last_score,
                    verified=False,
                    requires_more_evidence=True,
                    reasons=[
                        "Liveness evidence indicates "
                        "a possible spoof."
                    ],
                )
            )

        if liveness_state != (
            LivenessState.LIVE
        ):

            return self._record(
                IdentityDecision(
                    state=IdentityState.LIVENESS_CHECK,
                    liveness_state=liveness_state,
                    confidence=self.liveness.last_score,
                    verified=False,
                    requires_more_evidence=True,
                    reasons=[
                        "Additional liveness evidence "
                        "is required."
                    ],
                )
            )

        if identity_match is None:

            return self._record(
                IdentityDecision(
                    state=IdentityState.VERIFYING,
                    liveness_state=liveness_state,
                    confidence=self._combined(
                        face_confidence,
                        self.liveness.last_score,
                    ),
                    verified=False,
                    requires_more_evidence=True,
                    reasons=[
                        "Liveness passed but identity "
                        "match evidence is missing."
                    ],
                )
            )

        identity_confidence = max(
            0.0,
            min(
                1.0,
                float(identity_confidence),
            ),
        )

        if not identity_match:

            return self._record(
                IdentityDecision(
                    state=IdentityState.REJECTED,
                    liveness_state=liveness_state,
                    confidence=identity_confidence,
                    verified=False,
                    requires_more_evidence=True,
                    reasons=[
                        "Identity match failed."
                    ],
                )
            )

        combined = self._combined(
            face_confidence,
            self.liveness.last_score,
            identity_confidence,
        )

        if combined >= (
            self.trusted_threshold
        ):

            return self._record(
                IdentityDecision(
                    state=IdentityState.VERIFIED,
                    liveness_state=liveness_state,
                    confidence=combined,
                    verified=True,
                    requires_more_evidence=False,
                    reasons=[
                        "Face, liveness and identity "
                        "signals agree."
                    ],
                )
            )

        return self._record(
            IdentityDecision(
                state=IdentityState.VERIFYING,
                liveness_state=liveness_state,
                confidence=combined,
                verified=False,
                requires_more_evidence=True,
                reasons=[
                    "Identity evidence is below "
                    "trusted threshold."
                ],
            )
        )

    def analyze_values(
        self,
        face_detected: bool,
        face_confidence: float,
        identity_match: Optional[bool] = None,
        identity_confidence: float = 0.0,
        blink: Optional[bool] = None,
        head_movement: Optional[bool] = None,
        facial_motion: Optional[bool] = None,
        temporal_consistency: Optional[bool] = None,
        depth_consistency: Optional[bool] = None,
        challenge_response: Optional[bool] = None,
        liveness_confidence: float = 1.0,
    ) -> IdentityDecision:

        self.liveness.evaluate_values(
            blink=blink,
            head_movement=head_movement,
            facial_motion=facial_motion,
            temporal_consistency=(
                temporal_consistency
            ),
            depth_consistency=(
                depth_consistency
            ),
            challenge_response=(
                challenge_response
            ),
            confidence=liveness_confidence,
        )

        # Reconstruct evidence from supplied values
        # so the identity engine evaluates the same
        # signals in one controlled pipeline.

        evidence = []

        values = [
            (
                "blink",
                blink,
                1.0,
            ),
            (
                "head_movement",
                head_movement,
                1.0,
            ),
            (
                "facial_motion",
                facial_motion,
                1.0,
            ),
            (
                "temporal_consistency",
                temporal_consistency,
                1.2,
            ),
            (
                "depth_consistency",
                depth_consistency,
                1.2,
            ),
            (
                "challenge_response",
                challenge_response,
                1.5,
            ),
        ]

        for name, value, weight in values:

            if value is None:
                continue

            evidence.append(
                LivenessEvidence(
                    name=name,
                    passed=bool(value),
                    confidence=liveness_confidence,
                    weight=weight,
                )
            )

        return self.analyze(
            face_detected=face_detected,
            face_confidence=face_confidence,
            identity_match=identity_match,
            identity_confidence=identity_confidence,
            liveness_evidence=evidence,
        )

    def _combined(
        self,
        *values: float,
    ) -> float:

        valid = [
            max(
                0.0,
                min(1.0, float(value)),
            )
            for value in values
        ]

        if not valid:
            return 0.0

        return sum(valid) / len(valid)

    def _record(
        self,
        decision: IdentityDecision,
    ) -> IdentityDecision:

        self.last_decision = decision

        self.history.append(
            decision
        )

        return decision

    def status(self) -> Dict[str, Any]:

        return {
            "engine": "AUREXIdentityEngine",
            "verification_threshold": (
                self.verification_threshold
            ),
            "trusted_threshold": (
                self.trusted_threshold
            ),
            "history_count": len(
                self.history
            ),
            "last_state": (
                self.last_decision.state.value
                if self.last_decision
                else None
            ),
            "status": "ready",
        }