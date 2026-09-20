from __future__ import annotations

from collections import deque
from typing import Any, Dict, Iterable, Optional

from .emotion_features import AUREXEmotionFeatures
from .emotion_state import (
    AffectConfidence,
    EmotionDecision,
    EmotionEvidence,
    EmotionType,
)


class AUREXEmotionEngine:
    """
    Affective-state estimation engine.

    Combines facial geometry signals with temporal smoothing.
    Results describe observable facial affect and should not be treated
    as certainty about a person's internal emotional state.
    """

    def __init__(
        self,
        history_size: int = 12,
        minimum_confidence: float = 0.45,
    ) -> None:
        self.history_size = max(3, int(history_size))
        self.minimum_confidence = float(minimum_confidence)

        self.features = AUREXEmotionFeatures()
        self.history: deque[EmotionType] = deque(
            maxlen=self.history_size
        )

        self.frame_count = 0

    @staticmethod
    def _clamp(
        value: float,
        minimum: float = 0.0,
        maximum: float = 1.0,
    ) -> float:
        return max(
            minimum,
            min(maximum, float(value)),
        )

    @staticmethod
    def _level(confidence: float) -> AffectConfidence:
        if confidence >= 0.75:
            return AffectConfidence.HIGH

        if confidence >= 0.55:
            return AffectConfidence.MEDIUM

        return AffectConfidence.LOW

    @staticmethod
    def _safe_signal(
        features: Dict[str, float],
        name: str,
        default: float = 0.0,
    ) -> float:
        return float(features.get(name, default))

    def _classify(
        self,
        features: Dict[str, float],
    ) -> tuple[
        EmotionType,
        float,
        list[EmotionEvidence],
        list[str],
    ]:
        if not features:
            return (
                EmotionType.UNKNOWN,
                0.0,
                [],
                ["Facial expression features unavailable"],
            )

        eye = self._safe_signal(
            features,
            "eye_opening",
        )

        mouth_open = self._safe_signal(
            features,
            "mouth_opening",
        )

        mouth_width = self._safe_signal(
            features,
            "mouth_width",
        )

        mouth_curve = self._safe_signal(
            features,
            "mouth_curve",
        )

        brow = self._safe_signal(
            features,
            "brow_height",
        )

        candidates: Dict[EmotionType, float] = {
            EmotionType.NEUTRAL: 0.45,
            EmotionType.HAPPY: 0.0,
            EmotionType.SAD: 0.0,
            EmotionType.ANGRY: 0.0,
            EmotionType.SURPRISED: 0.0,
            EmotionType.FEARFUL: 0.0,
            EmotionType.DISGUSTED: 0.0,
        }

        evidence: list[EmotionEvidence] = []
        reasons: list[str] = []

        # =========================================================
        # SURPRISED
        # Wide eyes + raised brows + open mouth.
        # This is intentionally checked first because these signals
        # can overlap with a generic alert/fear configuration.
        # =========================================================
        if (
            eye >= 0.24
            and brow >= 0.040
            and mouth_open >= 0.085
        ):
            candidates[EmotionType.SURPRISED] = 0.90

            evidence.append(
                EmotionEvidence(
                    source="surprise_geometry",
                    value=0.90,
                    confidence=0.86,
                    description=(
                        "Wide eyes, raised brows and open mouth"
                    ),
                )
            )

            reasons.append(
                "Wide eyes, raised brows and open mouth"
            )

        # =========================================================
        # HAPPY
        # =========================================================
        elif (
            mouth_curve > 0.012
            and mouth_width > 0.28
            and mouth_open < 0.080
        ):
            candidates[EmotionType.HAPPY] = 0.72

            evidence.append(
                EmotionEvidence(
                    source="smile_geometry",
                    value=mouth_curve,
                    confidence=0.72,
                    description=(
                        "Upward mouth-corner geometry"
                    ),
                )
            )

            reasons.append(
                "Upward mouth geometry"
            )

        # =========================================================
        # SAD
        # =========================================================
        elif (
            mouth_curve < -0.010
            and mouth_open < 0.070
        ):
            candidates[EmotionType.SAD] = 0.62

            evidence.append(
                EmotionEvidence(
                    source="sadness_geometry",
                    value=abs(mouth_curve),
                    confidence=0.62,
                    description=(
                        "Downward mouth-corner geometry"
                    ),
                )
            )

            reasons.append(
                "Downward mouth geometry"
            )

        # =========================================================
        # ANGRY
        # =========================================================
        elif (
            eye < 0.19
            and brow < 0.030
            and mouth_open < 0.070
        ):
            candidates[EmotionType.ANGRY] = 0.62

            evidence.append(
                EmotionEvidence(
                    source="compressed_expression",
                    value=1.0 - self._clamp(
                        eye / 0.19
                    ),
                    confidence=0.60,
                    description=(
                        "Reduced eye opening with brow compression"
                    ),
                )
            )

            reasons.append(
                "Compressed eye and brow geometry"
            )

        # =========================================================
        # FEARFUL
        # =========================================================
        elif (
            eye >= 0.24
            and brow >= 0.040
            and mouth_open >= 0.055
        ):
            candidates[EmotionType.FEARFUL] = 0.58

            evidence.append(
                EmotionEvidence(
                    source="alert_expression",
                    value=eye,
                    confidence=0.55,
                    description=(
                        "Wide alert facial configuration"
                    ),
                )
            )

            reasons.append(
                "Wide alert facial configuration"
            )

        # =========================================================
        # DISGUSTED
        # =========================================================
        elif (
            mouth_open < 0.045
            and mouth_width < 0.23
            and brow < 0.032
        ):
            candidates[EmotionType.DISGUSTED] = 0.48

            evidence.append(
                EmotionEvidence(
                    source="compressed_mouth",
                    value=1.0,
                    confidence=0.50,
                    description=(
                        "Compressed mouth configuration"
                    ),
                )
            )

            reasons.append(
                "Compressed mouth configuration"
            )

        # =========================================================
        # NEUTRAL
        # =========================================================
        else:
            candidates[EmotionType.NEUTRAL] = 0.55

            reasons.append(
                "No strong expression pattern detected"
            )

        emotion = max(
            candidates,
            key=candidates.get,
        )

        raw_score = candidates[emotion]

        if emotion == EmotionType.NEUTRAL:
            confidence = self._clamp(
                0.50 + raw_score * 0.35
            )
        else:
            confidence = self._clamp(
                0.45 + raw_score * 0.55
            )

        if confidence < self.minimum_confidence:
            emotion = EmotionType.UNKNOWN

            reasons.append(
                "Expression confidence below threshold"
            )

        return (
            emotion,
            confidence,
            evidence,
            reasons,
        )

    def _temporal_stability(
        self,
        emotion: EmotionType,
    ) -> float:
        if not self.history:
            return 0.0

        matches = sum(
            1
            for item in self.history
            if item == emotion
        )

        return self._clamp(
            matches / len(self.history)
        )

    def analyze(
        self,
        landmarks: Optional[Iterable[Any]] = None,
        face_detected: bool = True,
        external_features: Optional[Dict[str, float]] = None,
    ) -> EmotionDecision:
        self.frame_count += 1

        if not face_detected:
            self.history.clear()

            return EmotionDecision(
                emotion=EmotionType.UNKNOWN,
                confidence=0.0,
                confidence_level=AffectConfidence.LOW,
                stability=0.0,
                face_detected=False,
                reasons=["No face detected"],
            )

        if external_features is not None:
            features = dict(external_features)
        else:
            features = self.features.extract(
                landmarks
            )

        (
            emotion,
            confidence,
            evidence,
            reasons,
        ) = self._classify(features)

        self.history.append(emotion)

        stability = self._temporal_stability(
            emotion
        )

        smoothed_confidence = self._clamp(
            confidence * 0.75
            + stability * 0.25
        )

        return EmotionDecision(
            emotion=emotion,
            confidence=smoothed_confidence,
            confidence_level=self._level(
                smoothed_confidence
            ),
            stability=stability,
            face_detected=True,
            evidence=evidence,
            reasons=reasons,
            metadata={
                "frame_count": self.frame_count,
                "history_size": len(self.history),
                "features": dict(features),
                "estimation_type": (
                    "visible_facial_affect"
                ),
            },
        )

    def reset(self) -> None:
        self.history.clear()
        self.features.reset()
        self.frame_count = 0

    def status(self) -> Dict[str, Any]:
        return {
            "frame_count": self.frame_count,
            "history_size": len(self.history),
            "minimum_confidence": (
                self.minimum_confidence
            ),
        }