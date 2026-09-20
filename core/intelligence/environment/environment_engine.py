from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .environment_state import AUREXEnvironmentState, EnvironmentState


class AUREXEnvironmentEngine:
    """
    Adaptive fusion layer for the AUREX physical-world intelligence stack.

    This engine does not replace perception modules.
    It combines their outputs into one environment-level state.
    """

    def __init__(
        self,
        history_limit: int = 60,
        hazard_threshold: float = 0.50,
        emergency_threshold: float = 0.85,
    ):
        self.history_limit = max(1, int(history_limit))
        self.hazard_threshold = float(hazard_threshold)
        self.emergency_threshold = float(emergency_threshold)

        self.history: List[AUREXEnvironmentState] = []
        self.latest: Optional[AUREXEnvironmentState] = None

    @staticmethod
    def _safe_value(obj: Any, name: str, default: Any = None) -> Any:
        if obj is None:
            return default

        if isinstance(obj, dict):
            return obj.get(name, default)

        return getattr(obj, name, default)

    @staticmethod
    def _enum_value(value: Any, default: str = "unknown") -> str:
        if value is None:
            return default

        if hasattr(value, "value"):
            return str(value.value)

        return str(value).lower()

    @staticmethod
    def _count_items(value: Any) -> int:
        if value is None:
            return 0

        try:
            return len(value)
        except TypeError:
            return 0

    def _extract_people(self, human_states: Any) -> List[Any]:
        if human_states is None:
            return []

        if isinstance(human_states, dict):
            return list(human_states.values())

        try:
            return list(human_states)
        except TypeError:
            return []

    def _extract_hazard_count(self, hazards: Any) -> int:
        if hazards is None:
            return 0

        if isinstance(hazards, dict):
            return len(hazards)

        try:
            return len(hazards)
        except TypeError:
            return 1

    def _hazard_confidence(self, hazard: Any) -> float:
        value = self._safe_value(hazard, "confidence", 0.0)

        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0

    def _hazard_severity(self, hazard: Any) -> str:
        value = self._safe_value(hazard, "severity", "normal")
        return self._enum_value(value, "normal")

    def _security_value(self, security: Any, name: str, default: Any) -> Any:
        value = self._safe_value(security, name, default)

        if hasattr(value, "value"):
            return value.value

        return value

    def _intent_value(self, intent: Any, name: str, default: str = "unknown") -> str:
        if intent is None:
            return default

        value = self._safe_value(intent, name, default)

        if hasattr(value, "value"):
            return str(value.value)

        return str(value)

    def _build_people_context(
        self,
        result: AUREXEnvironmentState,
        human_states: Iterable[Any],
    ) -> None:
        people = list(human_states)

        result.people_count = len(people)

        for person in people:
            movement_distance = self._safe_value(
                person,
                "movement_distance",
                0.0,
            )

            movement_direction = str(
                self._safe_value(
                    person,
                    "movement_direction",
                    "",
                )
                or ""
            ).lower()

            posture = self._enum_value(
                self._safe_value(person, "posture", "unknown"),
                "unknown",
            )

            try:
                movement_distance = float(movement_distance)
            except (TypeError, ValueError):
                movement_distance = 0.0

            if movement_distance > 0.05 or any(
                term in movement_direction
                for term in ("moving", "approach", "away", "left", "right")
            ):
                result.moving_people += 1
            else:
                result.stationary_people += 1

            if posture in {"sitting", "seated"}:
                result.seated_people += 1

            if posture in {"lying", "potential_fall"}:
                result.lying_people += 1

        if result.people_count == 0:
            return

        if result.people_count == 1:
            result.add_evidence(
                "people",
                "One person is present in the observed environment.",
                0.85,
                1.0,
            )
        else:
            result.add_evidence(
                "people",
                f"{result.people_count} people are present.",
                min(0.95, 0.70 + result.people_count * 0.05),
                1.0,
            )

        if result.moving_people:
            result.add_evidence(
                "movement",
                f"{result.moving_people} person(s) show movement.",
                min(0.95, 0.60 + result.moving_people * 0.08),
                0.90,
            )

        if result.lying_people:
            result.add_evidence(
                "posture",
                f"{result.lying_people} person(s) are in a lying posture.",
                0.80,
                1.0,
            )

    def _build_relationship_context(
        self,
        result: AUREXEnvironmentState,
        relationships: Any,
    ) -> None:
        if relationships is None:
            return

        if isinstance(relationships, dict):
            items = list(relationships.values())
        else:
            try:
                items = list(relationships)
            except TypeError:
                items = []

        result.relationship_count = len(items)

        if items:
            result.add_evidence(
                "spatial_relationships",
                f"{len(items)} spatial relationship(s) are active.",
                min(0.95, 0.60 + len(items) * 0.04),
                0.85,
            )

    def _build_object_context(
        self,
        result: AUREXEnvironmentState,
        objects: Any,
    ) -> None:
        if objects is None:
            return

        if isinstance(objects, dict):
            items = list(objects.values())
        else:
            try:
                items = list(objects)
            except TypeError:
                items = []

        result.object_count = len(items)

        if result.object_count:
            result.add_evidence(
                "scene",
                f"{result.object_count} scene object(s) are visible.",
                min(0.95, 0.55 + result.object_count * 0.025),
                0.75,
            )

    def _build_behavior_context(
        self,
        result: AUREXEnvironmentState,
        behavior: Any,
    ) -> None:
        if behavior is None:
            return

        anomalies = self._safe_value(behavior, "anomalies", [])

        try:
            result.behavior_anomaly_count = len(anomalies)
        except TypeError:
            result.behavior_anomaly_count = 0

        global_score = self._safe_value(
            behavior,
            "global_anomaly_score",
            0.0,
        )

        try:
            global_score = float(global_score)
        except (TypeError, ValueError):
            global_score = 0.0

        if result.behavior_anomaly_count or global_score >= self.hazard_threshold:
            result.add_evidence(
                "behavior",
                "Observable behavioral anomaly signals are present.",
                max(0.50, min(1.0, global_score)),
                0.95,
            )

    def _build_hazard_context(
        self,
        result: AUREXEnvironmentState,
        hazards: Any,
    ) -> None:
        if hazards is None:
            return

        if isinstance(hazards, dict):
            items = list(hazards.values())
        else:
            try:
                items = list(hazards)
            except TypeError:
                items = [hazards]

        result.hazard_count = len(items)

        highest_confidence = 0.0
        critical = False
        warning = False

        for hazard in items:
            confidence = self._hazard_confidence(hazard)
            severity = self._hazard_severity(hazard)

            highest_confidence = max(highest_confidence, confidence)

            if severity in {"critical", "high"}:
                critical = True

            if severity in {"warning", "high", "critical"}:
                warning = True

        if highest_confidence >= self.hazard_threshold or warning:
            result.add_evidence(
                "hazard",
                f"{result.hazard_count} hazard assessment(s) are active.",
                highest_confidence,
                1.0,
            )

        if critical:
            result.add_evidence(
                "critical_hazard",
                "At least one hazard assessment has high or critical severity.",
                max(0.80, highest_confidence),
                1.20,
            )

    def _build_security_context(
        self,
        result: AUREXEnvironmentState,
        security: Any,
    ) -> None:
        if security is None:
            return

        result.security_state = self._security_value(
            security,
            "state",
            "unknown",
        )

        result.security_level = self._security_value(
            security,
            "level",
            "low",
        )

        state = str(result.security_state).lower()
        level = str(result.security_level).lower()

        if state in {"verifying", "suspicious", "denied", "locked"}:
            result.add_evidence(
                "security",
                f"Security state is {state}.",
                0.80,
                1.0,
            )

        if level in {"high", "critical"}:
            result.add_evidence(
                "security_level",
                f"Security level is {level}.",
                0.85,
                1.1,
            )

    def _build_intent_context(
        self,
        result: AUREXEnvironmentState,
        voice_command: Any,
        multimodal_intent: Any,
    ) -> None:
        if voice_command is not None:
            result.voice_intent = self._intent_value(
                voice_command,
                "intent",
                "unknown",
            )

            if result.voice_intent != "unknown":
                result.add_evidence(
                    "voice",
                    f"Voice intent detected: {result.voice_intent}.",
                    self._safe_value(
                        voice_command,
                        "confidence",
                        0.70,
                    ),
                    0.70,
                )

        if multimodal_intent is not None:
            result.multimodal_intent = self._intent_value(
                multimodal_intent,
                "intent",
                "unknown",
            )

            if result.multimodal_intent == "unknown":
                result.multimodal_intent = self._intent_value(
                    multimodal_intent,
                    "primary",
                    "unknown",
                )

            if result.multimodal_intent != "unknown":
                confidence = self._safe_value(
                    multimodal_intent,
                    "confidence",
                    0.70,
                )

                result.add_evidence(
                    "multimodal_intent",
                    f"Multimodal intent detected: {result.multimodal_intent}.",
                    confidence,
                    0.90,
                )

    def _build_affect_context(
        self,
        result: AUREXEnvironmentState,
        affect: Any,
    ) -> None:
        if affect is None:
            return

        value = self._safe_value(affect, "emotion", None)

        if value is None:
            value = self._safe_value(affect, "affect", None)

        if value is None:
            value = self._safe_value(affect, "state", None)

        if value is None:
            return

        result.visible_affect = self._enum_value(value)

        if result.visible_affect != "unknown":
            confidence = self._safe_value(
                affect,
                "confidence",
                0.50,
            )

            result.add_evidence(
                "visible_affect",
                f"Visible facial affect estimate: {result.visible_affect}.",
                confidence,
                0.40,
            )

    def _determine_state(self, result: AUREXEnvironmentState) -> None:
        security_state = str(result.security_state).lower()
        security_level = str(result.security_level).lower()

        if (
            result.hazard_count
            and any(
                "critical_hazard" == evidence.source
                for evidence in result.evidence
            )
        ):
            result.state = EnvironmentState.EMERGENCY_CONTEXT
            result.reasons.append(
                "A high or critical hazard signal is active."
            )
            return

        if security_state in {"denied", "locked", "suspicious"}:
            result.state = EnvironmentState.SECURITY_VERIFICATION
            result.reasons.append(
                f"Security requires attention: {security_state}."
            )
            return

        if (
            result.hazard_count
            and any(
                evidence.source == "hazard"
                for evidence in result.evidence
            )
        ):
            result.state = EnvironmentState.POTENTIAL_HAZARD
            result.reasons.append(
                "One or more hazard assessments require monitoring."
            )
            return

        if result.people_count >= 2:
            result.state = EnvironmentState.MULTI_PERSON
            result.reasons.append(
                "Multiple people are visible in the environment."
            )

            if result.moving_people:
                result.state = EnvironmentState.PEOPLE_ACTIVE
                result.reasons.append(
                    "Movement is active among the observed people."
                )

            return

        if result.relationship_count and result.object_count:
            result.state = EnvironmentState.OBJECT_INTERACTION
            result.reasons.append(
                "Spatial relationships and scene objects are simultaneously active."
            )
            return

        if result.people_count == 1:
            if result.moving_people:
                result.state = EnvironmentState.PEOPLE_ACTIVE
                result.reasons.append(
                    "A person is present and movement is detected."
                )
            else:
                result.state = EnvironmentState.PERSON_PRESENT
                result.reasons.append(
                    "A person is present without significant movement."
                )
            return

        if result.object_count:
            result.state = EnvironmentState.CALM
            result.reasons.append(
                "Objects are visible without a higher-priority event."
            )
            return

        result.state = EnvironmentState.CALM
        result.reasons.append(
            "No higher-priority environmental event is currently detected."
        )

    def analyze(
        self,
        human_states: Any = None,
        objects: Any = None,
        relationships: Any = None,
        behavior: Any = None,
        hazards: Any = None,
        security: Any = None,
        voice_command: Any = None,
        multimodal_intent: Any = None,
        affect: Any = None,
    ) -> AUREXEnvironmentState:
        result = AUREXEnvironmentState()

        people = self._extract_people(human_states)

        self._build_people_context(result, people)
        self._build_object_context(result, objects)
        self._build_relationship_context(result, relationships)
        self._build_behavior_context(result, behavior)
        self._build_hazard_context(result, hazards)
        self._build_security_context(result, security)
        self._build_intent_context(
            result,
            voice_command,
            multimodal_intent,
        )
        self._build_affect_context(result, affect)

        self._determine_state(result)
        result.calculate_confidence()

        result.metadata.update(
            {
                "history_length": len(self.history),
                "evidence_count": len(result.evidence),
                "fusion_sources": [
                    evidence.source
                    for evidence in result.evidence
                ],
            }
        )

        self.history.append(result)

        if len(self.history) > self.history_limit:
            self.history = self.history[-self.history_limit :]

        self.latest = result

        return result

    def stable_state(self, frames: int = 3) -> EnvironmentState:
        if not self.history:
            return EnvironmentState.UNKNOWN

        frames = max(1, int(frames))
        recent = self.history[-frames:]

        if len(recent) < frames:
            return EnvironmentState.UNKNOWN

        first = recent[0].state

        if all(item.state == first for item in recent):
            return first

        return EnvironmentState.UNKNOWN

    def reset(self) -> None:
        self.history.clear()
        self.latest = None

    def status(self) -> Dict[str, Any]:
        return {
            "history_length": len(self.history),
            "latest": self.latest.to_dict() if self.latest else None,
            "stable_state": self.stable_state().value,
        }