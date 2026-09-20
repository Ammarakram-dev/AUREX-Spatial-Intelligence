"""
AUREX Spatial Intelligence
Human Spatial State Tests
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from core.spatial.human_state import (
    AUREXHumanSpatialFusion,
    HumanSpatialState,
)
from core.spatial.world_model import SpatialEntity, SpatialPosition


class MockTrackedPerson:
    person_id = 1
    confidence = 0.94
    bbox = (100, 120, 220, 420)
    movement_direction = "RIGHT"
    movement_distance = 18.5
    zone = "CENTER"


class MockPosture:
    state = "STANDING"
    confidence = 0.91


def test_human_spatial_state():

    tracked_person = MockTrackedPerson()

    spatial_entity = SpatialEntity(
        entity_id="person_001",
        entity_type="PERSON",
        position=SpatialPosition(
            x=0.45,
            y=0.50,
            z=0.80,
        ),
        confidence=0.94,
    )

    posture = MockPosture()

    fusion = AUREXHumanSpatialFusion()

    state = fusion.build(
        tracked_person=tracked_person,
        spatial_entity=spatial_entity,
        posture_result=posture,
        pose_available=True,
    )

    assert isinstance(state, HumanSpatialState)

    assert state.person_id == 1

    assert state.posture == "STANDING"
    assert state.posture_confidence == 0.91

    assert state.movement_direction == "RIGHT"
    assert state.movement_distance == 18.5

    assert state.zone == "CENTER"

    assert state.detection_confidence == 0.94

    assert state.position.x == 0.45
    assert state.position.y == 0.50
    assert state.position.z == 0.80

    assert state.pose_available is True

    data = state.to_dict()

    assert data["person_id"] == 1
    assert data["posture"] == "STANDING"
    assert data["movement_direction"] == "RIGHT"
    assert data["zone"] == "CENTER"


if __name__ == "__main__":
    test_human_spatial_state()
    print("Human Spatial State test passed.")