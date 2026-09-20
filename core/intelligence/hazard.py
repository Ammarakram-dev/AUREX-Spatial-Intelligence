"""
AUREX Spatial Intelligence
Predictive Hazard Model

Phase 27
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class HazardType(str, Enum):
    NONE = "none"
    FALL_RISK = "fall_risk"
    RAPID_APPROACH = "rapid_approach"
    ABNORMAL_MOVEMENT = "abnormal_movement"
    PROLONGED_LYING = "prolonged_lying"
    SPATIAL_CONFLICT = "spatial_conflict"
    CROWDING = "crowding"
    POTENTIAL_INCIDENT = "potential_incident"


class HazardSeverity(str, Enum):
    NORMAL = "normal"
    LOW = "low"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


class HazardResponse(str, Enum):
    NONE = "none"
    MONITOR = "monitor"
    ALERT = "alert"
    REQUEST_CONFIRMATION = "request_confirmation"
    EMERGENCY_WORKFLOW = "emergency_workflow"


@dataclass
class HazardEvidence:
    source: str
    description: str
    confidence: float
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def score(self) -> float:
        confidence = max(
            0.0,
            min(1.0, float(self.confidence)),
        )

        weight = max(
            0.0,
            float(self.weight),
        )

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
class HazardAssessment:
    hazard_type: HazardType
    severity: HazardSeverity
    confidence: float
    response: HazardResponse
    person_ids: List[str] = field(default_factory=list)
    evidence: List[HazardEvidence] = field(
        default_factory=list
    )
    reasons: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def add_evidence(
        self,
        evidence: HazardEvidence,
    ):
        self.evidence.append(evidence)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hazard_type": self.hazard_type.value,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "response": self.response.value,
            "person_ids": list(self.person_ids),
            "evidence": [
                item.to_dict()
                for item in self.evidence
            ],
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }

    def status(self) -> Dict[str, Any]:
        return {
            "hazard_type": self.hazard_type.value,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "response": self.response.value,
            "evidence_count": len(self.evidence),
            "person_count": len(self.person_ids),
        }