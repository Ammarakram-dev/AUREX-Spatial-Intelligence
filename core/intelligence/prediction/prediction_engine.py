from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional

from .prediction_state import (
    PredictionLevel,
    PredictionType,
    PredictiveAssessment,
)


class AUREXPredictiveEngine:
    """
    Lightweight temporal trend reasoning.

    This engine detects observable patterns in AUREX history.
    It does not claim certainty about future events or human intent.
    """

    def __init__(
        self,
        history_window: int = 30,
        repeated_pattern_threshold: int = 3,
        hazard_escalation_threshold: int = 2,
    ):
        self.history_window = max(
            3,
            int(history_window),
        )

        self.repeated_pattern_threshold = max(
            2,
            int(repeated_pattern_threshold),
        )

        self.hazard_escalation_threshold = max(
            2,
            int(hazard_escalation_threshold),
        )

        self.assessments: List[PredictiveAssessment] = []

        self.latest: Optional[
            PredictiveAssessment
        ] = None

    @staticmethod
    def _safe_value(
        obj: Any,
        name: str,
        default: Any = None,
    ) -> Any:
        if obj is None:
            return default

        if isinstance(obj, dict):
            return obj.get(name, default)

        return getattr(obj, name, default)

    def _recent(
        self,
        memory: Any,
    ) -> List[Any]:
        history = self._safe_value(
            memory,
            "history",
            [],
        )

        try:
            return list(history)[-self.history_window:]
        except TypeError:
            return []

    def _events(
        self,
        memory: Any,
    ) -> List[Any]:
        events = self._safe_value(
            memory,
            "events",
            [],
        )

        try:
            return list(events)[-self.history_window:]
        except TypeError:
            return []

    def _event_type(
        self,
        event: Any,
    ) -> str:
        value = self._safe_value(
            event,
            "event_type",
            "unknown",
        )

        if hasattr(value, "value"):
            return str(value.value)

        return str(value).lower()

    def _hazard_counts(
        self,
        history: List[Any],
    ) -> List[int]:
        result = []

        for state in history:
            value = self._safe_value(
                state,
                "hazard_count",
                0,
            )

            try:
                result.append(int(value))
            except (TypeError, ValueError):
                result.append(0)

        return result

    def _behavior_counts(
        self,
        history: List[Any],
    ) -> List[int]:
        result = []

        for state in history:
            value = self._safe_value(
                state,
                "behavior_anomaly_count",
                0,
            )

            try:
                result.append(int(value))
            except (TypeError, ValueError):
                result.append(0)

        return result

    def _environment_states(
        self,
        history: List[Any],
    ) -> List[str]:
        result = []

        for state in history:
            value = self._safe_value(
                state,
                "environment_state",
                "unknown",
            )

            if hasattr(value, "value"):
                value = value.value

            result.append(str(value).lower())

        return result

    def _stable_state(
        self,
        history: List[Any],
    ) -> Optional[PredictiveAssessment]:
        if len(history) < 3:
            return None

        states = self._environment_states(
            history[-5:]
        )

        if not states:
            return None

        if len(set(states)) != 1:
            return None

        if states[-1] == "unknown":
            return None

        assessment = PredictiveAssessment(
            prediction_type=PredictionType.STABLE_STATE,
            level=PredictionLevel.NORMAL,
            description=(
                f"Environment has remained in "
                f"'{states[-1]}' for recent observations."
            ),
        )

        assessment.add_evidence(
            "temporal_stability",
            "Recent environment observations are consistent.",
            0.85,
            1.0,
        )

        assessment.reasons.append(
            "The same environment state persisted across recent observations."
        )

        assessment.calculate_confidence()

        return assessment

    def _activity_trend(
        self,
        history: List[Any],
    ) -> Optional[PredictiveAssessment]:
        if len(history) < 4:
            return None

        counts = []

        for state in history[-8:]:
            people = self._safe_value(
                state,
                "people_ids",
                [],
            )

            try:
                counts.append(len(people))
            except TypeError:
                counts.append(0)

        if len(counts) < 4:
            return None

        first_half = counts[: len(counts) // 2]
        second_half = counts[len(counts) // 2 :]

        first_average = (
            sum(first_half) / len(first_half)
        )

        second_average = (
            sum(second_half) / len(second_half)
        )

        if second_average <= first_average:
            return None

        assessment = PredictiveAssessment(
            prediction_type=PredictionType.INCREASING_ACTIVITY,
            level=PredictionLevel.LOW,
            description=(
                "Recent observations show increasing "
                "people/activity levels."
            ),
        )

        confidence = min(
            0.90,
            0.55 + (
                second_average - first_average
            ) * 0.12,
        )

        assessment.add_evidence(
            "activity_trend",
            "Observed people count increased over the recent window.",
            confidence,
            1.0,
        )

        assessment.reasons.append(
            "Recent activity is higher than the earlier part of the observation window."
        )

        assessment.calculate_confidence()

        return assessment

    def _repeated_events(
        self,
        memory: Any,
    ) -> Optional[PredictiveAssessment]:
        events = self._events(memory)

        if not events:
            return None

        counts = Counter(
            self._event_type(event)
            for event in events
        )

        repeated = [
            (event_type, count)
            for event_type, count in counts.items()
            if count >= self.repeated_pattern_threshold
        ]

        if not repeated:
            return None

        repeated.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        event_type, count = repeated[0]

        assessment = PredictiveAssessment(
            prediction_type=PredictionType.REPEATED_PATTERN,
            level=PredictionLevel.WARNING,
            description=(
                f"Repeated temporal event pattern detected: "
                f"{event_type} ({count} occurrences)."
            ),
        )

        assessment.add_evidence(
            "event_frequency",
            f"{event_type} occurred {count} times in recent memory.",
            min(0.95, 0.55 + count * 0.08),
            1.0,
            {
                "event_type": event_type,
                "count": count,
            },
        )

        assessment.reasons.append(
            "The same observable event has occurred repeatedly."
        )

        assessment.calculate_confidence()

        return assessment

    def _hazard_trend(
        self,
        history: List[Any],
    ) -> Optional[PredictiveAssessment]:
        counts = self._hazard_counts(history)

        if len(counts) < 4:
            return None

        recent = counts[-4:]

        increases = sum(
            1
            for index in range(1, len(recent))
            if recent[index] > recent[index - 1]
        )

        if increases < self.hazard_escalation_threshold:
            if max(recent) <= 0:
                return None

            if all(value > 0 for value in recent):
                assessment = PredictiveAssessment(
                    prediction_type=PredictionType.HAZARD_PERSISTENCE,
                    level=PredictionLevel.WARNING,
                    description=(
                        "Hazard activity has persisted across "
                        "recent observations."
                    ),
                )

                assessment.add_evidence(
                    "hazard_persistence",
                    "Hazard count remained above zero across recent observations.",
                    0.80,
                    1.0,
                )

                assessment.reasons.append(
                    "Hazard activity has not cleared from recent temporal memory."
                )

                assessment.calculate_confidence()

                return assessment

            return None

        assessment = PredictiveAssessment(
            prediction_type=PredictionType.HAZARD_ESCALATION,
            level=PredictionLevel.HIGH,
            description=(
                "Hazard activity is increasing across recent observations."
            ),
        )

        assessment.add_evidence(
            "hazard_trend",
            "Hazard count increased repeatedly in the recent window.",
            0.82,
            1.10,
        )

        assessment.reasons.append(
            "The observed hazard signal is increasing over time."
        )

        assessment.calculate_confidence()

        return assessment

    def _behavior_trend(
        self,
        history: List[Any],
    ) -> Optional[PredictiveAssessment]:
        counts = self._behavior_counts(history)

        if len(counts) < 4:
            return None

        recent = counts[-4:]

        if recent[-1] <= recent[0]:
            return None

        assessment = PredictiveAssessment(
            prediction_type=PredictionType.BEHAVIOR_ESCALATION,
            level=PredictionLevel.WARNING,
            description=(
                "Observable behavior-anomaly activity is increasing."
            ),
        )

        assessment.add_evidence(
            "behavior_trend",
            "Behavior anomaly count increased over recent observations.",
            0.75,
            1.0,
        )

        assessment.reasons.append(
            "Observable anomaly signals increased over time."
        )

        assessment.calculate_confidence()

        return assessment

    def _environment_transition(
        self,
        history: List[Any],
    ) -> Optional[PredictiveAssessment]:
        states = self._environment_states(history)

        if len(states) < 3:
            return None

        unique_recent = len(set(states[-5:]))

        if unique_recent < 2:
            return None

        assessment = PredictiveAssessment(
            prediction_type=PredictionType.ENVIRONMENT_TRANSITION,
            level=PredictionLevel.LOW,
            description=(
                "The environment is transitioning between "
                "multiple observed states."
            ),
        )

        assessment.add_evidence(
            "state_transition",
            "Multiple environment states were observed recently.",
            0.70,
            0.85,
        )

        assessment.reasons.append(
            "The environment has not remained in a single state."
        )

        assessment.calculate_confidence()

        return assessment

    def analyze(
        self,
        memory: Any,
    ) -> List[PredictiveAssessment]:
        history = self._recent(memory)

        assessments: List[PredictiveAssessment] = []

        detectors = [
            self._stable_state,
            self._activity_trend,
            self._hazard_trend,
            self._behavior_trend,
            self._environment_transition,
        ]

        for detector in detectors:
            assessment = detector(history)

            if assessment is not None:
                assessments.append(assessment)

        repeated = self._repeated_events(memory)

        if repeated is not None:
            assessments.append(repeated)

        priority = {
            PredictionLevel.HIGH: 4,
            PredictionLevel.WARNING: 3,
            PredictionLevel.LOW: 2,
            PredictionLevel.NORMAL: 1,
        }

        assessments.sort(
            key=lambda item: (
                priority[item.level],
                item.confidence,
            ),
            reverse=True,
        )

        self.assessments = assessments

        self.latest = (
            assessments[0]
            if assessments
            else PredictiveAssessment()
        )

        return assessments

    def highest_risk(
        self,
    ) -> PredictiveAssessment:
        if not self.assessments:
            return PredictiveAssessment()

        return max(
            self.assessments,
            key=lambda item: (
                {
                    PredictionLevel.NORMAL: 1,
                    PredictionLevel.LOW: 2,
                    PredictionLevel.WARNING: 3,
                    PredictionLevel.HIGH: 4,
                }[item.level],
                item.confidence,
            ),
        )

    def reset(self) -> None:
        self.assessments.clear()
        self.latest = None

    def status(self) -> Dict[str, Any]:
        return {
            "assessment_count": len(
                self.assessments
            ),
            "latest": (
                self.latest.to_dict()
                if self.latest
                else None
            ),
        }