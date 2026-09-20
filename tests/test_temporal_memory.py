from core.spatial.memory import (
    AUREXTemporalMemory,
    MemoryEventType,
)


class FakePerson:
    def __init__(self, person_id):
        self.person_id = person_id


class FakeObject:
    def __init__(self, label):
        self.label = label


class FakeEnvironment:
    def __init__(self, state):
        self.state = state


class FakeSecurity:
    def __init__(self, state="trusted", level="low"):
        self.state = state
        self.level = level


class FakeHazard:
    pass


class FakeVoice:
    def __init__(self, intent="show"):
        self.intent = intent


class FakeMultimodal:
    def __init__(self, intent="show"):
        self.intent = intent


def test_person_entered():
    memory = AUREXTemporalMemory()

    memory.observe(
        human_states=[],
        timestamp=1.0,
    )

    state = memory.observe(
        human_states=[FakePerson("person_1")],
        timestamp=2.0,
    )

    assert len(state.events) == 1
    assert state.events[0].event_type == MemoryEventType.PERSON_ENTERED


def test_person_left():
    memory = AUREXTemporalMemory()

    memory.observe(
        human_states=[FakePerson("person_1")],
        timestamp=1.0,
    )

    state = memory.observe(
        human_states=[],
        timestamp=2.0,
    )

    assert state.events[0].event_type == MemoryEventType.PERSON_LEFT


def test_object_appearance():
    memory = AUREXTemporalMemory()

    memory.observe(
        objects=[],
        timestamp=1.0,
    )

    state = memory.observe(
        objects=[FakeObject("phone")],
        timestamp=2.0,
    )

    assert state.events[0].event_type == MemoryEventType.OBJECT_APPEARED


def test_environment_change():
    memory = AUREXTemporalMemory()

    memory.observe(
        environment=FakeEnvironment("calm"),
        timestamp=1.0,
    )

    state = memory.observe(
        environment=FakeEnvironment("potential_hazard"),
        timestamp=2.0,
    )

    assert any(
        event.event_type == MemoryEventType.STATE_CHANGED
        for event in state.events
    )


def test_hazard_start_and_clear():
    memory = AUREXTemporalMemory()

    memory.observe(
        hazards=[],
        timestamp=1.0,
    )

    state = memory.observe(
        hazards=[FakeHazard()],
        timestamp=2.0,
    )

    assert any(
        event.event_type == MemoryEventType.HAZARD_STARTED
        for event in state.events
    )

    state = memory.observe(
        hazards=[],
        timestamp=3.0,
    )

    assert any(
        event.event_type == MemoryEventType.HAZARD_CLEARED
        for event in state.events
    )


def test_security_change():
    memory = AUREXTemporalMemory()

    memory.observe(
        security=FakeSecurity("trusted", "low"),
        timestamp=1.0,
    )

    state = memory.observe(
        security=FakeSecurity("suspicious", "high"),
        timestamp=2.0,
    )

    assert any(
        event.event_type == MemoryEventType.SECURITY_CHANGED
        for event in state.events
    )


def test_intent_change():
    memory = AUREXTemporalMemory()

    memory.observe(
        voice_command=FakeVoice("show"),
        multimodal_intent=FakeMultimodal("show"),
        timestamp=1.0,
    )

    state = memory.observe(
        voice_command=FakeVoice("clear"),
        multimodal_intent=FakeMultimodal("clear"),
        timestamp=2.0,
    )

    assert any(
        event.event_type == MemoryEventType.INTENT_CHANGED
        for event in state.events
    )


def test_state_duration():
    memory = AUREXTemporalMemory()

    for index in range(3):
        memory.observe(
            environment=FakeEnvironment("person_present"),
            timestamp=float(index),
        )

    assert memory.state_duration("person_present") == 3


def test_recent_event():
    memory = AUREXTemporalMemory()

    memory.observe(
        human_states=[],
        timestamp=1.0,
    )

    memory.observe(
        human_states=[FakePerson("person_1")],
        timestamp=2.0,
    )

    assert memory.has_recent_event(
        MemoryEventType.PERSON_ENTERED
    )


if __name__ == "__main__":
    test_person_entered()
    test_person_left()
    test_object_appearance()
    test_environment_change()
    test_hazard_start_and_clear()
    test_security_change()
    test_intent_change()
    test_state_duration()
    test_recent_event()

    print("PHASE 35 TEMPORAL MEMORY TESTS PASSED")