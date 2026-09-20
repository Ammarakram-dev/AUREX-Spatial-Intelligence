from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class BehaviorPattern(str, Enum):
    UNKNOWN = "unknown"
    STATIONARY = "stationary"
    NORMAL_MOVEMENT = "normal_movement"
    REPEATED_MOVEMENT = "repeated_movement"
    RAPID_MOVEMENT = "rapid_movement"
    DIRECTION_CHANGE = "direction_change"
    APPROACHING = "approaching"
    MOVING_AWAY = "moving_away"
    PROLONGED_INACTIVITY = "prolonged_inactivity"
    BEHAVIOR_CHANGE = "behavior_change"


class AnomalySeverity(str, Enum):
    NORMAL = "normal"
    LOW = "low"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BehaviorObservation:
    person_id: str
    movement_distance: float
    movement_direction: str
    zone: str
    posture: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "person_id": self.person_id,
            "movement_distance": round(
                float(self.movement_distance), 4
            ),
            "movement_direction": self.movement_direction,
            "zone": self.zone,
            "posture": self.posture,
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }


@dataclass
class BehaviorAnomaly:
    person_id: str
    pattern: BehaviorPattern
    severity: AnomalySeverity
    confidence: float
    evidence: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "person_id": self.person_id,
            "pattern": self.pattern.value,
            "severity": self.severity.value,
            "confidence": round(
                float(self.confidence), 4
            ),
            "evidence": list(self.evidence),
            "metadata": dict(self.metadata),
        }


@dataclass
class BehaviorProfile:
    person_id: str
    observation_count: int
    average_movement: float
    maximum_movement: float
    stationary_frames: int
    movement_frames: int
    direction_changes: int
    approach_count: int
    departure_count: int
    dominant_zone: str
    dominant_posture: str
    recent_pattern: BehaviorPattern
    anomaly_score: float
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "person_id": self.person_id,
            "observation_count": self.observation_count,
            "average_movement": round(
                float(self.average_movement), 4
            ),
            "maximum_movement": round(
                float(self.maximum_movement), 4
            ),
            "stationary_frames": self.stationary_frames,
            "movement_frames": self.movement_frames,
            "direction_changes": self.direction_changes,
            "approach_count": self.approach_count,
            "departure_count": self.departure_count,
            "dominant_zone": self.dominant_zone,
            "dominant_posture": self.dominant_posture,
            "recent_pattern": self.recent_pattern.value,
            "anomaly_score": round(
                float(self.anomaly_score), 4
            ),
            "metadata": dict(self.metadata),
        }


@dataclass
class BehaviorAnalysis:
    profiles: List[BehaviorProfile]
    anomalies: List[BehaviorAnomaly]
    global_anomaly_score: float
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profiles": [
                profile.to_dict()
                for profile in self.profiles
            ],
            "anomalies": [
                anomaly.to_dict()
                for anomaly in self.anomalies
            ],
            "global_anomaly_score": round(
                float(self.global_anomaly_score), 4
            ),
            "metadata": dict(self.metadata),
        }