from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class EmotionType(str, Enum):
    UNKNOWN = "unknown"
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"


class AffectConfidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class EmotionEvidence:
    source: str
    value: float
    confidence: float
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "value": round(float(self.value), 4),
            "confidence": round(float(self.confidence), 4),
            "description": self.description,
            "metadata": dict(self.metadata),
        }


@dataclass
class EmotionDecision:
    emotion: EmotionType
    confidence: float
    confidence_level: AffectConfidence
    stability: float
    face_detected: bool
    evidence: list[EmotionEvidence] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def affective_state(self) -> str:
        return self.emotion.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "emotion": self.emotion.value,
            "affective_state": self.affective_state,
            "confidence": round(float(self.confidence), 4),
            "confidence_level": self.confidence_level.value,
            "stability": round(float(self.stability), 4),
            "face_detected": self.face_detected,
            "evidence": [item.to_dict() for item in self.evidence],
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }

    def status(self) -> Dict[str, Any]:
        return self.to_dict()