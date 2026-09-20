"""
AUREX Spatial Intelligence
Real Eye Liveness Intelligence

Phase 26
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class EyeState(str, Enum):
    UNKNOWN = "unknown"
    OPEN = "open"
    CLOSED = "closed"


class EyeEvidenceType(str, Enum):
    BLINK = "blink"
    EYE_STATE = "eye_state"
    HEAD_MOVEMENT = "head_movement"
    FACIAL_MOTION = "facial_motion"
    TEMPORAL_CONSISTENCY = "temporal_consistency"


@dataclass
class EyeEvidence:
    evidence_type: EyeEvidenceType
    value: bool
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "evidence_type": self.evidence_type.value,
            "value": self.value,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }


@dataclass
class EyeLivenessResult:
    state: EyeState
    confidence: float
    live: bool
    blink_detected: bool
    head_movement_detected: bool
    facial_motion_detected: bool
    temporal_consistency: bool
    evidence: List[EyeEvidence] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "state": self.state.value,
            "confidence": self.confidence,
            "live": self.live,
            "blink_detected": self.blink_detected,
            "head_movement_detected": self.head_movement_detected,
            "facial_motion_detected": self.facial_motion_detected,
            "temporal_consistency": self.temporal_consistency,
            "evidence": [item.to_dict() for item in self.evidence],
            "reasons": list(self.reasons),
        }


class AUREXEyeLiveness:

    def __init__(
        self,
        live_threshold: float = 0.70,
        minimum_signals: int = 2,
    ):
        self.live_threshold = live_threshold
        self.minimum_signals = minimum_signals

        self.previous_eye_state = EyeState.UNKNOWN

        self.blink_detected = False
        self.head_movement_detected = False
        self.facial_motion_detected = False

        self.history: List[EyeState] = []

    def update(
        self,
        eye_state,
        head_movement: bool = False,
        facial_motion: bool = False,
        confidence: float = 1.0,
    ) -> EyeLivenessResult:

        if not isinstance(eye_state, EyeState):
            eye_state = EyeState(str(eye_state))

        confidence = max(
            0.0,
            min(1.0, float(confidence)),
        )

        # Real blink transition.
        if (
            self.previous_eye_state == EyeState.OPEN
            and eye_state == EyeState.CLOSED
        ):
            self.blink_detected = True

        if (
            self.previous_eye_state == EyeState.CLOSED
            and eye_state == EyeState.OPEN
        ):
            self.blink_detected = True

        if head_movement:
            self.head_movement_detected = True

        if facial_motion:
            self.facial_motion_detected = True

        self.history.append(eye_state)

        if len(self.history) > 30:
            self.history.pop(0)

        self.previous_eye_state = eye_state

        evidence = []

        if self.blink_detected:
            evidence.append(
                EyeEvidence(
                    EyeEvidenceType.BLINK,
                    True,
                    confidence,
                )
            )

        if eye_state != EyeState.UNKNOWN:
            evidence.append(
                EyeEvidence(
                    EyeEvidenceType.EYE_STATE,
                    True,
                    confidence,
                )
            )

        if self.head_movement_detected:
            evidence.append(
                EyeEvidence(
                    EyeEvidenceType.HEAD_MOVEMENT,
                    True,
                    confidence,
                )
            )

        if self.facial_motion_detected:
            evidence.append(
                EyeEvidence(
                    EyeEvidenceType.FACIAL_MOTION,
                    True,
                    confidence,
                )
            )

        temporal_consistency = len(self.history) >= 5

        if temporal_consistency:
            evidence.append(
                EyeEvidence(
                    EyeEvidenceType.TEMPORAL_CONSISTENCY,
                    True,
                    confidence,
                )
            )

        signal_count = sum(
            [
                self.blink_detected,
                self.head_movement_detected,
                self.facial_motion_detected,
                temporal_consistency,
            ]
        )

        live = signal_count >= self.minimum_signals

        if live:
            signal_confidences = [
                item.confidence
                for item in evidence
                if item.value
            ]

            result_confidence = (
                sum(signal_confidences) /
                len(signal_confidences)
                if signal_confidences
                else 0.0
            )

            reasons = [
                "Multiple temporal facial signals detected."
            ]

            if self.blink_detected:
                reasons.append(
                    "Real blink transition detected."
                )

        else:
            result_confidence = confidence * 0.45

            reasons = [
                "Waiting for additional real liveness signals."
            ]

        return EyeLivenessResult(
            state=eye_state,
            confidence=result_confidence,
            live=live and result_confidence >= self.live_threshold,
            blink_detected=self.blink_detected,
            head_movement_detected=self.head_movement_detected,
            facial_motion_detected=self.facial_motion_detected,
            temporal_consistency=temporal_consistency,
            evidence=evidence,
            reasons=reasons,
        )

    def reset(self):
        self.previous_eye_state = EyeState.UNKNOWN
        self.blink_detected = False
        self.head_movement_detected = False
        self.facial_motion_detected = False
        self.history.clear()

    def status(self):
        return {
            "live_threshold": self.live_threshold,
            "minimum_signals": self.minimum_signals,
            "blink_detected": self.blink_detected,
            "head_movement_detected": self.head_movement_detected,
            "facial_motion_detected": self.facial_motion_detected,
            "history_length": len(self.history),
        }