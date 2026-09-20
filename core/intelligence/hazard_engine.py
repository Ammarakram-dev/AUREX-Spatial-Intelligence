"""
AUREX Spatial Intelligence
Predictive Hazard Engine

Phase 27
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from core.intelligence.hazard import (
    HazardAssessment,
    HazardEvidence,
    HazardResponse,
    HazardSeverity,
    HazardType,
)


class AUREXHazardEngine:

    def __init__(
        self,
        warning_threshold: float = 0.50,
        high_threshold: float = 0.70,
        critical_threshold: float = 0.88,
        prolonged_lying_frames: int = 30,
    ):
        self.warning_threshold = warning_threshold
        self.high_threshold = high_threshold
        self.critical_threshold = critical_threshold
        self.prolonged_lying_frames = prolonged_lying_frames

        self.history: List[HazardAssessment] = []

        self._lying_frames: Dict[str, int] = {}

    # =========================================================
    # NORMALIZATION
    # =========================================================

    @staticmethod
    def _value(
        obj: Any,
        name: str,
        default: Any = None,
    ):
        if obj is None:
            return default

        if isinstance(obj, dict):
            return obj.get(name, default)

        return getattr(
            obj,
            name,
            default,
        )

    @staticmethod
    def _text(
        obj: Any,
        name: str,
        default: str = "",
    ) -> str:
        value = AUREXHazardEngine._value(
            obj,
            name,
            default,
        )

        if hasattr(value, "value"):
            return str(value.value)

        return str(value)

    @staticmethod
    def _float(
        obj: Any,
        name: str,
        default: float = 0.0,
    ) -> float:
        value = AUREXHazardEngine._value(
            obj,
            name,
            default,
        )

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return default

    # =========================================================
    # SEVERITY
    # =========================================================

    def _severity(
        self,
        confidence: float,
    ) -> HazardSeverity:

        if confidence >= self.critical_threshold:
            return HazardSeverity.CRITICAL

        if confidence >= self.high_threshold:
            return HazardSeverity.HIGH

        if confidence >= self.warning_threshold:
            return HazardSeverity.WARNING

        if confidence > 0.0:
            return HazardSeverity.LOW

        return HazardSeverity.NORMAL

    # =========================================================
    # RESPONSE
    # =========================================================

    @staticmethod
    def _response(
        severity: HazardSeverity,
    ) -> HazardResponse:

        if severity == HazardSeverity.CRITICAL:
            return HazardResponse.EMERGENCY_WORKFLOW

        if severity == HazardSeverity.HIGH:
            return HazardResponse.REQUEST_CONFIRMATION

        if severity == HazardSeverity.WARNING:
            return HazardResponse.ALERT

        if severity == HazardSeverity.LOW:
            return HazardResponse.MONITOR

        return HazardResponse.NONE

    # =========================================================
    # FALL RISK
    # =========================================================

    def detect_fall_risk(
        self,
        human_states: Optional[Iterable[Any]] = None,
    ) -> Optional[HazardAssessment]:

        states = list(
            human_states or []
        )

        candidates = []

        for state in states:

            posture = self._text(
                state,
                "posture",
            ).lower()

            movement_distance = self._float(
                state,
                "movement_distance",
            )

            person_id = str(
                self._value(
                    state,
                    "person_id",
                    "unknown",
                )
            )

            if posture in {
                "lying",
                "potential_fall",
                "fall",
            }:

                candidates.append(
                    (
                        person_id,
                        posture,
                        movement_distance,
                    )
                )

        if not candidates:
            return None

        assessment = HazardAssessment(
            hazard_type=HazardType.FALL_RISK,
            severity=HazardSeverity.WARNING,
            confidence=0.0,
            response=HazardResponse.ALERT,
        )

        for person_id, posture, movement_distance in candidates:

            confidence = 0.65

            if posture in {
                "fall",
                "potential_fall",
            }:
                confidence = 0.85

            if movement_distance > 0.25:
                confidence += 0.05

            confidence = min(
                1.0,
                confidence,
            )

            assessment.add_evidence(
                HazardEvidence(
                    source="posture",
                    description=(
                        f"Person {person_id} has "
                        f"posture state '{posture}'."
                    ),
                    confidence=confidence,
                    weight=1.0,
                    metadata={
                        "person_id": person_id,
                        "movement_distance": movement_distance,
                    },
                )
            )

            assessment.person_ids.append(
                person_id
            )

            assessment.reasons.append(
                f"Potential fall-related posture detected for {person_id}."
            )

        assessment.confidence = min(
            1.0,
            sum(
                item.score()
                for item in assessment.evidence
            )
            / max(
                1,
                len(assessment.evidence),
            ),
        )

        assessment.severity = self._severity(
            assessment.confidence
        )

        assessment.response = self._response(
            assessment.severity
        )

        return assessment

    # =========================================================
    # APPROACHING PERSON
    # =========================================================

    def detect_rapid_approach(
        self,
        human_states: Optional[Iterable[Any]] = None,
        relationships: Optional[Iterable[Any]] = None,
    ) -> Optional[HazardAssessment]:

        states = list(
            human_states or []
        )

        relations = list(
            relationships or []
        )

        approaching_ids = []

        for relation in relations:

            relation_type = self._text(
                relation,
                "relationship",
            ).lower()

            source_id = str(
                self._value(
                    relation,
                    "source_id",
                    "unknown",
                )
            )

            target_id = str(
                self._value(
                    relation,
                    "target_id",
                    "unknown",
                )
            )

            if relation_type == "approaching":

                approaching_ids.extend(
                    [
                        source_id,
                        target_id,
                    ]
                )

        for state in states:

            direction = self._text(
                state,
                "movement_direction",
            ).lower()

            person_id = str(
                self._value(
                    state,
                    "person_id",
                    "unknown",
                )
            )

            movement_distance = self._float(
                state,
                "movement_distance",
            )

            if (
                "approach" in direction
                and movement_distance > 0.05
            ):
                approaching_ids.append(
                    person_id
                )

        approaching_ids = list(
            dict.fromkeys(
                approaching_ids
            )
        )

        if not approaching_ids:
            return None

        assessment = HazardAssessment(
            hazard_type=HazardType.RAPID_APPROACH,
            severity=HazardSeverity.WARNING,
            confidence=0.0,
            response=HazardResponse.ALERT,
            person_ids=approaching_ids,
        )

        assessment.add_evidence(
            HazardEvidence(
                source="movement",
                description=(
                    "Approaching movement detected."
                ),
                confidence=0.65,
            )
        )

        assessment.reasons.append(
            "One or more entities are approaching."
        )

        assessment.confidence = 0.65

        assessment.severity = self._severity(
            assessment.confidence
        )

        assessment.response = self._response(
            assessment.severity
        )

        return assessment

    # =========================================================
    # ABNORMAL MOVEMENT
    # =========================================================

    def detect_abnormal_movement(
        self,
        human_states: Optional[Iterable[Any]] = None,
    ) -> Optional[HazardAssessment]:

        states = list(
            human_states or []
        )

        suspicious = []

        for state in states:

            movement_distance = self._float(
                state,
                "movement_distance",
            )

            direction = self._text(
                state,
                "movement_direction",
            ).lower()

            person_id = str(
                self._value(
                    state,
                    "person_id",
                    "unknown",
                )
            )

            if movement_distance > 0.50:
                suspicious.append(
                    (
                        person_id,
                        movement_distance,
                        direction,
                    )
                )

        if not suspicious:
            return None

        assessment = HazardAssessment(
            hazard_type=HazardType.ABNORMAL_MOVEMENT,
            severity=HazardSeverity.WARNING,
            confidence=0.0,
            response=HazardResponse.ALERT,
        )

        for (
            person_id,
            movement_distance,
            direction,
        ) in suspicious:

            confidence = min(
                0.90,
                0.50 + movement_distance * 0.30,
            )

            assessment.add_evidence(
                HazardEvidence(
                    source="movement",
                    description=(
                        f"Unusually large movement "
                        f"detected for {person_id}."
                    ),
                    confidence=confidence,
                    metadata={
                        "person_id": person_id,
                        "movement_distance": movement_distance,
                        "direction": direction,
                    },
                )
            )

            assessment.person_ids.append(
                person_id
            )

            assessment.reasons.append(
                f"Large movement detected for {person_id}."
            )

        assessment.confidence = min(
            1.0,
            sum(
                item.score()
                for item in assessment.evidence
            )
            / len(assessment.evidence),
        )

        assessment.severity = self._severity(
            assessment.confidence
        )

        assessment.response = self._response(
            assessment.severity
        )

        return assessment

    # =========================================================
    # PROLONGED LYING
    # =========================================================

    def detect_prolonged_lying(
        self,
        human_states: Optional[Iterable[Any]] = None,
    ) -> Optional[HazardAssessment]:

        states = list(
            human_states or []
        )

        candidates = []

        active_ids = set()

        for state in states:

            person_id = str(
                self._value(
                    state,
                    "person_id",
                    "unknown",
                )
            )

            active_ids.add(
                person_id
            )

            posture = self._text(
                state,
                "posture",
            ).lower()

            if posture == "lying":

                self._lying_frames[
                    person_id
                ] = (
                    self._lying_frames.get(
                        person_id,
                        0,
                    )
                    + 1
                )

            else:

                self._lying_frames[
                    person_id
                ] = 0

            if (
                self._lying_frames[
                    person_id
                ]
                >= self.prolonged_lying_frames
            ):

                candidates.append(
                    person_id
                )

        stale_ids = [
            person_id
            for person_id in self._lying_frames
            if person_id not in active_ids
        ]

        for person_id in stale_ids:
            del self._lying_frames[
                person_id
            ]

        if not candidates:
            return None

        assessment = HazardAssessment(
            hazard_type=HazardType.PROLONGED_LYING,
            severity=HazardSeverity.HIGH,
            confidence=0.0,
            response=HazardResponse.REQUEST_CONFIRMATION,
            person_ids=candidates,
        )

        for person_id in candidates:

            assessment.add_evidence(
                HazardEvidence(
                    source="temporal_posture",
                    description=(
                        f"Person {person_id} has remained "
                        "in a lying posture for an extended period."
                    ),
                    confidence=0.80,
                    metadata={
                        "person_id": person_id,
                        "frames": self._lying_frames[
                            person_id
                        ],
                    },
                )
            )

        assessment.reasons.append(
            "Prolonged lying posture detected."
        )

        assessment.confidence = 0.80

        assessment.severity = self._severity(
            assessment.confidence
        )

        assessment.response = self._response(
            assessment.severity
        )

        return assessment

    # =========================================================
    # CROWDING
    # =========================================================

    def detect_crowding(
        self,
        human_states: Optional[Iterable[Any]] = None,
    ) -> Optional[HazardAssessment]:

        states = list(
            human_states or []
        )

        if len(states) < 4:
            return None

        confidence = min(
            0.90,
            0.45 + (len(states) - 3) * 0.10,
        )

        person_ids = [
            str(
                self._value(
                    state,
                    "person_id",
                    "unknown",
                )
            )
            for state in states
        ]

        assessment = HazardAssessment(
            hazard_type=HazardType.CROWDING,
            severity=self._severity(
                confidence
            ),
            confidence=confidence,
            response=self._response(
                self._severity(confidence)
            ),
            person_ids=person_ids,
        )

        assessment.add_evidence(
            HazardEvidence(
                source="population",
                description=(
                    f"{len(states)} people detected "
                    "within the monitored scene."
                ),
                confidence=confidence,
            )
        )

        assessment.reasons.append(
            "Multiple people detected in the monitored scene."
        )

        return assessment

    # =========================================================
    # WORLD ANALYSIS
    # =========================================================

    def analyze(
        self,
        human_states: Optional[Iterable[Any]] = None,
        relationships: Optional[Iterable[Any]] = None,
        context: Optional[Any] = None,
    ) -> List[HazardAssessment]:

        states = list(
            human_states or []
        )

        relations = list(
            relationships or []
        )

        assessments = []

        detectors = [
            lambda: self.detect_fall_risk(
                states
            ),
            lambda: self.detect_rapid_approach(
                states,
                relations,
            ),
            lambda: self.detect_abnormal_movement(
                states
            ),
            lambda: self.detect_prolonged_lying(
                states
            ),
            lambda: self.detect_crowding(
                states
            ),
        ]

        for detector in detectors:

            result = detector()

            if result is not None:
                assessments.append(
                    result
                )

        # Context-level incident signal.
        context_type = self._text(
            context,
            "context_type",
        ).lower()

        if (
            "potential_incident"
            in context_type
        ):

            assessment = HazardAssessment(
                hazard_type=(
                    HazardType.POTENTIAL_INCIDENT
                ),
                severity=HazardSeverity.WARNING,
                confidence=0.60,
                response=HazardResponse.ALERT,
            )

            assessment.add_evidence(
                HazardEvidence(
                    source="context_engine",
                    description=(
                        "Context engine reported a "
                        "potential incident."
                    ),
                    confidence=0.60,
                )
            )

            assessment.reasons.append(
                "Potential incident context detected."
            )

            assessments.append(
                assessment
            )

        # Sort by severity/confidence for internal processing.
        severity_order = {
            HazardSeverity.NORMAL: 0,
            HazardSeverity.LOW: 1,
            HazardSeverity.WARNING: 2,
            HazardSeverity.HIGH: 3,
            HazardSeverity.CRITICAL: 4,
        }

        assessments.sort(
            key=lambda item: (
                severity_order[item.severity],
                item.confidence,
            ),
            reverse=True,
        )

        self.history.extend(
            assessments
        )

        if len(self.history) > 100:
            self.history = self.history[-100:]

        return assessments

    def highest_risk(
        self,
        assessments: Optional[
            Iterable[HazardAssessment]
        ] = None,
    ) -> Optional[HazardAssessment]:

        items = list(
            assessments
            if assessments is not None
            else self.history
        )

        if not items:
            return None

        severity_order = {
            HazardSeverity.NORMAL: 0,
            HazardSeverity.LOW: 1,
            HazardSeverity.WARNING: 2,
            HazardSeverity.HIGH: 3,
            HazardSeverity.CRITICAL: 4,
        }

        return max(
            items,
            key=lambda item: (
                severity_order[item.severity],
                item.confidence,
            ),
        )

    def reset(self):

        self.history.clear()
        self._lying_frames.clear()

    def status(self) -> Dict[str, Any]:

        highest = self.highest_risk()

        return {
            "warning_threshold": self.warning_threshold,
            "high_threshold": self.high_threshold,
            "critical_threshold": self.critical_threshold,
            "history_size": len(self.history),
            "tracked_lying_people": len(
                self._lying_frames
            ),
            "highest_risk": (
                highest.to_dict()
                if highest
                else None
            ),
        }