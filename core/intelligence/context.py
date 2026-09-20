"""
AUREX Spatial Intelligence
Context Intelligence Data Model

Phase 18.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ContextType(str, Enum):
    UNKNOWN = "unknown"
    NORMAL = "normal"
    PERSON_PRESENT = "person_present"
    PERSON_MOVING = "person_moving"
    PERSON_STATIONARY = "person_stationary"
    PERSON_SITTING = "person_sitting"
    PERSON_LYING = "person_lying"
    PERSON_APPROACHING = "person_approaching"
    PERSON_MOVING_AWAY = "person_moving_away"
    MULTIPLE_PEOPLE = "multiple_people"
    SPATIAL_INTERACTION = "spatial_interaction"
    POTENTIAL_INCIDENT = "potential_incident"


@dataclass
class ContextEvidence:
    """
    Evidence used to support an inferred context.
    """

    source: str
    value: Any
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "value": self.value,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class AUREXContext:
    """
    Unified environmental context produced by AUREX intelligence.
    """

    context_type: ContextType = ContextType.UNKNOWN

    confidence: float = 0.0

    people_count: int = 0

    active_people: List[str] = field(default_factory=list)

    moving_people: List[str] = field(default_factory=list)

    stationary_people: List[str] = field(default_factory=list)

    seated_people: List[str] = field(default_factory=list)

    lying_people: List[str] = field(default_factory=list)

    approaching_people: List[str] = field(default_factory=list)

    moving_away_people: List[str] = field(default_factory=list)

    relationship_count: int = 0

    zone_counts: Dict[str, int] = field(default_factory=dict)

    evidence: List[ContextEvidence] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_evidence(
        self,
        source: str,
        value: Any,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:

        confidence = max(0.0, min(1.0, float(confidence)))

        self.evidence.append(
            ContextEvidence(
                source=source,
                value=value,
                confidence=confidence,
                metadata=metadata or {},
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_type": self.context_type.value,
            "confidence": self.confidence,
            "people_count": self.people_count,
            "active_people": list(self.active_people),
            "moving_people": list(self.moving_people),
            "stationary_people": list(self.stationary_people),
            "seated_people": list(self.seated_people),
            "lying_people": list(self.lying_people),
            "approaching_people": list(self.approaching_people),
            "moving_away_people": list(self.moving_away_people),
            "relationship_count": self.relationship_count,
            "zone_counts": dict(self.zone_counts),
            "evidence": [
                item.to_dict()
                for item in self.evidence
            ],
            "metadata": dict(self.metadata),
        }

    def status(self) -> Dict[str, Any]:
        return {
            "context_type": self.context_type.value,
            "confidence": self.confidence,
            "people_count": self.people_count,
            "relationship_count": self.relationship_count,
            "evidence_count": len(self.evidence),
        }