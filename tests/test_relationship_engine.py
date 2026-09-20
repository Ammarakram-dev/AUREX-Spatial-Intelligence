"""
AUREX Spatial Intelligence
Spatial Relationship Intelligence Tests
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from core.spatial.relationship_engine import (
    AUREXRelationshipEngine,
    RelationshipType,
)
from core.spatial.world_model import (
    AUREXWorldModel,
    SpatialEntity,
    SpatialPosition,
)


def test_relationship_engine():

    world = AUREXWorldModel()

    person = SpatialEntity(
        entity_id="person_001",
        entity_type="PERSON",
        position=SpatialPosition(
            x=0.20,
            y=0.50,
            z=0.50,
        ),
        confidence=0.95,
        properties={
            "zone": "LEFT",
            "movement_direction": "RIGHT",
        },
    )

    door = SpatialEntity(
        entity_id="door_001",
        entity_type="DOOR",
        position=SpatialPosition(
            x=0.35,
            y=0.50,
            z=0.50,
        ),
        confidence=0.98,
        properties={
            "zone": "LEFT",
        },
    )

    world.add_entity(person)
    world.add_entity(door)

    engine = AUREXRelationshipEngine(
        near_distance=0.30,
        spatial_near_distance=0.60,
    )

    results = engine.analyze_world(world)

    assert len(results) > 0

    relationship_types = {
        result.relationship
        for result in results
    }

    assert RelationshipType.NEAR in relationship_types

    assert RelationshipType.SAME_ZONE in relationship_types

    assert RelationshipType.APPROACHING in relationship_types

    applied = engine.apply_to_world(world)

    assert len(applied) > 0

    assert len(world.relationships) > 0

    print("Spatial Relationship Engine test passed.")


if __name__ == "__main__":
    test_relationship_engine()