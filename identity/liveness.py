"""
AUREX Spatial Intelligence
Adaptive Liveness Evaluator

Phase 22
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from identity.identity_state import (
    LivenessState,
)


@dataclass
class LivenessEvidence:
    name: str
    passed: bool
    confidence: float
    weight: float = 1.0
    metadata: Optional[
        Dict[str, Any]
    ] = None

    def __post_init__(self) -> None:
        self.confidence = max(
            0.0,
            min(1.0, float(self.confidence)),
        )

        self.weight = max(
            0.0,
            float(self.weight),
        )

        if self.metadata is None:
            self.metadata = {}

    def score(self) -> float:
        if not self.passed:
            return 0.0

        return (
            self.confidence
            * self.weight
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "confidence": self.confidence,
            "weight": self.weight,
            "score": self.score(),
            "metadata": dict(
                self.metadata or {}
            ),
        }


class AUREXLivenessEvaluator:
    """
    Multisignal liveness evaluator.

    Signals can include:

    - blink
    - head movement
    - facial motion
    - temporal consistency
    - depth consistency
    - challenge response

    This class does not claim biometric-grade
    anti-spoofing by itself. It produces evidence
    for the identity decision layer.
    """

    def __init__(
        self,
        live_threshold: float = 0.70,
        spoof_threshold: float = 0.30,
    ) -> None:

        self.live_threshold = float(
            live_threshold
        )

        self.spoof_threshold = float(
            spoof_threshold
        )

        self.last_score = 0.0
        self.last_state = (
            LivenessState.UNKNOWN
        )

    def evaluate(
        self,
        evidence: list[
            LivenessEvidence
        ],
    ) -> LivenessState:

        if not evidence:

            self.last_score = 0.0

            self.last_state = (
                LivenessState.UNKNOWN
            )

            return self.last_state

        total_weight = sum(
            item.weight
            for item in evidence
        )

        if total_weight <= 0.0:

            self.last_score = 0.0

            self.last_state = (
                LivenessState.UNKNOWN
            )

            return self.last_state

        passed_weight = sum(
            item.score()
            for item in evidence
        )

        self.last_score = max(
            0.0,
            min(
                1.0,
                passed_weight
                / total_weight,
            ),
        )

        failed = [
            item
            for item in evidence
            if not item.passed
            and item.confidence
            >= self.live_threshold
        ]

        if (
            self.last_score
            >= self.live_threshold
        ):

            self.last_state = (
                LivenessState.LIVE
            )

        elif (
            failed
            and self.last_score
            <= self.spoof_threshold
        ):

            self.last_state = (
                LivenessState.POSSIBLE_SPOOF
            )

        else:

            self.last_state = (
                LivenessState.UNKNOWN
            )

        return self.last_state

    def evaluate_values(
        self,
        blink: Optional[bool] = None,
        head_movement: Optional[bool] = None,
        facial_motion: Optional[bool] = None,
        temporal_consistency: Optional[bool] = None,
        depth_consistency: Optional[bool] = None,
        challenge_response: Optional[bool] = None,
        confidence: float = 1.0,
    ) -> LivenessState:

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

        evidence = []

        for name, value, weight in values:

            if value is None:
                continue

            evidence.append(
                LivenessEvidence(
                    name=name,
                    passed=bool(value),
                    confidence=confidence,
                    weight=weight,
                )
            )

        return self.evaluate(
            evidence
        )

    def status(self) -> Dict[str, Any]:

        return {
            "engine": (
                "AUREXLivenessEvaluator"
            ),
            "live_threshold": (
                self.live_threshold
            ),
            "spoof_threshold": (
                self.spoof_threshold
            ),
            "last_score": (
                self.last_score
            ),
            "last_state": (
                self.last_state.value
            ),
            "status": "ready",
        }