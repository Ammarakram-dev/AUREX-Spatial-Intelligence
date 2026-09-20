from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class MemoryEventType(str, Enum):
    UNKNOWN = "unknown"
    PERSON_ENTERED = "person_entered"
    PERSON_LEFT = "person_left"
    OBJECT_APPEARED = "object_appeared"
    OBJECT_DISAPPEARED = "object_disappeared"
    STATE_CHANGED = "state_changed"
    HAZARD_STARTED = "hazard_started"
    HAZARD_CLEARED = "hazard_cleared"
    SECURITY_CHANGED = "security_changed"
    INTENT_CHANGED = "intent_changed"
    BEHAVIOR_CHANGED = "behavior_changed"


@dataclass
class MemoryEvent:
    event_type: MemoryEventType
    description: str
    confidence: float = 0.0
    timestamp: float = 0.0
    entity_id: str | None = None
    previous_value: Any = None
    current_value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.confidence = max(
            0.0,
            min(1.0, float(self.confidence)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "description": self.description,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "entity_id": self.entity_id,
            "previous_value": self.previous_value,
            "current_value": self.current_value,
            "metadata": dict(self.metadata),
        }


@dataclass
class TemporalMemoryState:
    frame_index: int = 0
    timestamp: float = 0.0

    people_ids: List[str] = field(default_factory=list)
    object_labels: List[str] = field(default_factory=list)

    environment_state: str = "unknown"
    security_state: str = "unknown"
    security_level: str = "low"

    hazard_count: int = 0
    behavior_anomaly_count: int = 0

    voice_intent: str = "unknown"
    multimodal_intent: str = "unknown"

    events: List[MemoryEvent] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_index": self.frame_index,
            "timestamp": self.timestamp,
            "people_ids": list(self.people_ids),
            "object_labels": list(self.object_labels),
            "environment_state": self.environment_state,
            "security_state": self.security_state,
            "security_level": self.security_level,
            "hazard_count": self.hazard_count,
            "behavior_anomaly_count": self.behavior_anomaly_count,
            "voice_intent": self.voice_intent,
            "multimodal_intent": self.multimodal_intent,
            "events": [event.to_dict() for event in self.events],
            "metadata": dict(self.metadata),
        }