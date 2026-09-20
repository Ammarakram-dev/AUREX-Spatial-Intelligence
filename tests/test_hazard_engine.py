from core.intelligence.hazard import (
    HazardSeverity,
    HazardType,
    HazardResponse,
)
from core.intelligence.hazard_engine import (
    AUREXHazardEngine,
)


class FakeState:

    def __init__(
        self,
        person_id,
        posture="standing",
        movement_distance=0.0,
        movement_direction="stationary",
    ):
        self.person_id = person_id
        self.posture = posture
        self.movement_distance = movement_distance
        self.movement_direction = movement_direction


class FakeRelationship:

    def __init__(
        self,
        source_id,
        relationship,
        target_id,
    ):
        self.source_id = source_id
        self.relationship = relationship
        self.target_id = target_id


class FakeContext:

    def __init__(
        self,
        context_type,
    ):
        self.context_type = context_type


def test_fall_risk():

    engine = AUREXHazardEngine()

    states = [
        FakeState(
            "person_1",
            posture="lying",
            movement_distance=0.30,
        )
    ]

    result = engine.detect_fall_risk(
        states
    )

    assert result is not None
    assert result.hazard_type == HazardType.FALL_RISK
    assert result.confidence > 0.0


def test_rapid_approach():

    engine = AUREXHazardEngine()

    relationships = [
        FakeRelationship(
            "person_1",
            "approaching",
            "person_2",
        )
    ]

    result = engine.detect_rapid_approach(
        [],
        relationships,
    )

    assert result is not None
    assert (
        result.hazard_type
        == HazardType.RAPID_APPROACH
    )


def test_abnormal_movement():

    engine = AUREXHazardEngine()

    states = [
        FakeState(
            "person_1",
            movement_distance=0.80,
            movement_direction="unknown",
        )
    ]

    result = engine.detect_abnormal_movement(
        states
    )

    assert result is not None
    assert (
        result.hazard_type
        == HazardType.ABNORMAL_MOVEMENT
    )


def test_crowding():

    engine = AUREXHazardEngine()

    states = [
        FakeState(f"person_{i}")
        for i in range(5)
    ]

    result = engine.detect_crowding(
        states
    )

    assert result is not None
    assert (
        result.hazard_type
        == HazardType.CROWDING
    )


def test_context_incident():

    engine = AUREXHazardEngine()

    result = engine.analyze(
        context=FakeContext(
            "potential_incident"
        )
    )

    assert len(result) == 1
    assert (
        result[0].hazard_type
        == HazardType.POTENTIAL_INCIDENT
    )


def test_highest_risk():

    engine = AUREXHazardEngine()

    assessments = engine.analyze(
        human_states=[
            FakeState(
                "person_1",
                posture="lying",
                movement_distance=0.40,
            ),
            FakeState(
                "person_2",
                posture="standing",
            ),
            FakeState(
                "person_3",
                posture="standing",
            ),
            FakeState(
                "person_4",
                posture="standing",
            ),
        ]
    )

    highest = engine.highest_risk(
        assessments
    )

    assert highest is not None
    assert highest.severity in {
        HazardSeverity.WARNING,
        HazardSeverity.HIGH,
        HazardSeverity.CRITICAL,
    }


if __name__ == "__main__":
    test_fall_risk()
    test_rapid_approach()
    test_abnormal_movement()
    test_crowding()
    test_context_incident()
    test_highest_risk()

    print("=" * 70)
    print("PHASE 27 HAZARD ENGINE TEST: PASS")
    print("=" * 70)