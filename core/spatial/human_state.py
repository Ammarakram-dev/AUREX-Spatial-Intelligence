"""
AUREX Spatial Intelligence
Unified Human Spatial State
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from core.spatial.world_model import SpatialPosition


@dataclass
class HumanSpatialState:
    """
    Unified representation of a person's physical state
    inside the AUREX spatial environment.
    """

    person_id: int

    position: SpatialPosition

    posture: str = "UNKNOWN"
    posture_confidence: float = 0.0

    movement_direction: str = "STATIONARY"
    movement_distance: float = 0.0

    zone: str = "UNKNOWN"

    detection_confidence: float = 0.0

    bounding_box: tuple[int, int, int, int] | None = None

    pose_available: bool = False

    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert the unified state into a serializable dictionary."""

        return {
            "person_id": self.person_id,
            "position": self.position.to_dict(),
            "posture": self.posture,
            "posture_confidence": self.posture_confidence,
            "movement_direction": self.movement_direction,
            "movement_distance": self.movement_distance,
            "zone": self.zone,
            "detection_confidence": self.detection_confidence,
            "bounding_box": self.bounding_box,
            "pose_available": self.pose_available,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class AUREXHumanSpatialFusion:
    """
    Combines tracking, posture and spatial information
    into one HumanSpatialState.
    """

    def build(
        self,
        tracked_person,
        spatial_entity,
        posture_result=None,
        pose_available: bool = False,
    ) -> HumanSpatialState:
        """
        Build a unified HumanSpatialState from existing AUREX modules.
        """

        posture = "UNKNOWN"
        posture_confidence = 0.0

        if posture_result is not None:
            posture = posture_result.state
            posture_confidence = posture_result.confidence

        return HumanSpatialState(
            person_id=tracked_person.person_id,
            position=spatial_entity.position,
            posture=posture,
            posture_confidence=posture_confidence,
            movement_direction=tracked_person.movement_direction,
            movement_distance=tracked_person.movement_distance,
            zone=tracked_person.zone,
            detection_confidence=tracked_person.confidence,
            bounding_box=tracked_person.bbox,
            pose_available=pose_available,
            metadata={
                "entity_id": spatial_entity.entity_id,
                "entity_type": spatial_entity.entity_type,
            },
        )