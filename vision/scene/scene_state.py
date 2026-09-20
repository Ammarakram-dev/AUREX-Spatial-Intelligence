from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class SceneRelationshipType(str, Enum):
    NEAR = "near"
    OVERLAPPING = "overlapping"
    LEFT_OF = "left_of"
    RIGHT_OF = "right_of"
    ABOVE = "above"
    BELOW = "below"
    PERSON_NEAR_OBJECT = "person_near_object"


class SceneChangeType(str, Enum):
    NONE = "none"
    OBJECT_APPEARED = "object_appeared"
    OBJECT_DISAPPEARED = "object_disappeared"
    COUNT_CHANGED = "count_changed"


@dataclass
class SceneRelationship:
    source_id: str
    source_label: str
    relationship: SceneRelationshipType
    target_id: str
    target_label: str
    confidence: float
    distance: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_label": self.source_label,
            "relationship": self.relationship.value,
            "target_id": self.target_id,
            "target_label": self.target_label,
            "confidence": round(
                float(self.confidence),
                4,
            ),
            "distance": round(
                float(self.distance),
                4,
            ),
            "metadata": dict(self.metadata),
        }


@dataclass
class SceneChange:
    change_type: SceneChangeType
    label: str
    count_before: int
    count_after: int
    confidence: float
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "change_type": self.change_type.value,
            "label": self.label,
            "count_before": self.count_before,
            "count_after": self.count_after,
            "confidence": round(
                float(self.confidence),
                4,
            ),
            "metadata": dict(self.metadata),
        }


@dataclass
class SceneSnapshot:
    frame_number: int
    object_count: int
    class_counts: Dict[str, int]
    objects: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    changes: List[Dict[str, Any]]
    scene_confidence: float
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_number": self.frame_number,
            "object_count": self.object_count,
            "class_counts": dict(self.class_counts),
            "objects": list(self.objects),
            "relationships": list(
                self.relationships
            ),
            "changes": list(self.changes),
            "scene_confidence": round(
                float(self.scene_confidence),
                4,
            ),
            "metadata": dict(self.metadata),
        }