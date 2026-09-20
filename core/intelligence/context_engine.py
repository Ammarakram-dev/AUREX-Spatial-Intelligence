"""
AUREX Spatial Intelligence
Context Intelligence Engine

Phase 18
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from core.intelligence.context import (
    AUREXContext,
    ContextType,
)


class AUREXContextEngine:
    """
    Converts human states and spatial relationships into
    a unified environmental context.
    """

    def __init__(
        self,
        moving_threshold: float = 0.05,
        interaction_confidence: float = 0.65,
    ) -> None:

        self.moving_threshold = float(moving_threshold)
        self.interaction_confidence = float(interaction_confidence)

    @staticmethod
    def _get(obj: Any, name: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(name, default)

        return getattr(obj, name, default)

    @staticmethod
    def _safe_confidence(value: Any, default: float = 1.0) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = default

        return max(0.0, min(1.0, value))

    @staticmethod
    def _normalize(value: Any) -> str:
        if value is None:
            return ""

        if hasattr(value, "value"):
            value = value.value

        return str(value).strip().lower()

    def _movement_value(self, person: Any) -> float:
        value = self._get(person, "movement_distance", 0.0)

        try:
            return abs(float(value))
        except (TypeError, ValueError):
            return 0.0

    def _posture(self, person: Any) -> str:
        posture = self._get(person, "posture", "")

        return self._normalize(posture)

    def _person_id(self, person: Any) -> str:
        value = self._get(person, "person_id", None)

        if value is None:
            value = self._get(person, "id", None)

        if value is None:
            return "unknown"

        return str(value)

    def _person_confidence(self, person: Any) -> float:
        value = self._get(
            person,
            "detection_confidence",
            self._get(person, "confidence", 1.0),
        )

        return self._safe_confidence(value)

    def _relationship_value(self, relationship: Any) -> str:
        value = self._get(
            relationship,
            "relationship",
            self._get(relationship, "type", ""),
        )

        return self._normalize(value)

    def _relationship_confidence(self, relationship: Any) -> float:
        return self._safe_confidence(
            self._get(relationship, "confidence", 1.0)
        )

    def analyze(
        self,
        human_states: Optional[Iterable[Any]] = None,
        relationships: Optional[Iterable[Any]] = None,
    ) -> AUREXContext:
        """
        Analyze human states and spatial relationships.
        """

        people: List[Any] = list(human_states or [])
        relations: List[Any] = list(relationships or [])

        context = AUREXContext()

        context.people_count = len(people)
        context.relationship_count = len(relations)

        if not people:
            context.context_type = ContextType.NORMAL
            context.confidence = 0.95

            context.add_evidence(
                source="people",
                value="none_detected",
                confidence=0.95,
            )

            return context

        for person in people:

            person_id = self._person_id(person)

            context.active_people.append(person_id)

            confidence = self._person_confidence(person)

            movement_distance = self._movement_value(person)

            posture = self._posture(person)

            zone = self._get(person, "zone", None)

            if zone:
                zone = str(zone)

                context.zone_counts[zone] = (
                    context.zone_counts.get(zone, 0) + 1
                )

            if movement_distance > self.moving_threshold:

                context.moving_people.append(person_id)

                context.add_evidence(
                    source="movement",
                    value=person_id,
                    confidence=confidence,
                    metadata={
                        "movement_distance": movement_distance,
                    },
                )

            else:

                context.stationary_people.append(person_id)

            if posture in {
                "sitting",
                "seated",
            }:

                context.seated_people.append(person_id)

                context.add_evidence(
                    source="posture",
                    value="sitting",
                    confidence=confidence,
                    metadata={
                        "person_id": person_id,
                    },
                )

            elif posture in {
                "lying",
                "fallen",
                "fall",
            }:

                context.lying_people.append(person_id)

                context.add_evidence(
                    source="posture",
                    value="lying",
                    confidence=confidence,
                    metadata={
                        "person_id": person_id,
                    },
                )

            direction = self._normalize(
                self._get(person, "movement_direction", "")
            )

            if direction in {
                "approaching",
                "toward",
                "towards",
            }:

                context.approaching_people.append(person_id)

            elif direction in {
                "moving_away",
                "away",
                "departing",
            }:

                context.moving_away_people.append(person_id)

        for relationship in relations:

            relationship_type = self._relationship_value(
                relationship
            )

            confidence = self._relationship_confidence(
                relationship
            )

            source_id = self._get(
                relationship,
                "source_id",
                "unknown",
            )

            target_id = self._get(
                relationship,
                "target_id",
                "unknown",
            )

            if relationship_type in {
                "approaching",
            }:

                person_id = str(source_id)

                if person_id not in context.approaching_people:

                    context.approaching_people.append(
                        person_id
                    )

                context.add_evidence(
                    source="relationship",
                    value="approaching",
                    confidence=confidence,
                    metadata={
                        "source_id": str(source_id),
                        "target_id": str(target_id),
                    },
                )

            elif relationship_type in {
                "moving_away",
            }:

                person_id = str(source_id)

                if person_id not in context.moving_away_people:

                    context.moving_away_people.append(
                        person_id
                    )

                context.add_evidence(
                    source="relationship",
                    value="moving_away",
                    confidence=confidence,
                    metadata={
                        "source_id": str(source_id),
                        "target_id": str(target_id),
                    },
                )

            elif relationship_type in {
                "near",
                "spatially_near",
                "same_zone",
            }:

                context.add_evidence(
                    source="relationship",
                    value=relationship_type,
                    confidence=confidence,
                    metadata={
                        "source_id": str(source_id),
                        "target_id": str(target_id),
                    },
                )

        self._infer_context_type(context)

        self._calculate_confidence(context)

        return context

    def _infer_context_type(
        self,
        context: AUREXContext,
    ) -> None:

        if context.lying_people:

            context.context_type = ContextType.POTENTIAL_INCIDENT

            return

        if context.approaching_people:

            context.context_type = ContextType.PERSON_APPROACHING

            return

        if context.moving_away_people:

            context.context_type = ContextType.PERSON_MOVING_AWAY

            return

        if context.relationship_count > 0:

            context.context_type = (
                ContextType.SPATIAL_INTERACTION
            )

            return

        if context.people_count > 1:

            context.context_type = ContextType.MULTIPLE_PEOPLE

            return

        if context.seated_people:

            context.context_type = ContextType.PERSON_SITTING

            return

        if context.moving_people:

            context.context_type = ContextType.PERSON_MOVING

            return

        if context.stationary_people:

            context.context_type = (
                ContextType.PERSON_STATIONARY
            )

            return

        context.context_type = ContextType.PERSON_PRESENT

    def _calculate_confidence(
        self,
        context: AUREXContext,
    ) -> None:

        evidence = context.evidence

        if not evidence:

            context.confidence = 0.0

            return

        average = sum(
            item.confidence
            for item in evidence
        ) / len(evidence)

        support_bonus = min(
            0.15,
            max(0, len(evidence) - 1) * 0.025,
        )

        context.confidence = max(
            0.0,
            min(
                1.0,
                average + support_bonus,
            ),
        )

    def analyze_tracked_people(
        self,
        tracked_people: Iterable[Any],
        relationships: Optional[Iterable[Any]] = None,
    ) -> AUREXContext:
        """
        Convenience adapter for live tracked people.

        Converts tracker objects into the context model
        without requiring a separate HumanSpatialState.
        """

        return self.analyze(
            human_states=list(tracked_people),
            relationships=relationships,
        )

    def status(self) -> Dict[str, Any]:
        return {
            "engine": "AUREXContextEngine",
            "moving_threshold": self.moving_threshold,
            "interaction_confidence": self.interaction_confidence,
            "status": "ready",
        }