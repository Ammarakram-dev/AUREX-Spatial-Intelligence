"""
AUREX Spatial Intelligence
Live Perception → Spatial World Bridge
"""

from __future__ import annotations

from core.spatial.world_model import (
    AUREXWorldModel,
    SpatialEntity,
    SpatialPosition,
)
from vision.person_tracker import TrackedPerson


class AUREXSpatialBridge:
    """
    Converts tracked vision entities into
    spatial world entities.
    """

    def __init__(
        self,
        world: AUREXWorldModel | None = None,
    ) -> None:

        self.world = (
            world
            if world is not None
            else AUREXWorldModel()
        )

    def update_people(
        self,
        people: list[TrackedPerson],
        frame_width: int,
        frame_height: int,
    ) -> AUREXWorldModel:

        current_ids = set()

        for person in people:

            entity_id = (
                f"person_{person.person_id:03d}"
            )

            current_ids.add(entity_id)

            center_x, center_y = (
                person.current_center
            )

            x = (
                center_x
                / max(frame_width, 1)
            )

            y = (
                center_y
                / max(frame_height, 1)
            )

            # Bounding-box height gives us a
            # simple relative depth estimate.
            box_height = max(
                person.y2 - person.y1,
                1,
            )

            relative_depth = min(
                1.0,
                200.0 / box_height,
            )

            entity = SpatialEntity(
                entity_id=entity_id,
                entity_type="PERSON",
                position=SpatialPosition(
                    x=x,
                    y=y,
                    z=relative_depth,
                ),
                confidence=person.confidence,
                properties={
                    "movement_direction": (
                        person.movement_direction
                    ),
                    "movement_distance": (
                        person.movement_distance
                    ),
                    "zone": person.zone,
                    "bounding_box": {
                        "x1": person.x1,
                        "y1": person.y1,
                        "x2": person.x2,
                        "y2": person.y2,
                    },
                },
            )

            self.world.add_entity(
                entity
            )

        existing_people = (
            self.world.entities_by_type(
                "PERSON"
            )
        )

        for entity in existing_people:

            if entity.entity_id not in current_ids:
                self.world.remove_entity(
                    entity.entity_id
                )

        self.world.relate_nearby_entities()

        return self.world