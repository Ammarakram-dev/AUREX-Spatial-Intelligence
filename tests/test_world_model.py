import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.spatial.world_model import (
    AUREXWorldModel,
    SpatialEntity,
    SpatialPosition,
)


def main():

    print("=" * 60)
    print("AUREX SPATIAL WORLD MODEL TEST")
    print("=" * 60)

    world = AUREXWorldModel()

    person = SpatialEntity(
        entity_id="person_001",
        entity_type="PERSON",
        position=SpatialPosition(
            x=0.40,
            y=0.50,
            z=0.20,
        ),
        confidence=0.94,
        properties={
            "posture": "STANDING",
            "zone": "CENTER",
        },
    )

    object_1 = SpatialEntity(
        entity_id="object_001",
        entity_type="OBJECT",
        position=SpatialPosition(
            x=0.48,
            y=0.52,
            z=0.18,
        ),
        confidence=0.88,
        properties={
            "name": "TABLE",
        },
    )

    object_2 = SpatialEntity(
        entity_id="object_002",
        entity_type="OBJECT",
        position=SpatialPosition(
            x=0.90,
            y=0.80,
            z=0.50,
        ),
        confidence=0.91,
        properties={
            "name": "DOOR",
        },
    )

    world.add_entity(person)
    world.add_entity(object_1)
    world.add_entity(object_2)

    world.relate_nearby_entities(
        radius=0.20
    )

    print()
    print("WORLD STATUS")
    print(world.status())

    print()
    print("NEARBY PERSON ENTITIES")

    nearby = world.find_nearby(
        "person_001",
        radius=0.20,
    )

    for entity in nearby:
        print(
            f"- {entity.entity_id}: "
            f"{entity.properties.get('name', entity.entity_type)}"
        )

    print()
    print("SPATIAL RELATIONSHIPS")

    for relationship in world.relationships:
        print(
            f"- {relationship.source_id} "
            f"--{relationship.relation}--> "
            f"{relationship.target_id} "
            f"({relationship.confidence:.2f})"
        )

    print()
    print("WORLD SNAPSHOT")

    snapshot = world.snapshot()

    print(
        "Entities:",
        len(snapshot["entities"]),
    )

    print(
        "Relationships:",
        len(snapshot["relationships"]),
    )

    assert len(world.entities) == 3

    assert len(nearby) == 1

    assert len(world.relationships) >= 1

    print()
    print("=" * 60)
    print("SPATIAL WORLD MODEL TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()