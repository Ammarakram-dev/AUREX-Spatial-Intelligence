from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class PredictionType(str, Enum):
    UNKNOWN = "unknown"
    STABLE_STATE = "stable_state"
    INCREASING_ACTIVITY = "increasing_activity"
    REPEATED_PATTERN = "repeated_pattern"
    HAZARD_ESCALATION = "hazard_escalation"
    HAZARD_PERSISTENCE = "hazard_persistence"
    BEHAVIOR_ESCALATION = "behavior_escalation"
    ENVIRONMENT_TRANSITION = "environment_transition"


class PredictionLevel(str, Enum):
    NORMAL = "normal"
    LOW = "low"
    WARNING = "warning"
    HIGH = "high"


@dataclass
class PredictionEvidence:
    source: str
    description: str
    confidence: float = 0.0
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.confidence = max(
            0.0,
            min(1.0, float(self.confidence)),
        )

        self.weight = max(
            0.0,
            float(self.weight),
        )

    def score(self) -> float:
        return self.confidence * self.weight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "description": self.description,
            "confidence": self.confidence,
            "weight": self.weight,
            "metadata": dict(self.metadata),
        }


@dataclass
class PredictiveAssessment:
    prediction_type: PredictionType = PredictionType.UNKNOWN
    level: PredictionLevel = PredictionLevel.NORMAL
    confidence: float = 0.0

    description: str = ""

    evidence: List[PredictionEvidence] = field(
        default_factory=list
    )

    reasons: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def add_evidence(
        self,
        source: str,
        description: str,
        confidence: float,
        weight: float = 1.0,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        self.evidence.append(
            PredictionEvidence(
                source=source,
                description=description,
                confidence=confidence,
                weight=weight,
                metadata=metadata or {},
            )
        )

    def calculate_confidence(self) -> float:
        if not self.evidence:
            return self.confidence

        total_weight = sum(
            evidence.weight
            for evidence in self.evidence
        )

        if total_weight <= 0:
            return 0.0

        total_score = sum(
            evidence.score()
            for evidence in self.evidence
        )

        bonus = min(
            0.15,
            max(0, len(self.evidence) - 1) * 0.025,
        )

        self.confidence = min(
            1.0,
            total_score / total_weight + bonus,
        )

        return self.confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_type": self.prediction_type.value,
            "level": self.level.value,
            "confidence": self.confidence,
            "description": self.description,
            "evidence": [
                evidence.to_dict()
                for evidence in self.evidence
            ],
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }

    def status(self) -> Dict[str, Any]:
        return self.to_dict()