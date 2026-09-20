from __future__ import annotations

from typing import Any, Dict, Iterable, Optional
import time

from .situation_state import (
    ActivityLevel,
    ContextPriority,
    PersonalContext,
    SituationEvidence,
    SituationType,
    UnifiedWorldState,
)


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(name, default)

    return getattr(obj, name, default)


def _enum_value(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default

    if hasattr(value, "value"):
        return str(value.value)

    return str(value)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class AUREXPersonalContextEngine:
    """
    Converts multiple AUREX intelligence outputs into one
    situational/personal context representation.

    This engine reasons only from observable system signals.
    It does not infer private thoughts, motives, personality,
    medical conditions, or hidden mental states.
    """

    def __init__(
        self,
        attention_threshold: float = 0.60,
        warning_threshold: float = 0.75,
        critical_threshold: float = 0.90,
    ):
        self.attention_threshold = attention_threshold
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

        self.history = []
        self.history_limit = 60

        self.last_context: Optional[PersonalContext] = None

    def analyze(
        self,
        context: Any = None,
        human_states: Optional[Iterable[Any]] = None,
        relationships: Optional[Iterable[Any]] = None,
        scene: Any = None,
        security: Any = None,
        hazard: Any = None,
        behavior: Any = None,
        affect: Any = None,
        prediction: Any = None,
        intent: Any = None,
        multimodal: Any = None,
        memory: Any = None,
    ) -> PersonalContext:

        result = PersonalContext()

        people = list(human_states or [])
        relation_list = list(relationships or [])

        result.people_count = len(people)

        if scene is not None:
            result.object_count = _safe_int(
                _get(scene, "object_count", _get(scene, "objects_count", 0))
            )

        moving = 0
        stationary = 0
        approaching = 0
        separating = 0

        for person in people:
            movement_distance = _safe_float(
                _get(person, "movement_distance", 0.0)
            )

            direction = str(
                _get(person, "movement_direction", "")
            ).lower()

            if movement_distance >= 0.05:
                moving += 1
            else:
                stationary += 1

            if "approach" in direction:
                approaching += 1

            if (
                "away" in direction
                or "separat" in direction
                or "depart" in direction
            ):
                separating += 1

            zone = _get(person, "zone", None)

            if zone:
                result.zone_counts[str(zone)] = (
                    result.zone_counts.get(str(zone), 0) + 1
                )

        result.moving_people = moving
        result.stationary_people = stationary
        result.approaching_people = approaching
        result.separating_people = separating

        if context is not None:
            result.metadata["context"] = _get(
                context,
                "metadata",
                {},
            )

            context_type = _enum_value(
                _get(context, "context_type", "unknown")
            )

            if context_type != "unknown":
                result.reasons.append(
                    f"Context engine reports {context_type}."
                )

            result.add_evidence(
                SituationEvidence(
                    source="context",
                    value=context_type,
                    confidence=_safe_float(
                        _get(context, "confidence", 0.0)
                    ),
                    weight=1.0,
                )
            )

        if security is not None:
            result.security_state = _enum_value(
                _get(security, "state", "unknown")
            )
            result.security_level = _enum_value(
                _get(security, "level", "unknown")
            )

            security_confidence = _safe_float(
                _get(security, "confidence", 0.0)
            )

            if result.security_state not in {
                "unknown",
                "trusted",
                "no_presence",
            }:
                result.reasons.append(
                    f"Security state is {result.security_state}."
                )

            result.add_evidence(
                SituationEvidence(
                    source="security",
                    value=result.security_state,
                    confidence=security_confidence,
                    weight=1.2,
                )
            )

        if hazard is not None:
            assessments = []

            if isinstance(hazard, (list, tuple)):
                assessments = list(hazard)
            else:
                assessments = list(
                    _get(hazard, "assessments", []) or []
                )

                if not assessments and _get(hazard, "hazard_type") is not None:
                    assessments = [hazard]

            result.hazard_count = len(assessments)

            if assessments:
                ranked = sorted(
                    assessments,
                    key=lambda item: _safe_float(
                        _get(item, "confidence", 0.0)
                    ),
                    reverse=True,
                )

                top = ranked[0]

                result.highest_hazard = _enum_value(
                    _get(top, "hazard_type", "unknown")
                )

                result.highest_hazard_severity = _enum_value(
                    _get(top, "severity", "normal")
                )

                result.reasons.append(
                    f"Hazard intelligence reports {result.hazard_count} assessment(s)."
                )

                for item in assessments:
                    result.add_evidence(
                        SituationEvidence(
                            source="hazard",
                            value=_enum_value(
                                _get(item, "hazard_type", "unknown")
                            ),
                            confidence=_safe_float(
                                _get(item, "confidence", 0.0)
                            ),
                            weight=1.3,
                        )
                    )

        if behavior is not None:
            result.behavior_anomaly_score = _safe_float(
                _get(
                    behavior,
                    "global_anomaly_score",
                    _get(behavior, "anomaly_score", 0.0),
                )
            )

            result.behavior_anomaly_score = max(
                0.0,
                min(1.0, result.behavior_anomaly_score),
            )

            if result.behavior_anomaly_score > 0.50:
                result.reasons.append(
                    "Behavior analysis reports elevated observable activity."
                )

            result.add_evidence(
                SituationEvidence(
                    source="behavior",
                    value=result.behavior_anomaly_score,
                    confidence=result.behavior_anomaly_score,
                    weight=0.8,
                )
            )

        if affect is not None:
            emotion = _get(
                affect,
                "emotion",
                _get(affect, "affect", _get(affect, "state", "unknown")),
            )

            result.affect_state = _enum_value(emotion)

            result.add_evidence(
                SituationEvidence(
                    source="affect",
                    value=result.affect_state,
                    confidence=_safe_float(
                        _get(affect, "confidence", 0.0)
                    ),
                    weight=0.5,
                )
            )

        if prediction is not None:
            prediction_items = []

            if isinstance(prediction, (list, tuple)):
                prediction_items = list(prediction)
            else:
                prediction_items = list(
                    _get(prediction, "assessments", []) or []
                )

                if not prediction_items and _get(
                    prediction,
                    "prediction_type",
                ) is not None:
                    prediction_items = [prediction]

            if prediction_items:
                top_prediction = max(
                    prediction_items,
                    key=lambda item: _safe_float(
                        _get(item, "confidence", 0.0)
                    ),
                )

                result.prediction_type = _enum_value(
                    _get(top_prediction, "prediction_type", "unknown")
                )

                result.prediction_level = _enum_value(
                    _get(top_prediction, "level", "normal")
                )

                result.add_evidence(
                    SituationEvidence(
                        source="prediction",
                        value=result.prediction_type,
                        confidence=_safe_float(
                            _get(top_prediction, "confidence", 0.0)
                        ),
                        weight=1.0,
                    )
                )

        if intent is not None:
            primary = _get(
                intent,
                "primary",
                _get(intent, "intent_type", "unknown"),
            )

            result.primary_intent = _enum_value(primary)

            result.add_evidence(
                SituationEvidence(
                    source="intent",
                    value=result.primary_intent,
                    confidence=_safe_float(
                        _get(intent, "confidence", 0.0)
                    ),
                    weight=0.8,
                )
            )

        if multimodal is not None:
            result.multimodal_intent = _enum_value(
                _get(
                    multimodal,
                    "intent",
                    _get(multimodal, "intent_type", "unknown"),
                )
            )

            result.add_evidence(
                SituationEvidence(
                    source="multimodal",
                    value=result.multimodal_intent,
                    confidence=_safe_float(
                        _get(multimodal, "confidence", 0.0)
                    ),
                    weight=1.0,
                )
            )

        self._classify_situation(
            result,
            relation_count=len(relation_list),
        )

        result.calculate_confidence()

        self._record(result)

        self.last_context = result

        return result

    def _classify_situation(
        self,
        result: PersonalContext,
        relation_count: int,
    ) -> None:

        hazard_severity = result.highest_hazard_severity.lower()
        security_state = result.security_state.lower()

        if hazard_severity == "critical":
            result.situation = SituationType.EMERGENCY_CONTEXT
            result.activity_level = ActivityLevel.CRITICAL
            result.priority = ContextPriority.CRITICAL
            result.recommended_mode = "emergency_workflow"
            result.reasons.append(
                "A critical hazard signal is present."
            )
            return

        if result.hazard_count > 0:
            result.situation = SituationType.HAZARD_EVENT
            result.activity_level = ActivityLevel.HIGH
            result.priority = ContextPriority.WARNING
            result.recommended_mode = "alert"
            return

        if security_state in {
            "suspicious",
            "denied",
            "locked",
        }:
            result.situation = SituationType.SECURITY_EVENT
            result.activity_level = ActivityLevel.HIGH
            result.priority = ContextPriority.WARNING
            result.recommended_mode = "security_monitor"
            return

        if result.approaching_people > 0:
            result.situation = SituationType.ACTIVE_INTERACTION
            result.activity_level = ActivityLevel.HIGH
            result.priority = ContextPriority.ATTENTION
            result.recommended_mode = "track"
            return

        if result.people_count >= 4:
            result.situation = SituationType.ELEVATED_ACTIVITY
            result.activity_level = ActivityLevel.HIGH
            result.priority = ContextPriority.ATTENTION
            result.recommended_mode = "monitor"
            return

        if relation_count > 0:
            result.situation = SituationType.ACTIVE_INTERACTION
            result.activity_level = ActivityLevel.MODERATE
            result.priority = ContextPriority.ATTENTION
            result.recommended_mode = "observe"
            return

        if result.moving_people > 0:
            result.situation = SituationType.NORMAL_ACTIVITY
            result.activity_level = ActivityLevel.MODERATE
            result.priority = ContextPriority.NORMAL
            result.recommended_mode = "monitor"
            return

        if result.people_count > 0:
            result.situation = SituationType.PERSON_PRESENT
            result.activity_level = ActivityLevel.LOW
            result.priority = ContextPriority.NORMAL
            result.recommended_mode = "monitor"
            return

        result.situation = SituationType.IDLE
        result.activity_level = ActivityLevel.NONE
        result.priority = ContextPriority.NORMAL
        result.recommended_mode = "standby"

    def _record(self, context: PersonalContext) -> None:
        self.history.append(context)

        if len(self.history) > self.history_limit:
            self.history = self.history[-self.history_limit:]

    def recent(self, limit: int = 10):
        return self.history[-max(1, limit):]

    def reset(self) -> None:
        self.history.clear()
        self.last_context = None

    def status(self) -> Dict[str, Any]:
        return {
            "history_size": len(self.history),
            "has_context": self.last_context is not None,
            "last_context": (
                self.last_context.status()
                if self.last_context
                else None
            ),
        }


class AUREXUnifiedIntelligence:
    """
    Final fusion layer for Step 1.

    It creates one UnifiedWorldState from the outputs of
    AUREX perception, context, security, intent, scene,
    behavior, affect, hazard, memory and prediction systems.
    """

    def __init__(self):
        self.context_engine = AUREXPersonalContextEngine()

        self.history = []
        self.history_limit = 60

        self.current_state: Optional[UnifiedWorldState] = None

    def update(
        self,
        context: Any = None,
        human_states: Optional[Iterable[Any]] = None,
        relationships: Optional[Iterable[Any]] = None,
        scene: Any = None,
        security: Any = None,
        hazard: Any = None,
        behavior: Any = None,
        affect: Any = None,
        prediction: Any = None,
        intent: Any = None,
        multimodal: Any = None,
        memory: Any = None,
    ) -> UnifiedWorldState:

        personal = self.context_engine.analyze(
            context=context,
            human_states=human_states,
            relationships=relationships,
            scene=scene,
            security=security,
            hazard=hazard,
            behavior=behavior,
            affect=affect,
            prediction=prediction,
            intent=intent,
            multimodal=multimodal,
            memory=memory,
        )

        state = UnifiedWorldState(
            timestamp=time.time(),
            people_count=personal.people_count,
            object_count=personal.object_count,
            context_type=(
                _enum_value(
                    _get(context, "context_type", "unknown")
                )
            ),
            security_state=personal.security_state,
            security_level=personal.security_level,
            primary_intent=personal.primary_intent,
            multimodal_intent=personal.multimodal_intent,
            hazard_count=personal.hazard_count,
            highest_hazard=personal.highest_hazard,
            highest_hazard_severity=personal.highest_hazard_severity,
            behavior_anomaly_score=personal.behavior_anomaly_score,
            affect_state=personal.affect_state,
            prediction_type=personal.prediction_type,
            prediction_level=personal.prediction_level,
            environment_state=(
                _enum_value(
                    _get(memory, "environment_state", "unknown")
                )
            ),
            situation=personal.situation,
            activity_level=personal.activity_level,
            priority=personal.priority,
            confidence=personal.confidence,
            recommended_mode=personal.recommended_mode,
            metadata={
                "zone_counts": personal.zone_counts,
                "reasons": personal.reasons,
                "evidence_count": len(personal.evidence),
            },
        )

        self.history.append(state)

        if len(self.history) > self.history_limit:
            self.history = self.history[-self.history_limit:]

        self.current_state = state

        return state

    def reset(self) -> None:
        self.context_engine.reset()
        self.history.clear()
        self.current_state = None

    def recent(self, limit: int = 10):
        return self.history[-max(1, limit):]

    def status(self) -> Dict[str, Any]:
        return {
            "history_size": len(self.history),
            "has_current_state": self.current_state is not None,
            "current_state": (
                self.current_state.to_dict()
                if self.current_state
                else None
            ),
            "context_engine": self.context_engine.status(),
        }