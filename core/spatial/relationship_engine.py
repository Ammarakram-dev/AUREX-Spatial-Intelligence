"""
AUREX Spatial Intelligence
Spatial Relationship Intelligence Engine
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core.spatial.world_model import (
    AUREXWorldModel,
    SpatialEntity,
    SpatialRelationship,
)


class RelationshipType(str, Enum):
    NEAR = "NEAR"
    SPATIALLY_NEAR = "SPATIALLY_NEAR"
    SAME_ZONE = "SAME_ZONE"
    APPROACHING = "APPROACHING"
    MOVING_AWAY = "MOVING_AWAY"


@dataclass
class RelationshipResult:
    """
    Represents an interpreted spatial relationship.
    """

    source_id: str
    relationship: RelationshipType
    target_id: str
    confidence: float
    distance: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "relationship": self.relationship.value,
            "target_id": self.target_id,
            "confidence": self.confidence,
            "distance": self.distance,
            "metadata": self.metadata,
        }


class AUREXRelationshipEngine:
    """
    Interprets spatial relationships between entities
    already present in the AUREX World Model.
    """

    def __init__(
        self,
        near_distance: float = 0.30,
        spatial_near_distance: float = 0.60,
    ) -> None:

        self.near_distance = near_distance
        self.spatial_near_distance = spatial_near_distance

    def calculate_distance(
        self,
        source: SpatialEntity,
        target: SpatialEntity,
    ) -> float:
        """
        Calculate Euclidean distance between two spatial entities.
        """

        return source.position.distance_to(target.position)

    def detect_proximity(
        self,
        source: SpatialEntity,
        target: SpatialEntity,
    ) -> RelationshipResult | None:

        distance = self.calculate_distance(source, target)

        if distance <= self.near_distance:

            confidence = max(
                0.0,
                1.0 - (distance / self.near_distance),
            )

            return RelationshipResult(
                source_id=source.entity_id,
                relationship=RelationshipType.NEAR,
                target_id=target.entity_id,
                confidence=confidence,
                distance=distance,
            )

        if distance <= self.spatial_near_distance:

            confidence = max(
                0.0,
                1.0
                - (
                    distance / self.spatial_near_distance
                ),
            )

            return RelationshipResult(
                source_id=source.entity_id,
                relationship=RelationshipType.SPATIALLY_NEAR,
                target_id=target.entity_id,
                confidence=confidence,
                distance=distance,
            )

        return None

    def detect_same_zone(
        self,
        source: SpatialEntity,
        target: SpatialEntity,
    ) -> RelationshipResult | None:

        source_zone = source.properties.get("zone")
        target_zone = target.properties.get("zone")

        if not source_zone or not target_zone:
            return None

        if source_zone != target_zone:
            return None

        return RelationshipResult(
            source_id=source.entity_id,
            relationship=RelationshipType.SAME_ZONE,
            target_id=target.entity_id,
            confidence=0.90,
            distance=self.calculate_distance(
                source,
                target,
            ),
            metadata={
                "zone": source_zone,
            },
        )

    def detect_movement_relationship(
        self,
        source: SpatialEntity,
        target: SpatialEntity,
    ) -> RelationshipResult | None:

        direction = source.properties.get(
            "movement_direction"
        )

        if not direction:
            return None

        distance = self.calculate_distance(
            source,
            target,
        )

        if direction == "STATIONARY":
            return None

        source_x = source.position.x
        source_y = source.position.y

        target_x = target.position.x
        target_y = target.position.y

        approaching = False

        if direction == "RIGHT" and target_x > source_x:
            approaching = True

        elif direction == "LEFT" and target_x < source_x:
            approaching = True

        elif direction == "DOWN" and target_y > source_y:
            approaching = True

        elif direction == "UP" and target_y < source_y:
            approaching = True

        if approaching:

            return RelationshipResult(
                source_id=source.entity_id,
                relationship=RelationshipType.APPROACHING,
                target_id=target.entity_id,
                confidence=0.70,
                distance=distance,
                metadata={
                    "movement_direction": direction,
                },
            )

        return RelationshipResult(
            source_id=source.entity_id,
            relationship=RelationshipType.MOVING_AWAY,
            target_id=target.entity_id,
            confidence=0.60,
            distance=distance,
            metadata={
                "movement_direction": direction,
            },
        )

    def analyze_pair(
        self,
        source: SpatialEntity,
        target: SpatialEntity,
    ) -> list[RelationshipResult]:

        results: list[RelationshipResult] = []

        proximity = self.detect_proximity(
            source,
            target,
        )

        if proximity is not None:
            results.append(proximity)

        same_zone = self.detect_same_zone(
            source,
            target,
        )

        if same_zone is not None:
            results.append(same_zone)

        movement = self.detect_movement_relationship(
            source,
            target,
        )

        if movement is not None:
            results.append(movement)

        return results

    def analyze_world(
        self,
        world: AUREXWorldModel,
    ) -> list[RelationshipResult]:

        entities = list(world.entities.values())

        results: list[RelationshipResult] = []

        for index, source in enumerate(entities):

            for target in entities[index + 1:]:

                results.extend(
                    self.analyze_pair(
                        source,
                        target,
                    )
                )

        return results

    def apply_to_world(
        self,
        world: AUREXWorldModel,
    ) -> list[RelationshipResult]:

        results = self.analyze_world(world)

        world.clear_relationships()

        for result in results:

            world.add_relationship(
                SpatialRelationship(
                    source_id=result.source_id,
                    relation=result.relationship.value,
                    target_id=result.target_id,
                    confidence=result.confidence,
                )
            )

        return results

    def status(self) -> dict[str, Any]:

        return {
            "near_distance": self.near_distance,
            "spatial_near_distance": (
                self.spatial_near_distance
            ),
            "relationship_types": [
                relationship.value
                for relationship in RelationshipType
            ],
        }