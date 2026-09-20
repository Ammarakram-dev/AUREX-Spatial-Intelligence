from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class GroupSecurityState(str, Enum):
    NO_GROUP = "no_group"
    SINGLE_PERSON = "single_person"
    MULTI_PERSON = "multi_person"
    PROXIMITY = "proximity"
    APPROACH_PATTERN = "approach_pattern"
    SEPARATION_PATTERN = "separation_pattern"
    HIGH_DENSITY = "high_density"
    SPATIAL_CONFLICT = "spatial_conflict"
    MONITORING = "monitoring"


class GroupSecurityLevel(str, Enum):
    NORMAL = "normal"
    LOW = "low"
    WARNING = "warning"
    HIGH = "high"


@dataclass
class GroupSecurityEvidence:
    source: str
    description: str
    confidence: float
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def score(self) -> float:
        confidence = max(0.0, min(1.0, self.confidence))
        weight = max(0.0, self.weight)
        return confidence * weight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "description": self.description,
            "confidence": self.confidence,
            "weight": self.weight,
            "score": self.score(),
            "metadata": dict(self.metadata),
        }


@dataclass
class MultiPersonAssessment:
    state: GroupSecurityState
    level: GroupSecurityLevel
    confidence: float
    person_ids: List[str] = field(default_factory=list)
    nearby_pairs: List[Dict[str, Any]] = field(default_factory=list)
    approaching_pairs: List[Dict[str, Any]] = field(default_factory=list)
    separating_pairs: List[Dict[str, Any]] = field(default_factory=list)
    same_zone_pairs: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[GroupSecurityEvidence] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_evidence(self, evidence: GroupSecurityEvidence) -> None:
        self.evidence.append(evidence)

    def calculate_confidence(self) -> float:
        if not self.evidence:
            self.confidence = 0.0
            return self.confidence

        total_weight = sum(
            max(0.0, evidence.weight)
            for evidence in self.evidence
        )

        if total_weight <= 0:
            self.confidence = 0.0
            return self.confidence

        weighted_score = sum(
            evidence.score()
            for evidence in self.evidence
        )

        self.confidence = max(
            0.0,
            min(1.0, weighted_score / total_weight),
        )

        return self.confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "level": self.level.value,
            "confidence": self.confidence,
            "person_ids": list(self.person_ids),
            "nearby_pairs": list(self.nearby_pairs),
            "approaching_pairs": list(self.approaching_pairs),
            "separating_pairs": list(self.separating_pairs),
            "same_zone_pairs": list(self.same_zone_pairs),
            "evidence": [
                item.to_dict()
                for item in self.evidence
            ],
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }

    def status(self) -> Dict[str, Any]:
        return self.to_dict()