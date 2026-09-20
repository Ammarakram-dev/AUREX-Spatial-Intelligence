from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class OverlayType(str, Enum):
    PERSON = "person"
    OBJECT = "object"
    RELATIONSHIP = "relationship"
    CONTEXT = "context"
    HAZARD = "hazard"
    SECURITY = "security"
    INTENT = "intent"


@dataclass
class OverlayAnchor:
    x: float
    y: float
    width: float = 0.0
    height: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }


@dataclass
class RealityOverlay:
    overlay_id: str
    overlay_type: OverlayType
    label: str
    confidence: float
    anchor: OverlayAnchor
    priority: int = 0
    visible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overlay_id": self.overlay_id,
            "overlay_type": self.overlay_type.value,
            "label": self.label,
            "confidence": self.confidence,
            "anchor": self.anchor.to_dict(),
            "priority": self.priority,
            "visible": self.visible,
            "metadata": dict(self.metadata),
        }