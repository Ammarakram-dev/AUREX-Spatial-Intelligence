from core.intelligence.environment import (
    AUREXEnvironmentEngine,
    EnvironmentState,
)


class FakePerson:
    def __init__(
        self,
        movement_distance=0.0,
        movement_direction="stationary",
        posture="standing",
    ):
        self.movement_distance = movement_distance
        self.movement_direction = movement_direction
        self.posture = posture


class FakeHazard:
    def __init__(
        self,
        confidence=0.80,
        severity="warning",
    ):
        self.confidence = confidence
        self.severity = severity


class FakeSecurity:
    def __init__(
        self,
        state="trusted",
        level="low",
    ):
        self.state = state
        self.level = level


class FakeVoice:
    def __init__(
        self,
        intent="show",
        confidence=0.80,
    ):
        self.intent = intent
        self.confidence = confidence


class FakeMultimodal:
    def __init__(
        self,
        intent="show",
        confidence=0.85,
    ):
        self.intent = intent
        self.confidence = confidence


def test_person_context():
    engine = AUREXEnvironmentEngine()

    result = engine.analyze(
        human_states=[
            FakePerson(
                movement_distance=0.12,
                movement_direction="moving",
                posture="standing",
            )
        ]
    )

    assert result.people_count == 1
    assert result.moving_people == 1
    assert result.state == EnvironmentState.PEOPLE_ACTIVE
    assert result.confidence > 0.0


def test_multi_person_context():
    engine = AUREXEnvironmentEngine()

    result = engine.analyze(
        human_states=[
            FakePerson(),
            FakePerson(),
        ]
    )

    assert result.people_count == 2
    assert result.state == EnvironmentState.MULTI_PERSON


def test_hazard_context():
    engine = AUREXEnvironmentEngine()

    result = engine.analyze(
        human_states=[FakePerson()],
        hazards=[
            FakeHazard(
                confidence=0.80,
                severity="warning",
            )
        ],
    )

    assert result.hazard_count == 1
    assert result.state == EnvironmentState.POTENTIAL_HAZARD


def test_emergency_context():
    engine = AUREXEnvironmentEngine()

    result = engine.analyze(
        human_states=[FakePerson()],
        hazards=[
            FakeHazard(
                confidence=0.95,
                severity="critical",
            )
        ],
    )

    assert result.state == EnvironmentState.EMERGENCY_CONTEXT


def test_security_context():
    engine = AUREXEnvironmentEngine()

    result = engine.analyze(
        human_states=[FakePerson()],
        security=FakeSecurity(
            state="suspicious",
            level="high",
        ),
    )

    assert result.state == EnvironmentState.SECURITY_VERIFICATION
    assert result.security_state == "suspicious"


def test_multimodal_context():
    engine = AUREXEnvironmentEngine()

    result = engine.analyze(
        human_states=[FakePerson()],
        voice_command=FakeVoice(
            intent="show",
            confidence=0.90,
        ),
        multimodal_intent=FakeMultimodal(
            intent="show",
            confidence=0.88,
        ),
    )

    assert result.voice_intent == "show"
    assert result.multimodal_intent == "show"
    assert len(result.evidence) >= 2


def test_object_context():
    engine = AUREXEnvironmentEngine()

    result = engine.analyze(
        objects=[
            {"label": "phone"},
            {"label": "chair"},
        ]
    )

    assert result.object_count == 2
    assert result.state == EnvironmentState.CALM


def test_stable_state():
    engine = AUREXEnvironmentEngine()

    for _ in range(3):
        result = engine.analyze(
            human_states=[
                FakePerson(
                    movement_distance=0.0,
                    movement_direction="stationary",
                )
            ]
        )

    assert result.state == EnvironmentState.PERSON_PRESENT
    assert engine.stable_state(3) == EnvironmentState.PERSON_PRESENT


if __name__ == "__main__":
    test_person_context()
    test_multi_person_context()
    test_hazard_context()
    test_emergency_context()
    test_security_context()
    test_multimodal_context()
    test_object_context()
    test_stable_state()

    print("PHASE 34 ENVIRONMENT INTELLIGENCE TESTS PASSED")