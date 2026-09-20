from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List
import time


class SituationType(str, Enum):
    UNKNOWN = "unknown"
    IDLE = "idle"
    NORMAL_ACTIVITY = "normal_activity"
    PERSON_PRESENT = "person_present"
    ACTIVE_INTERACTION = "active_interaction"
    ELEVATED_ACTIVITY = "elevated_activity"
    SECURITY_EVENT = "security_event"
    HAZARD_EVENT = "hazard_event"
    EMERGENCY_CONTEXT = "emergency_context"
    TRANSITION = "transition"


class ActivityLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ContextPriority(str, Enum):
    NORMAL = "normal"
    ATTENTION = "attention"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class SituationEvidence:
    source: str
    value: Any
    confidence: float = 0.0
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.confidence = max(0.0, min(1.0, float(self.confidence)))
        self.weight = max(0.0, float(self.weight))

    @property
    def score(self) -> float:
        return self.confidence * self.weight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "value": self.value,
            "confidence": self.confidence,
            "weight": self.weight,
            "score": self.score,
            "metadata": self.metadata,
        }


@dataclass
class PersonalContext:
    situation: SituationType = SituationType.UNKNOWN
    activity_level: ActivityLevel = ActivityLevel.NONE
    priority: ContextPriority = ContextPriority.NORMAL

    confidence: float = 0.0

    people_count: int = 0
    object_count: int = 0

    moving_people: int = 0
    stationary_people: int = 0
    approaching_people: int = 0
    separating_people: int = 0

    security_state: str = "unknown"
    security_level: str = "unknown"

    primary_intent: str = "unknown"
    multimodal_intent: str = "unknown"

    hazard_count: int = 0
    highest_hazard: str = "none"
    highest_hazard_severity: str = "normal"

    behavior_anomaly_score: float = 0.0

    affect_state: str = "unknown"
    prediction_level: str = "normal"
    prediction_type: str = "unknown"

    environment_state: str = "unknown"

    zone_counts: Dict[str, int] = field(default_factory=dict)

    evidence: List[SituationEvidence] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)

    recommended_mode: str = "monitor"
    timestamp: float = field(default_factory=time.time)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_evidence(self, evidence: SituationEvidence) -> None:
        self.evidence.append(evidence)

    def calculate_confidence(self) -> float:
        if not self.evidence:
            self.confidence = 0.0
            return self.confidence

        total_weight = sum(item.weight for item in self.evidence)

        if total_weight <= 0:
            self.confidence = 0.0
            return self.confidence

        self.confidence = min(
            1.0,
            sum(item.score for item in self.evidence) / total_weight,
        )

        return self.confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "situation": self.situation.value,
            "activity_level": self.activity_level.value,
            "priority": self.priority.value,
            "confidence": self.confidence,
            "people_count": self.people_count,
            "object_count": self.object_count,
            "moving_people": self.moving_people,
            "stationary_people": self.stationary_people,
            "approaching_people": self.approaching_people,
            "separating_people": self.separating_people,
            "security_state": self.security_state,
            "security_level": self.security_level,
            "primary_intent": self.primary_intent,
            "multimodal_intent": self.multimodal_intent,
            "hazard_count": self.hazard_count,
            "highest_hazard": self.highest_hazard,
            "highest_hazard_severity": self.highest_hazard_severity,
            "behavior_anomaly_score": self.behavior_anomaly_score,
            "affect_state": self.affect_state,
            "prediction_level": self.prediction_level,
            "prediction_type": self.prediction_type,
            "environment_state": self.environment_state,
            "zone_counts": self.zone_counts,
            "evidence": [item.to_dict() for item in self.evidence],
            "reasons": self.reasons,
            "recommended_mode": self.recommended_mode,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    def status(self) -> Dict[str, Any]:
        return {
            "situation": self.situation.value,
            "activity_level": self.activity_level.value,
            "priority": self.priority.value,
            "confidence": round(self.confidence, 3),
            "people_count": self.people_count,
            "hazard_count": self.hazard_count,
            "security_state": self.security_state,
            "primary_intent": self.primary_intent,
            "recommended_mode": self.recommended_mode,
        }


@dataclass
class UnifiedWorldState:
    timestamp: float = field(default_factory=time.time)

    people_count: int = 0
    object_count: int = 0

    context_type: str = "unknown"
    security_state: str = "unknown"
    security_level: str = "unknown"

    primary_intent: str = "unknown"
    multimodal_intent: str = "unknown"

    hazard_count: int = 0
    highest_hazard: str = "none"
    highest_hazard_severity: str = "normal"

    behavior_anomaly_score: float = 0.0

    affect_state: str = "unknown"

    prediction_type: str = "unknown"
    prediction_level: str = "normal"

    environment_state: str = "unknown"

    situation: SituationType = SituationType.UNKNOWN
    activity_level: ActivityLevel = ActivityLevel.NONE
    priority: ContextPriority = ContextPriority.NORMAL

    confidence: float = 0.0
    recommended_mode: str = "monitor"

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "people_count": self.people_count,
            "object_count": self.object_count,
            "context_type": self.context_type,
            "security_state": self.security_state,
            "security_level": self.security_level,
            "primary_intent": self.primary_intent,
            "multimodal_intent": self.multimodal_intent,
            "hazard_count": self.hazard_count,
            "highest_hazard": self.highest_hazard,
            "highest_hazard_severity": self.highest_hazard_severity,
            "behavior_anomaly_score": self.behavior_anomaly_score,
            "affect_state": self.affect_state,
            "prediction_type": self.prediction_type,
            "prediction_level": self.prediction_level,
            "environment_state": self.environment_state,
            "situation": self.situation.value,
            "activity_level": self.activity_level.value,
            "priority": self.priority.value,
            "confidence": self.confidence,
            "recommended_mode": self.recommended_mode,
            "metadata": self.metadata,
        }