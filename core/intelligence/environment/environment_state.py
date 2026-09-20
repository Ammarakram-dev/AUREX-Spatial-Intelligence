from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class EnvironmentState(str, Enum):
    UNKNOWN = "unknown"
    CALM = "calm"
    PERSON_PRESENT = "person_present"
    PEOPLE_ACTIVE = "people_active"
    MULTI_PERSON = "multi_person"
    OBJECT_INTERACTION = "object_interaction"
    SECURITY_VERIFICATION = "security_verification"
    POTENTIAL_HAZARD = "potential_hazard"
    EMERGENCY_CONTEXT = "emergency_context"


@dataclass
class EnvironmentEvidence:
    source: str
    description: str
    confidence: float = 0.0
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.confidence = max(0.0, min(1.0, float(self.confidence)))
        self.weight = max(0.0, float(self.weight))

    def score(self) -> float:
        return self.confidence * self.weight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "description": self.description,
            "confidence": self.confidence,
            "weight": self.weight,
            "metadata": self.metadata,
        }


@dataclass
class AUREXEnvironmentState:
    state: EnvironmentState = EnvironmentState.UNKNOWN
    confidence: float = 0.0

    people_count: int = 0
    object_count: int = 0

    moving_people: int = 0
    stationary_people: int = 0
    seated_people: int = 0
    lying_people: int = 0

    relationship_count: int = 0
    behavior_anomaly_count: int = 0
    hazard_count: int = 0

    security_state: str = "unknown"
    security_level: str = "low"

    voice_intent: str = "unknown"
    multimodal_intent: str = "unknown"

    visible_affect: str = "unknown"

    evidence: List[EnvironmentEvidence] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_evidence(
        self,
        source: str,
        description: str,
        confidence: float,
        weight: float = 1.0,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        self.evidence.append(
            EnvironmentEvidence(
                source=source,
                description=description,
                confidence=confidence,
                weight=weight,
                metadata=metadata or {},
            )
        )

    def calculate_confidence(self) -> float:
        if not self.evidence:
            return max(0.0, min(1.0, self.confidence))

        total_weight = sum(item.weight for item in self.evidence)

        if total_weight <= 0:
            return 0.0

        weighted_score = sum(item.score() for item in self.evidence)

        support_bonus = min(0.15, max(0, len(self.evidence) - 1) * 0.025)

        self.confidence = min(
            1.0,
            (weighted_score / total_weight) + support_bonus,
        )

        return self.confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "confidence": self.confidence,
            "people_count": self.people_count,
            "object_count": self.object_count,
            "moving_people": self.moving_people,
            "stationary_people": self.stationary_people,
            "seated_people": self.seated_people,
            "lying_people": self.lying_people,
            "relationship_count": self.relationship_count,
            "behavior_anomaly_count": self.behavior_anomaly_count,
            "hazard_count": self.hazard_count,
            "security_state": self.security_state,
            "security_level": self.security_level,
            "voice_intent": self.voice_intent,
            "multimodal_intent": self.multimodal_intent,
            "visible_affect": self.visible_affect,
            "evidence": [item.to_dict() for item in self.evidence],
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }

    def status(self) -> Dict[str, Any]:
        return self.to_dict()