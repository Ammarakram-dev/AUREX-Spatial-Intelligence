"""
AUREX Spatial Intelligence
Security Signals

Phase 21
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class SecuritySignalType(str, Enum):
    PRESENCE = "presence"
    FACE_DETECTED = "face_detected"
    LIVENESS = "liveness"
    MOTION = "motion"
    IDENTITY = "identity"
    SPATIAL = "spatial"
    CONTEXT = "context"
    BEHAVIOR = "behavior"


@dataclass
class SecuritySignal:
    signal_type: SecuritySignalType
    value: Any
    confidence: float = 0.0
    source: str = "unknown"
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.confidence = max(
            0.0,
            min(1.0, float(self.confidence)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_type": self.signal_type.value,
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source,
            "metadata": dict(self.metadata),
        }