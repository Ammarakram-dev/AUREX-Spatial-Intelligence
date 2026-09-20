"""
AUREX Spatial Intelligence
Core Event System

The event system provides a common communication layer
between AUREX perception, intelligence, spatial, security,
intent, and emergency subsystems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class AUREXEvent:
    """
    Represents an event generated anywhere inside AUREX.
    """

    event_type: str
    source: str
    data: dict[str, Any] = field(default_factory=dict)

    event_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    confidence: float = 1.0

    priority: int = 0

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the event into a serializable dictionary.
        """

        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "data": self.data,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "priority": self.priority,
        }


def create_event(
    event_type: str,
    source: str,
    data: dict[str, Any] | None = None,
    confidence: float = 1.0,
    priority: int = 0,
) -> AUREXEvent:
    """
    Convenience factory for creating AUREX events.
    """

    return AUREXEvent(
        event_type=event_type,
        source=source,
        data=data or {},
        confidence=max(0.0, min(1.0, confidence)),
        priority=priority,
    )