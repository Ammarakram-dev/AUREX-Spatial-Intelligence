from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class VoiceIntent(str, Enum):
    UNKNOWN = "unknown"
    OBSERVE = "observe"
    SHOW = "show"
    HIDE = "hide"
    CLEAR = "clear"
    SELECT = "select"
    DRAW = "draw"
    STOP = "stop"
    HELP = "request_help"
    EMERGENCY = "emergency"
    STATUS = "status"
    LOCK = "lock"
    UNLOCK = "unlock"


@dataclass
class VoiceCommand:
    text: str
    intent: VoiceIntent
    confidence: float
    entities: Dict[str, Any] = field(
        default_factory=dict
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "intent": self.intent.value,
            "confidence": self.confidence,
            "entities": dict(self.entities),
            "metadata": dict(self.metadata),
        }