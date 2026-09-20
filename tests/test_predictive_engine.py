from core.intelligence.prediction import (
    AUREXPredictiveEngine,
    PredictionLevel,
    PredictionType,
)
from core.spatial.memory import (
    AUREXTemporalMemory,
)


class FakePerson:
    def __init__(self, person_id):
        self.person_id = person_id


class FakeEnvironment:
    def __init__(self, state):
        self.state = state


class FakeHazard:
    pass


def test_stable_state():
    memory = AUREXTemporalMemory()
    engine = AUREXPredictiveEngine()

    for index in range(5):
        memory.observe(
            human_states=[
                FakePerson("person_1")
            ],
            environment=FakeEnvironment(
                "person_present"
            ),
            timestamp=float(index),
        )

    results = engine.analyze(memory)

    assert any(
        result.prediction_type
        == PredictionType.STABLE_STATE
        for result in results
    )


def test_increasing_activity():
    memory = AUREXTemporalMemory()
    engine = AUREXPredictiveEngine()

    memory.observe(
        human_states=[],
        environment=FakeEnvironment("calm"),
        timestamp=1.0,
    )

    memory.observe(
        human_states=[],
        environment=FakeEnvironment("calm"),
        timestamp=2.0,
    )

    memory.observe(
        human_states=[
            FakePerson("p1")
        ],
        environment=FakeEnvironment("person_present"),
        timestamp=3.0,
    )

    memory.observe(
        human_states=[
            FakePerson("p1"),
            FakePerson("p2"),
        ],
        environment=FakeEnvironment("multi_person"),
        timestamp=4.0,
    )

    results = engine.analyze(memory)

    assert any(
        result.prediction_type
        == PredictionType.INCREASING_ACTIVITY
        for result in results
    )


def test_hazard_persistence():
    memory = AUREXTemporalMemory()
    engine = AUREXPredictiveEngine()

    for index in range(5):
        memory.observe(
            hazards=[FakeHazard()],
            environment=FakeEnvironment(
                "potential_hazard"
            ),
            timestamp=float(index),
        )

    results = engine.analyze(memory)

    assert any(
        result.prediction_type
        == PredictionType.HAZARD_PERSISTENCE
        for result in results
    )


def test_hazard_escalation():
    memory = AUREXTemporalMemory()
    engine = AUREXPredictiveEngine()

    for index, count in enumerate(
        [0, 1, 2, 3]
    ):
        hazards = [
            FakeHazard()
            for _ in range(count)
        ]

        memory.observe(
            hazards=hazards,
            environment=FakeEnvironment(
                "potential_hazard"
                if count
                else "calm"
            ),
            timestamp=float(index),
        )

    results = engine.analyze(memory)

    assert any(
        result.prediction_type
        == PredictionType.HAZARD_ESCALATION
        for result in results
    )


def test_environment_transition():
    memory = AUREXTemporalMemory()
    engine = AUREXPredictiveEngine()

    states = [
        "calm",
        "person_present",
        "people_active",
        "multi_person",
    ]

    for index, state in enumerate(states):
        memory.observe(
            environment=FakeEnvironment(state),
            timestamp=float(index),
        )

    results = engine.analyze(memory)

    assert any(
        result.prediction_type
        == PredictionType.ENVIRONMENT_TRANSITION
        for result in results
    )


def test_highest_risk():
    memory = AUREXTemporalMemory()
    engine = AUREXPredictiveEngine()

    for index, count in enumerate(
        [0, 1, 2, 3]
    ):
        memory.observe(
            hazards=[
                FakeHazard()
                for _ in range(count)
            ],
            environment=FakeEnvironment(
                "potential_hazard"
                if count
                else "calm"
            ),
            timestamp=float(index),
        )

    engine.analyze(memory)

    result = engine.highest_risk()

    assert result.level == PredictionLevel.HIGH


if __name__ == "__main__":
    test_stable_state()
    test_increasing_activity()
    test_hazard_persistence()
    test_hazard_escalation()
    test_environment_transition()
    test_highest_risk()

    print("PHASE 36 PREDICTIVE ENGINE TESTS PASSED")