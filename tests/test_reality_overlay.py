from vision.person_tracker import TrackedPerson

from core.spatial.overlay import (
    AUREXRealityOverlay,
    OverlayType,
)


def make_person(
    person_id,
    x,
    y,
    direction="stationary",
):
    return TrackedPerson(
        person_id=person_id,
        x1=x - 30,
        y1=y - 60,
        x2=x + 30,
        y2=y + 60,
        confidence=0.95,
        previous_center=(x, y),
        current_center=(x, y),
        movement_distance=0.0,
        movement_direction=direction,
        zone="main",
    )


def test_person_overlay():

    engine = AUREXRealityOverlay()

    person = make_person(
        "P1",
        200,
        200,
    )

    overlays = engine.people_overlays(
        [person]
    )

    assert len(overlays) == 1
    assert overlays[0].overlay_type == OverlayType.PERSON
    assert overlays[0].label == "PERSON P1"


def test_multiple_people():

    engine = AUREXRealityOverlay()

    people = [
        make_person("P1", 100, 100),
        make_person("P2", 400, 300),
    ]

    overlays = engine.people_overlays(
        people
    )

    assert len(overlays) == 2


def test_build():

    engine = AUREXRealityOverlay()

    person = make_person(
        "P1",
        200,
        200,
    )

    overlays = engine.build(
        people=[person],
        frame_width=640,
        frame_height=480,
    )

    assert len(overlays) == 1
    assert overlays[0].overlay_id == "person:P1"


def test_reset():

    engine = AUREXRealityOverlay()

    person = make_person(
        "P1",
        200,
        200,
    )

    engine.build(
        people=[person]
    )

    assert len(engine.history) == 1

    engine.reset()

    assert len(engine.history) == 0


if __name__ == "__main__":

    test_person_overlay()
    test_multiple_people()
    test_build()
    test_reset()

    print(
        "PHASE 32 REALITY OVERLAY TESTS PASSED"
    )