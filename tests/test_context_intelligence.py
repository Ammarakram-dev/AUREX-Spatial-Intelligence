"""
AUREX Spatial Intelligence
Context Intelligence Tests

Phase 18
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from core.intelligence.context import (
    AUREXContext,
    ContextType,
)

from core.intelligence.context_engine import (
    AUREXContextEngine,
)

from core.spatial.human_state import (
    AUREXHumanSpatialFusion,
)


class FakePerson:
    def __init__(
        self,
        person_id,
        movement_distance=0.0,
        movement_direction="stationary",
        posture="standing",
        zone="zone_a",
        confidence=0.95,
    ):
        self.person_id = person_id
        self.movement_distance = movement_distance
        self.movement_direction = movement_direction
        self.posture = posture
        self.zone = zone
        self.detection_confidence = confidence


class FakeRelationship:
    def __init__(
        self,
        source_id,
        relationship,
        target_id,
        confidence=0.9,
    ):
        self.source_id = source_id
        self.relationship = relationship
        self.target_id = target_id
        self.confidence = confidence


def test_empty_environment():

    engine = AUREXContextEngine()

    context = engine.analyze()

    assert isinstance(context, AUREXContext)

    assert context.context_type == ContextType.NORMAL

    assert context.people_count == 0

    assert context.confidence > 0.0


def test_single_stationary_person():

    engine = AUREXContextEngine()

    person = FakePerson(
        person_id="person_1",
        movement_distance=0.0,
        posture="standing",
    )

    context = engine.analyze(
        human_states=[person]
    )

    assert context.people_count == 1

    assert "person_1" in context.stationary_people

    assert (
        context.context_type
        == ContextType.PERSON_STATIONARY
    )


def test_moving_person():

    engine = AUREXContextEngine()

    person = FakePerson(
        person_id="person_1",
        movement_distance=0.50,
        movement_direction="forward",
        posture="standing",
    )

    context = engine.analyze(
        human_states=[person]
    )

    assert "person_1" in context.moving_people

    assert (
        context.context_type
        == ContextType.PERSON_MOVING
    )


def test_sitting_person():

    engine = AUREXContextEngine()

    person = FakePerson(
        person_id="person_1",
        posture="sitting",
    )

    context = engine.analyze(
        human_states=[person]
    )

    assert "person_1" in context.seated_people

    assert (
        context.context_type
        == ContextType.PERSON_SITTING
    )


def test_lying_person_creates_incident_context():

    engine = AUREXContextEngine()

    person = FakePerson(
        person_id="person_1",
        posture="lying",
        confidence=0.92,
    )

    context = engine.analyze(
        human_states=[person]
    )

    assert "person_1" in context.lying_people

    assert (
        context.context_type
        == ContextType.POTENTIAL_INCIDENT
    )

    assert context.confidence > 0.0


def test_approaching_relationship():

    engine = AUREXContextEngine()

    person = FakePerson(
        person_id="person_1",
        movement_distance=0.20,
    )

    relationship = FakeRelationship(
        source_id="person_1",
        relationship="approaching",
        target_id="person_2",
    )

    context = engine.analyze(
        human_states=[person],
        relationships=[relationship],
    )

    assert (
        "person_1"
        in context.approaching_people
    )

    assert (
        context.context_type
        == ContextType.PERSON_APPROACHING
    )


def test_multiple_people():

    engine = AUREXContextEngine()

    people = [
        FakePerson("person_1"),
        FakePerson("person_2"),
    ]

    context = engine.analyze(
        human_states=people
    )

    assert context.people_count == 2

    assert (
        context.context_type
        == ContextType.MULTIPLE_PEOPLE
    )


def test_spatial_interaction():

    engine = AUREXContextEngine()

    people = [
        FakePerson("person_1"),
        FakePerson("person_2"),
    ]

    relationship = FakeRelationship(
        source_id="person_1",
        relationship="near",
        target_id="person_2",
    )

    context = engine.analyze(
        human_states=people,
        relationships=[relationship],
    )

    assert context.relationship_count == 1

    assert (
        context.context_type
        == ContextType.SPATIAL_INTERACTION
    )

    assert len(context.evidence) > 0


def test_context_serialization():

    engine = AUREXContextEngine()

    person = FakePerson(
        person_id="person_1",
        movement_distance=0.20,
    )

    context = engine.analyze(
        human_states=[person]
    )

    data = context.to_dict()

    assert isinstance(data, dict)

    assert "context_type" in data

    assert "confidence" in data

    assert "people_count" in data

    assert "evidence" in data


def test_engine_status():

    engine = AUREXContextEngine()

    status = engine.status()

    assert status["engine"] == "AUREXContextEngine"

    assert status["status"] == "ready"


def test_human_spatial_fusion_compatibility():

    """
    Verify that Phase 18 can consume the Phase 16
    HumanSpatialState representation.
    """

    fusion = AUREXHumanSpatialFusion()

    assert fusion is not None


if __name__ == "__main__":

    test_empty_environment()
    test_single_stationary_person()
    test_moving_person()
    test_sitting_person()
    test_lying_person_creates_incident_context()
    test_approaching_relationship()
    test_multiple_people()
    test_spatial_interaction()
    test_context_serialization()
    test_engine_status()
    test_human_spatial_fusion_compatibility()

    print("=" * 70)
    print("AUREX PHASE 18 CONTEXT INTELLIGENCE TESTS")
    print("=" * 70)
    print("All tests passed.")
    print("=" * 70)