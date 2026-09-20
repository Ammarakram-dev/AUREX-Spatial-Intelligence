from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from vision.person_tracker import TrackedPerson

from .multi_person_state import (
    GroupSecurityEvidence,
    GroupSecurityLevel,
    GroupSecurityState,
    MultiPersonAssessment,
)


class AUREXMultiPersonSecurity:

    def __init__(
        self,
        proximity_threshold: float = 0.30,
        high_density_threshold: int = 4,
        history_limit: int = 30,
        stability_frames: int = 3,
    ) -> None:

        self.proximity_threshold = proximity_threshold
        self.high_density_threshold = high_density_threshold
        self.history_limit = history_limit
        self.stability_frames = stability_frames

        self.history: List[MultiPersonAssessment] = []

    @staticmethod
    def _distance(
        first: TrackedPerson,
        second: TrackedPerson,
    ) -> float:

        x1, y1 = first.current_center
        x2, y2 = second.current_center

        dx = x2 - x1
        dy = y2 - y1

        return (dx * dx + dy * dy) ** 0.5

    def _analyze_pair(
        self,
        first: TrackedPerson,
        second: TrackedPerson,
    ) -> Dict[str, Any]:

        distance = self._distance(first, second)

        first_direction = str(
            first.movement_direction or ""
        ).lower()

        second_direction = str(
            second.movement_direction or ""
        ).lower()

        approaching = (
            "approach" in first_direction
            or "approach" in second_direction
        )

        separating = (
            "away" in first_direction
            or "away" in second_direction
            or "separat" in first_direction
            or "separat" in second_direction
        )

        same_zone = (
            first.zone is not None
            and second.zone is not None
            and first.zone == second.zone
        )

        nearby = distance <= self.proximity_threshold

        return {
            "source_id": str(first.person_id),
            "target_id": str(second.person_id),
            "distance": distance,
            "nearby": nearby,
            "approaching": approaching,
            "separating": separating,
            "same_zone": same_zone,
            "source_direction": first.movement_direction,
            "target_direction": second.movement_direction,
        }

    def analyze(
        self,
        tracked_people: Optional[
            Iterable[TrackedPerson]
        ] = None,
    ) -> MultiPersonAssessment:

        people = list(tracked_people or [])

        person_ids = [
            str(person.person_id)
            for person in people
        ]

        assessment = MultiPersonAssessment(
            state=GroupSecurityState.NO_GROUP,
            level=GroupSecurityLevel.NORMAL,
            confidence=0.0,
            person_ids=person_ids,
        )

        count = len(people)

        if count == 0:

            assessment.state = GroupSecurityState.NO_GROUP
            assessment.level = GroupSecurityLevel.NORMAL

            assessment.reasons.append(
                "No tracked people are currently present."
            )

            self._record(assessment)

            return assessment

        if count == 1:

            assessment.state = GroupSecurityState.SINGLE_PERSON
            assessment.level = GroupSecurityLevel.NORMAL

            assessment.add_evidence(
                GroupSecurityEvidence(
                    source="person_count",
                    description="One tracked person is present.",
                    confidence=1.0,
                    weight=1.0,
                )
            )

            assessment.reasons.append(
                "Single-person scene."
            )

            assessment.calculate_confidence()

            self._record(assessment)

            return assessment

        assessment.add_evidence(
            GroupSecurityEvidence(
                source="person_count",
                description=f"{count} tracked people are present.",
                confidence=min(
                    1.0,
                    0.70 + count * 0.05,
                ),
                weight=0.50,
                metadata={
                    "count": count
                },
            )
        )

        if count >= self.high_density_threshold:

            assessment.state = GroupSecurityState.HIGH_DENSITY
            assessment.level = GroupSecurityLevel.WARNING

            assessment.add_evidence(
                GroupSecurityEvidence(
                    source="density",
                    description=(
                        "High number of tracked people "
                        "in the scene."
                    ),
                    confidence=min(
                        0.95,
                        0.55 + (count - 3) * 0.10,
                    ),
                    weight=1.0,
                    metadata={
                        "count": count
                    },
                )
            )

            assessment.reasons.append(
                "Multiple people create a high-density scene."
            )

        else:

            assessment.state = GroupSecurityState.MULTI_PERSON
            assessment.level = GroupSecurityLevel.NORMAL

            assessment.reasons.append(
                "Multiple people are present."
            )

        for index, first in enumerate(people):

            for second in people[index + 1:]:

                pair = self._analyze_pair(
                    first,
                    second,
                )

                if pair["nearby"]:
                    assessment.nearby_pairs.append(pair)

                if pair["approaching"]:
                    assessment.approaching_pairs.append(pair)

                if pair["separating"]:
                    assessment.separating_pairs.append(pair)

                if pair["same_zone"]:
                    assessment.same_zone_pairs.append(pair)

        if assessment.nearby_pairs:

            assessment.state = GroupSecurityState.PROXIMITY

            if assessment.level == GroupSecurityLevel.NORMAL:
                assessment.level = GroupSecurityLevel.LOW

            assessment.add_evidence(
                GroupSecurityEvidence(
                    source="person_proximity",
                    description=(
                        f"{len(assessment.nearby_pairs)} "
                        "person pair(s) are spatially close."
                    ),
                    confidence=min(
                        0.95,
                        0.65
                        + len(
                            assessment.nearby_pairs
                        ) * 0.08,
                    ),
                    weight=1.0,
                    metadata={
                        "pair_count": len(
                            assessment.nearby_pairs
                        )
                    },
                )
            )

            assessment.reasons.append(
                "Person-to-person proximity detected."
            )

        if assessment.approaching_pairs:

            assessment.state = (
                GroupSecurityState.APPROACH_PATTERN
            )

            if assessment.level in (
                GroupSecurityLevel.NORMAL,
                GroupSecurityLevel.LOW,
            ):
                assessment.level = (
                    GroupSecurityLevel.WARNING
                )

            assessment.add_evidence(
                GroupSecurityEvidence(
                    source="approach_pattern",
                    description=(
                        f"{len(assessment.approaching_pairs)} "
                        "pair(s) show an observable "
                        "approach pattern."
                    ),
                    confidence=min(
                        0.92,
                        0.65
                        + len(
                            assessment.approaching_pairs
                        ) * 0.08,
                    ),
                    weight=1.20,
                    metadata={
                        "pair_count": len(
                            assessment.approaching_pairs
                        )
                    },
                )
            )

            assessment.reasons.append(
                "An observable approach pattern was detected."
            )

        if assessment.separating_pairs:

            if not assessment.approaching_pairs:

                assessment.state = (
                    GroupSecurityState.SEPARATION_PATTERN
                )

            assessment.add_evidence(
                GroupSecurityEvidence(
                    source="separation_pattern",
                    description=(
                        f"{len(assessment.separating_pairs)} "
                        "pair(s) show an observable "
                        "separation pattern."
                    ),
                    confidence=min(
                        0.90,
                        0.60
                        + len(
                            assessment.separating_pairs
                        ) * 0.08,
                    ),
                    weight=0.80,
                    metadata={
                        "pair_count": len(
                            assessment.separating_pairs
                        )
                    },
                )
            )

            assessment.reasons.append(
                "An observable separation pattern was detected."
            )

        if assessment.same_zone_pairs:

            assessment.add_evidence(
                GroupSecurityEvidence(
                    source="same_zone",
                    description=(
                        f"{len(assessment.same_zone_pairs)} "
                        "pair(s) occupy the same tracked zone."
                    ),
                    confidence=min(
                        0.90,
                        0.60
                        + len(
                            assessment.same_zone_pairs
                        ) * 0.06,
                    ),
                    weight=0.70,
                    metadata={
                        "pair_count": len(
                            assessment.same_zone_pairs
                        )
                    },
                )
            )

            assessment.reasons.append(
                "People share one or more spatial zones."
            )

        assessment.calculate_confidence()

        if (
            assessment.approaching_pairs
            and assessment.nearby_pairs
            and assessment.confidence >= 0.70
        ):

            assessment.level = GroupSecurityLevel.HIGH

            assessment.state = (
                GroupSecurityState.APPROACH_PATTERN
            )

            assessment.reasons.append(
                "Approach and proximity signals "
                "are simultaneously present."
            )

        elif (
            assessment.nearby_pairs
            and assessment.confidence >= 0.60
        ):

            if assessment.level == GroupSecurityLevel.NORMAL:
                assessment.level = GroupSecurityLevel.LOW

        assessment.metadata = {
            "people_count": count,
            "nearby_pair_count": len(
                assessment.nearby_pairs
            ),
            "approaching_pair_count": len(
                assessment.approaching_pairs
            ),
            "separating_pair_count": len(
                assessment.separating_pairs
            ),
            "same_zone_pair_count": len(
                assessment.same_zone_pairs
            ),
        }

        self._record(assessment)

        return assessment

    def stable_state(
        self,
        state: GroupSecurityState,
    ) -> bool:

        if len(self.history) < self.stability_frames:
            return False

        recent = self.history[
            -self.stability_frames:
        ]

        return all(
            item.state == state
            for item in recent
        )

    def highest_recent_level(
        self,
    ) -> GroupSecurityLevel:

        if not self.history:
            return GroupSecurityLevel.NORMAL

        priority = {
            GroupSecurityLevel.NORMAL: 0,
            GroupSecurityLevel.LOW: 1,
            GroupSecurityLevel.WARNING: 2,
            GroupSecurityLevel.HIGH: 3,
        }

        return max(
            self.history,
            key=lambda item: priority[item.level],
        ).level

    def _record(
        self,
        assessment: MultiPersonAssessment,
    ) -> None:

        self.history.append(assessment)

        if len(self.history) > self.history_limit:
            self.history = self.history[
                -self.history_limit:
            ]

    def reset(self) -> None:
        self.history.clear()

    def status(self) -> Dict[str, Any]:

        latest = (
            self.history[-1].to_dict()
            if self.history
            else None
        )

        return {
            "history_size": len(self.history),
            "proximity_threshold": (
                self.proximity_threshold
            ),
            "high_density_threshold": (
                self.high_density_threshold
            ),
            "stability_frames": (
                self.stability_frames
            ),
            "latest": latest,
        }