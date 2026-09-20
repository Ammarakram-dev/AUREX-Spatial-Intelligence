"""
AUREX Spatial Intelligence
3D Spatial World Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import sqrt
from typing import Any


@dataclass
class SpatialPosition:
    """
    Normalized 3D position.

    x, y represent image/world-relative horizontal
    and vertical coordinates.

    z represents estimated depth.
    """

    x: float
    y: float
    z: float = 0.0

    def distance_to(
        self,
        other: "SpatialPosition",
    ) -> float:

        return sqrt(
            (self.x - other.x) ** 2
            + (self.y - other.y) ** 2
            + (self.z - other.z) ** 2
        )

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }


@dataclass
class SpatialEntity:
    entity_id: str
    entity_type: str
    position: SpatialPosition
    confidence: float = 1.0
    properties: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "position": self.position.to_dict(),
            "confidence": self.confidence,
            "properties": self.properties,
        }


@dataclass
class SpatialRelationship:
    source_id: str
    relation: str
    target_id: str
    confidence: float = 1.0

    def to_dict(self) -> dict:
        return {
            "source": self.source_id,
            "relation": self.relation,
            "target": self.target_id,
            "confidence": self.confidence,
        }


class AUREXWorldModel:
    """
    Maintains AUREX's current spatial representation
    of people, objects and their relationships.
    """

    def __init__(self) -> None:

        self.entities: dict[
            str,
            SpatialEntity,
        ] = {}

        self.relationships: list[
            SpatialRelationship
        ] = []

        self.updated_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

    def add_entity(
        self,
        entity: SpatialEntity,
    ) -> None:

        self.entities[
            entity.entity_id
        ] = entity

        self._touch()

    def remove_entity(
        self,
        entity_id: str,
    ) -> None:

        self.entities.pop(
            entity_id,
            None,
        )

        self.relationships = [
            relationship
            for relationship in self.relationships
            if (
                relationship.source_id
                != entity_id
                and relationship.target_id
                != entity_id
            )
        ]

        self._touch()

    def get_entity(
        self,
        entity_id: str,
    ) -> SpatialEntity | None:

        return self.entities.get(
            entity_id
        )

    def add_relationship(
        self,
        relationship: SpatialRelationship,
    ) -> None:

        self.relationships.append(
            relationship
        )

        self._touch()

    def clear_relationships(self) -> None:

        self.relationships.clear()

        self._touch()

    def find_nearby(
        self,
        entity_id: str,
        radius: float,
    ) -> list[SpatialEntity]:

        source = self.get_entity(
            entity_id
        )

        if source is None:
            return []

        nearby = []

        for entity in self.entities.values():

            if entity.entity_id == entity_id:
                continue

            distance = (
                source.position.distance_to(
                    entity.position
                )
            )

            if distance <= radius:
                nearby.append(entity)

        return nearby

    def entities_by_type(
        self,
        entity_type: str,
    ) -> list[SpatialEntity]:

        return [
            entity
            for entity in self.entities.values()
            if entity.entity_type
            == entity_type
        ]

    def relate_nearby_entities(
        self,
        radius: float = 0.25,
    ) -> None:

        self.relationships.clear()

        entity_list = list(
            self.entities.values()
        )

        for index, source in enumerate(
            entity_list
        ):

            for target in entity_list[
                index + 1:
            ]:

                distance = (
                    source.position.distance_to(
                        target.position
                    )
                )

                if distance > radius:
                    continue

                if (
                    source.entity_type
                    == "PERSON"
                    and target.entity_type
                    == "OBJECT"
                ):

                    relation = (
                        "NEAR"
                    )

                elif (
                    source.entity_type
                    == "OBJECT"
                    and target.entity_type
                    == "PERSON"
                ):

                    relation = (
                        "NEAR"
                    )

                else:

                    relation = (
                        "SPATIALLY_NEAR"
                    )

                confidence = max(
                    0.0,
                    1.0
                    - (
                        distance
                        / radius
                    ),
                )

                self.relationships.append(
                    SpatialRelationship(
                        source_id=(
                            source.entity_id
                        ),
                        relation=relation,
                        target_id=(
                            target.entity_id
                        ),
                        confidence=confidence,
                    )
                )

        self._touch()

    def snapshot(self) -> dict:

        return {
            "updated_at": self.updated_at,
            "entities": [
                entity.to_dict()
                for entity in self.entities.values()
            ],
            "relationships": [
                relationship.to_dict()
                for relationship
                in self.relationships
            ],
        }

    def _touch(self) -> None:

        self.updated_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

    def status(self) -> dict:

        return {
            "entities": len(
                self.entities
            ),
            "relationships": len(
                self.relationships
            ),
            "people": len(
                self.entities_by_type(
                    "PERSON"
                )
            ),
            "objects": len(
                self.entities_by_type(
                    "OBJECT"
                )
            ),
            "updated_at": self.updated_at,
        }