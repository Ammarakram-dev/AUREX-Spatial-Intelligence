from vision.person_tracker import TrackedPerson

from core.security.multi_person import (
    AUREXMultiPersonSecurity,
    GroupSecurityState,
    GroupSecurityLevel,
)


def make_person(
    person_id,
    x,
    y,
    direction="stationary",
    distance=0.0,
    zone="main",
):
    return TrackedPerson(
        person_id=person_id,
        x1=x - 25,
        y1=y - 50,
        x2=x + 25,
        y2=y + 50,
        confidence=0.95,
        previous_center=(x, y),
        current_center=(x, y),
        movement_distance=distance,
        movement_direction=direction,
        zone=zone,
    )


def test_no_people():
    engine = AUREXMultiPersonSecurity()

    result = engine.analyze([])

    assert result.state == GroupSecurityState.NO_GROUP
    assert result.level == GroupSecurityLevel.NORMAL


def test_single_person():
    engine = AUREXMultiPersonSecurity()

    person = make_person(
        "P1",
        100,
        100,
    )

    result = engine.analyze([person])

    assert result.state == GroupSecurityState.SINGLE_PERSON
    assert result.level == GroupSecurityLevel.NORMAL


def test_multiple_people():
    engine = AUREXMultiPersonSecurity()

    people = [
        make_person("P1", 100, 100),
        make_person("P2", 500, 400),
    ]

    result = engine.analyze(people)

    assert len(result.person_ids) == 2
    assert result.state == GroupSecurityState.MULTI_PERSON


def test_proximity():
    engine = AUREXMultiPersonSecurity(
        proximity_threshold=100,
    )

    people = [
        make_person("P1", 100, 100),
        make_person("P2", 150, 120),
    ]

    result = engine.analyze(people)

    assert len(result.nearby_pairs) == 1
    assert result.state == GroupSecurityState.PROXIMITY


def test_approach_pattern():
    engine = AUREXMultiPersonSecurity()

    people = [
        make_person(
            "P1",
            100,
            100,
            direction="approaching",
        ),
        make_person(
            "P2",
            120,
            120,
        ),
    ]

    result = engine.analyze(people)

    assert len(result.approaching_pairs) == 1
    assert result.state == GroupSecurityState.APPROACH_PATTERN


def test_high_density():
    engine = AUREXMultiPersonSecurity()

    people = [
        make_person("P1", 50, 50),
        make_person("P2", 150, 50),
        make_person("P3", 250, 50),
        make_person("P4", 350, 50),
    ]

    result = engine.analyze(people)

    assert result.state == GroupSecurityState.HIGH_DENSITY
    assert result.level == GroupSecurityLevel.WARNING


def test_temporal_stability():
    engine = AUREXMultiPersonSecurity(
        proximity_threshold=100,
        stability_frames=3,
    )

    people = [
        make_person("P1", 100, 100),
        make_person("P2", 150, 120),
    ]

    for _ in range(3):
        result = engine.analyze(people)

    assert result.state == GroupSecurityState.PROXIMITY
    assert engine.stable_state(
        GroupSecurityState.PROXIMITY
    )


if __name__ == "__main__":
    test_no_people()
    test_single_person()
    test_multiple_people()
    test_proximity()
    test_approach_pattern()
    test_high_density()
    test_temporal_stability()

    print("PHASE 31 MULTI-PERSON SECURITY TESTS PASSED")