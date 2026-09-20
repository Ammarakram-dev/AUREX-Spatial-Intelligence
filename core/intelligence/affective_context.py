from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional

from identity.emotion_state import EmotionDecision, EmotionType


@dataclass
class AffectiveContext:
    """
    Combines visible affective state with AUREX environmental context.
    """

    primary_emotion: EmotionType = EmotionType.UNKNOWN
    confidence: float = 0.0
    stability: float = 0.0
    people_count: int = 0
    contextual_state: str = "unknown"
    observations: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_emotion": self.primary_emotion.value,
            "confidence": round(float(self.confidence), 4),
            "stability": round(float(self.stability), 4),
            "people_count": self.people_count,
            "contextual_state": self.contextual_state,
            "observations": list(self.observations),
            "metadata": dict(self.metadata),
        }


class AUREXAffectiveContextEngine:
    """
    Connects emotion estimation with AUREX context signals.
    """

    def combine(
        self,
        emotion: EmotionDecision,
        contextual_state: str = "unknown",
        people_count: int = 1,
        observations: Optional[Iterable[str]] = None,
    ) -> AffectiveContext:
        combined_observations = list(observations or [])

        if emotion.emotion != EmotionType.UNKNOWN:
            combined_observations.append(
                f"Visible affect estimated as {emotion.emotion.value}"
            )

        return AffectiveContext(
            primary_emotion=emotion.emotion,
            confidence=emotion.confidence,
            stability=emotion.stability,
            people_count=max(0, int(people_count)),
            contextual_state=str(contextual_state),
            observations=combined_observations,
            metadata={
                "estimation_type": "visible_facial_affect",
                "emotion_metadata": dict(emotion.metadata),
            },
        )

    def status(self) -> Dict[str, Any]:
        return {
            "module": "affective_context",
            "status": "ready",
        }