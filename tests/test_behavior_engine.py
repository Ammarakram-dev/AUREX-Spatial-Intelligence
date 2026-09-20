from core.intelligence.behavior.behavior_engine import (
    AUREXBehaviorEngine,
)

from core.intelligence.behavior.behavior_state import (
    AnomalySeverity,
    BehaviorPattern,
)


def test_observation_history():
    engine = AUREXBehaviorEngine()

    for index in range(5):
        engine.observe(
            person_id="person_1",
            movement_distance=0.10,
            movement_direction="right",
            zone="center",
            posture="standing",
            timestamp=float(index),
        )

    assert len(
        engine.history["person_1"]
    ) == 5


def test_normal_movement():
    engine = AUREXBehaviorEngine()

    for index in range(8):
        engine.observe(
            person_id="person_1",
            movement_distance=0.08,
            movement_direction="right",
            zone="center",
            posture="standing",
            timestamp=float(index),
        )

    result = engine.analyze()

    assert len(result.profiles) == 1

    profile = result.profiles[0]

    assert profile.person_id == "person_1"
    assert profile.observation_count == 8
    assert profile.movement_frames == 8


def test_rapid_movement_anomaly():
    engine = AUREXBehaviorEngine(
        rapid_movement_threshold=0.30
    )

    for index in range(8):
        engine.observe(
            person_id="person_1",
            movement_distance=0.45,
            movement_direction="right",
            zone="center",
            posture="standing",
            timestamp=float(index),
        )

    result = engine.analyze()

    assert len(result.anomalies) >= 1

    anomaly = result.anomalies[0]

    assert (
        anomaly.pattern
        == BehaviorPattern.RAPID_MOVEMENT
    )

    assert anomaly.confidence > 0.50


def test_direction_change():
    engine = AUREXBehaviorEngine()

    directions = [
        "left",
        "right",
        "left",
        "right",
        "left",
        "right",
        "left",
    ]

    for index, direction in enumerate(
        directions
    ):
        engine.observe(
            person_id="person_1",
            movement_distance=0.10,
            movement_direction=direction,
            zone="center",
            posture="standing",
            timestamp=float(index),
        )

    result = engine.analyze()

    profile = result.profiles[0]

    assert (
        profile.direction_changes >= 5
    )

    assert (
        profile.recent_pattern
        == BehaviorPattern.DIRECTION_CHANGE
    )

    assert len(result.anomalies) >= 1


def test_prolonged_inactivity():
    engine = AUREXBehaviorEngine(
        prolonged_stationary_frames=5
    )

    for index in range(10):
        engine.observe(
            person_id="person_1",
            movement_distance=0.0,
            movement_direction="",
            zone="center",
            posture="standing",
            timestamp=float(index),
        )

    result = engine.analyze()

    profile = result.profiles[0]

    assert (
        profile.recent_pattern
        == BehaviorPattern.PROLONGED_INACTIVITY
    )


def test_multiple_people():
    engine = AUREXBehaviorEngine()

    for index in range(5):
        engine.observe(
            person_id="person_1",
            movement_distance=0.06,
            movement_direction="right",
            zone="left",
            posture="standing",
            timestamp=float(index),
        )

        engine.observe(
            person_id="person_2",
            movement_distance=0.07,
            movement_direction="left",
            zone="right",
            posture="standing",
            timestamp=float(index),
        )

    result = engine.analyze()

    assert len(result.profiles) == 2


def test_reset():
    engine = AUREXBehaviorEngine()

    engine.observe(
        person_id="person_1",
        movement_distance=0.10,
        movement_direction="right",
        zone="center",
        posture="standing",
        timestamp=1.0,
    )

    engine.reset()

    assert engine.history == {}


if __name__ == "__main__":
    test_observation_history()
    test_normal_movement()
    test_rapid_movement_anomaly()
    test_direction_change()
    test_prolonged_inactivity()
    test_multiple_people()
    test_reset()

    print("=" * 70)
    print(
        "AUREX PHASE 30 BEHAVIOR ENGINE TEST: PASSED"
    )
    print("=" * 70)