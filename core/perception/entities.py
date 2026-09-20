"""
AUREX Spatial Intelligence
Perception Entities

Structured representations of things detected in the
physical environment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BoundingBox:
    """2D normalized bounding box."""

    x: float
    y: float
    width: float
    height: float

    def to_dict(self) -> dict[str, float]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }


@dataclass(slots=True)
class DetectedPerson:
    """Represents a detected human."""

    person_id: str
    confidence: float
    bounding_box: BoundingBox

    posture: str = "unknown"
    movement: str = "unknown"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "person_id": self.person_id,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box.to_dict(),
            "posture": self.posture,
            "movement": self.movement,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class DetectedObject:
    """Represents an environmental object."""

    object_id: str
    label: str
    confidence: float
    bounding_box: BoundingBox

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "label": self.label,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box.to_dict(),
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class GestureSignal:
    """Represents a detected hand/body gesture."""

    gesture: str
    confidence: float

    hand: str = "unknown"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "gesture": self.gesture,
            "confidence": self.confidence,
            "hand": self.hand,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class VisualFrame:
    """
    Represents one processed perception frame.

    The actual image data is intentionally kept outside
    this structure so the core remains lightweight.
    """

    frame_id: str

    width: int
    height: int

    persons: list[DetectedPerson] = field(
        default_factory=list
    )

    objects: list[DetectedObject] = field(
        default_factory=list
    )

    gestures: list[GestureSignal] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def summary(self) -> dict[str, Any]:
        """Return a compact perception summary."""

        return {
            "frame_id": self.frame_id,
            "resolution": [
                self.width,
                self.height,
            ],
            "persons": len(self.persons),
            "objects": len(self.objects),
            "gestures": len(self.gestures),
        }