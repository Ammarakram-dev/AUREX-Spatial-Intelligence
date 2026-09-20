from core.intelligence.situation import (
    AUREXPersonalContextEngine,
    AUREXUnifiedIntelligence,
    SituationType,
    ActivityLevel,
    ContextPriority,
)


def test_idle_context():
    engine = AUREXPersonalContextEngine()

    result = engine.analyze()

    assert result.situation == SituationType.IDLE
    assert result.activity_level == ActivityLevel.NONE
    assert result.priority == ContextPriority.NORMAL


def test_person_present():
    engine = AUREXPersonalContextEngine()

    person = {
        "person_id": "person_1",
        "movement_distance": 0.0,
        "movement_direction": "",
        "zone": "center",
    }

    result = engine.analyze(
        human_states=[person]
    )

    assert result.people_count == 1
    assert result.stationary_people == 1
    assert result.situation == SituationType.PERSON_PRESENT


def test_active_movement():
    engine = AUREXPersonalContextEngine()

    person = {
        "person_id": "person_1",
        "movement_distance": 0.20,
        "movement_direction": "forward",
        "zone": "center",
    }

    result = engine.analyze(
        human_states=[person]
    )

    assert result.people_count == 1
    assert result.moving_people == 1
    assert result.situation == SituationType.NORMAL_ACTIVITY
    assert result.activity_level == ActivityLevel.MODERATE


def test_approaching_person():
    engine = AUREXPersonalContextEngine()

    person = {
        "person_id": "person_1",
        "movement_distance": 0.20,
        "movement_direction": "approaching",
        "zone": "front",
    }

    result = engine.analyze(
        human_states=[person]
    )

    assert result.approaching_people == 1
    assert result.situation == SituationType.ACTIVE_INTERACTION
    assert result.recommended_mode == "track"


def test_security_event():
    engine = AUREXPersonalContextEngine()

    security = {
        "state": "suspicious",
        "level": "high",
        "confidence": 0.92,
    }

    result = engine.analyze(
        security=security
    )

    assert result.situation == SituationType.SECURITY_EVENT
    assert result.priority == ContextPriority.WARNING
    assert result.recommended_mode == "security_monitor"


def test_hazard_event():
    engine = AUREXPersonalContextEngine()

    hazard = {
        "assessments": [
            {
                "hazard_type": "fall_risk",
                "severity": "warning",
                "confidence": 0.85,
            }
        ]
    }

    result = engine.analyze(
        hazard=hazard
    )

    assert result.hazard_count == 1
    assert result.highest_hazard == "fall_risk"
    assert result.situation == SituationType.HAZARD_EVENT


def test_critical_hazard():
    engine = AUREXPersonalContextEngine()

    hazard = {
        "assessments": [
            {
                "hazard_type": "potential_incident",
                "severity": "critical",
                "confidence": 0.95,
            }
        ]
    }

    result = engine.analyze(
        hazard=hazard
    )

    assert result.situation == SituationType.EMERGENCY_CONTEXT
    assert result.activity_level == ActivityLevel.CRITICAL
    assert result.priority == ContextPriority.CRITICAL
    assert result.recommended_mode == "emergency_workflow"


def test_unified_state():
    engine = AUREXUnifiedIntelligence()

    person = {
        "person_id": "person_1",
        "movement_distance": 0.15,
        "movement_direction": "forward",
        "zone": "center",
    }

    state = engine.update(
        human_states=[person],
        security={
            "state": "trusted",
            "level": "low",
            "confidence": 0.95,
        },
        intent={
            "primary": "observe",
            "confidence": 0.90,
        },
        prediction={
            "assessments": [
                {
                    "prediction_type": "stable_state",
                    "level": "normal",
                    "confidence": 0.85,
                }
            ]
        },
    )

    assert state.people_count == 1
    assert state.security_state == "trusted"
    assert state.primary_intent == "observe"
    assert state.situation == SituationType.NORMAL_ACTIVITY
    assert state.confidence > 0.0


def test_history():
    engine = AUREXUnifiedIntelligence()

    engine.update()
    engine.update()

    assert len(engine.history) == 2
    assert len(engine.recent(2)) == 2


if __name__ == "__main__":
    test_idle_context()
    test_person_present()
    test_active_movement()
    test_approaching_person()
    test_security_event()
    test_hazard_event()
    test_critical_hazard()
    test_unified_state()
    test_history()

    print("PHASE 37 STEP 1 UNIFIED INTELLIGENCE TESTS PASSED")