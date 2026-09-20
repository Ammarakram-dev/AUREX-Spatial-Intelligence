from __future__ import annotations

from collections import Counter, deque
from typing import Any, Dict, List, Optional

from .behavior_state import (
    AnomalySeverity,
    BehaviorAnalysis,
    BehaviorAnomaly,
    BehaviorObservation,
    BehaviorPattern,
    BehaviorProfile,
)


class AUREXBehaviorEngine:
    """
    Short-term behavioral pattern and anomaly engine.

    The engine analyzes observable temporal movement signals.
    It does not infer psychological states, motives, or identity.
    """

    def __init__(
        self,
        history_limit: int = 60,
        movement_threshold: float = 0.05,
        rapid_movement_threshold: float = 0.35,
        prolonged_stationary_frames: int = 45,
    ) -> None:
        self.history_limit = int(history_limit)
        self.movement_threshold = float(
            movement_threshold
        )
        self.rapid_movement_threshold = float(
            rapid_movement_threshold
        )
        self.prolonged_stationary_frames = int(
            prolonged_stationary_frames
        )

        self.history: Dict[
            str,
            deque[BehaviorObservation]
        ] = {}

    def _get_history(
        self,
        person_id: str,
    ) -> deque[BehaviorObservation]:
        if person_id not in self.history:
            self.history[person_id] = deque(
                maxlen=self.history_limit
            )

        return self.history[person_id]

    @staticmethod
    def _safe_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _direction(value: Any) -> str:
        if value is None:
            return ""

        return str(value).strip().lower()

    @staticmethod
    def _posture(value: Any) -> str:
        if value is None:
            return ""

        return str(value).strip().lower()

    def observe(
        self,
        person_id: str,
        movement_distance: float,
        movement_direction: str = "",
        zone: str = "",
        posture: str = "",
        timestamp: float = 0.0,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> BehaviorObservation:
        observation = BehaviorObservation(
            person_id=str(person_id),
            movement_distance=self._safe_float(
                movement_distance
            ),
            movement_direction=self._direction(
                movement_direction
            ),
            zone=str(zone or ""),
            posture=self._posture(posture),
            timestamp=float(timestamp),
            metadata=dict(metadata or {}),
        )

        self._get_history(
            observation.person_id
        ).append(observation)

        return observation

    def observe_state(
        self,
        human_state: Any,
        timestamp: Optional[float] = None,
    ) -> BehaviorObservation:
        """
        Accepts the existing HumanSpatialState object
        without tightly coupling this engine to its module.
        """

        if timestamp is None:
            timestamp = self._safe_float(
                getattr(
                    human_state,
                    "timestamp",
                    0.0,
                )
            )

        posture = getattr(
            human_state,
            "posture",
            "",
        )

        posture_value = getattr(
            posture,
            "value",
            posture,
        )

        return self.observe(
            person_id=getattr(
                human_state,
                "person_id",
                "unknown",
            ),
            movement_distance=getattr(
                human_state,
                "movement_distance",
                0.0,
            ),
            movement_direction=getattr(
                human_state,
                "movement_direction",
                "",
            ),
            zone=getattr(
                human_state,
                "zone",
                "",
            ),
            posture=posture_value,
            timestamp=timestamp,
        )

    def _direction_changes(
        self,
        observations: List[BehaviorObservation],
    ) -> int:
        previous = None
        changes = 0

        meaningful = {
            "left",
            "right",
            "up",
            "down",
            "approaching",
            "moving_away",
            "away",
        }

        for observation in observations:
            direction = observation.movement_direction

            if direction not in meaningful:
                continue

            if previous is not None and direction != previous:
                changes += 1

            previous = direction

        return changes

    def _counts(
        self,
        observations: List[BehaviorObservation],
    ):
        stationary = sum(
            1
            for item in observations
            if item.movement_distance
            < self.movement_threshold
        )

        moving = len(observations) - stationary

        approaching = sum(
            1
            for item in observations
            if (
                "approach"
                in item.movement_direction
            )
        )

        departure = sum(
            1
            for item in observations
            if (
                "away"
                in item.movement_direction
                or "depart"
                in item.movement_direction
            )
        )

        return (
            stationary,
            moving,
            approaching,
            departure,
        )

    def _dominant(
        self,
        values: List[str],
    ) -> str:
        clean = [
            value
            for value in values
            if value
        ]

        if not clean:
            return ""

        return Counter(clean).most_common(1)[0][0]

    def _recent_pattern(
        self,
        observations: List[BehaviorObservation],
        direction_changes: int,
    ) -> BehaviorPattern:
        if not observations:
            return BehaviorPattern.UNKNOWN

        recent = observations[-10:]

        if direction_changes >= 3:
            return BehaviorPattern.DIRECTION_CHANGE

        if any(
            "approach"
            in item.movement_direction
            for item in recent
        ):
            return BehaviorPattern.APPROACHING

        if any(
            "away"
            in item.movement_direction
            or "depart"
            in item.movement_direction
            for item in recent
        ):
            return BehaviorPattern.MOVING_AWAY

        if all(
            item.movement_distance
            < self.movement_threshold
            for item in recent
        ):
            return BehaviorPattern.PROLONGED_INACTIVITY

        if any(
            item.movement_distance
            >= self.rapid_movement_threshold
            for item in recent
        ):
            return BehaviorPattern.RAPID_MOVEMENT

        if len(recent) >= 6:
            distances = [
                item.movement_distance
                for item in recent
            ]

            moving_count = sum(
                value >= self.movement_threshold
                for value in distances
            )

            if moving_count >= 4:
                return BehaviorPattern.REPEATED_MOVEMENT

        if any(
            item.movement_distance
            >= self.movement_threshold
            for item in recent
        ):
            return BehaviorPattern.NORMAL_MOVEMENT

        return BehaviorPattern.STATIONARY

    def _anomaly_for_profile(
        self,
        profile: BehaviorProfile,
        observations: List[BehaviorObservation],
    ) -> Optional[BehaviorAnomaly]:
        evidence: List[str] = []
        score = 0.0
        pattern = profile.recent_pattern

        if pattern == BehaviorPattern.RAPID_MOVEMENT:
            score += 0.55
            evidence.append(
                "rapid movement detected"
            )

        if pattern == BehaviorPattern.DIRECTION_CHANGE:
            score += 0.45
            evidence.append(
                "multiple recent direction changes"
            )

        if pattern == BehaviorPattern.PROLONGED_INACTIVITY:
            score += 0.35
            evidence.append(
                "prolonged stationary period"
            )

        if profile.direction_changes >= 5:
            score += 0.20
            evidence.append(
                "frequent directional variation"
            )

        if profile.approach_count >= 4:
            score += 0.15
            evidence.append(
                "repeated approaching pattern"
            )

        if profile.departure_count >= 4:
            score += 0.15
            evidence.append(
                "repeated departure pattern"
            )

        recent = observations[-10:]

        if len(recent) >= 6:
            older = observations[:-6]

            if older:
                old_average = sum(
                    item.movement_distance
                    for item in older
                ) / len(older)

                recent_average = sum(
                    item.movement_distance
                    for item in recent
                ) / len(recent)

                if (
                    old_average < self.movement_threshold
                    and recent_average
                    >= self.movement_threshold * 2
                ):
                    score += 0.30
                    evidence.append(
                        "movement changed significantly "
                        "from earlier observations"
                    )

        score = min(
            1.0,
            score,
        )

        profile.anomaly_score = score

        if score < 0.35:
            return None

        if score >= 0.85:
            severity = AnomalySeverity.CRITICAL
        elif score >= 0.70:
            severity = AnomalySeverity.HIGH
        elif score >= 0.50:
            severity = AnomalySeverity.WARNING
        else:
            severity = AnomalySeverity.LOW

        return BehaviorAnomaly(
            person_id=profile.person_id,
            pattern=pattern,
            severity=severity,
            confidence=score,
            evidence=evidence,
            metadata={
                "observation_count": len(
                    observations
                ),
            },
        )

    def analyze_person(
        self,
        person_id: str,
    ) -> Optional[
        tuple[
            BehaviorProfile,
            Optional[BehaviorAnomaly],
        ]
    ]:
        if person_id not in self.history:
            return None

        observations = list(
            self.history[person_id]
        )

        if not observations:
            return None

        distances = [
            item.movement_distance
            for item in observations
        ]

        stationary, moving, approaching, departure = (
            self._counts(observations)
        )

        direction_changes = (
            self._direction_changes(
                observations
            )
        )

        dominant_zone = self._dominant(
            [
                item.zone
                for item in observations
            ]
        )

        dominant_posture = self._dominant(
            [
                item.posture
                for item in observations
            ]
        )

        pattern = self._recent_pattern(
            observations,
            direction_changes,
        )

        profile = BehaviorProfile(
            person_id=person_id,
            observation_count=len(observations),
            average_movement=sum(
                distances
            ) / len(distances),
            maximum_movement=max(
                distances
            ),
            stationary_frames=stationary,
            movement_frames=moving,
            direction_changes=direction_changes,
            approach_count=approaching,
            departure_count=departure,
            dominant_zone=dominant_zone,
            dominant_posture=dominant_posture,
            recent_pattern=pattern,
            anomaly_score=0.0,
        )

        anomaly = self._anomaly_for_profile(
            profile,
            observations,
        )

        return profile, anomaly

    def analyze(
        self,
        human_states: Optional[
            List[Any]
        ] = None,
    ) -> BehaviorAnalysis:
        if human_states:
            for state in human_states:
                self.observe_state(state)

        profiles: List[BehaviorProfile] = []
        anomalies: List[BehaviorAnomaly] = []

        for person_id in list(
            self.history.keys()
        ):
            result = self.analyze_person(
                person_id
            )

            if result is None:
                continue

            profile, anomaly = result

            profiles.append(profile)

            if anomaly is not None:
                anomalies.append(anomaly)

        if anomalies:
            global_score = max(
                item.confidence
                for item in anomalies
            )
        else:
            global_score = 0.0

        return BehaviorAnalysis(
            profiles=profiles,
            anomalies=anomalies,
            global_anomaly_score=global_score,
            metadata={
                "tracked_people": len(
                    profiles
                ),
                "history_limit": self.history_limit,
            },
        )

    def clear_person(
        self,
        person_id: str,
    ) -> None:
        self.history.pop(
            str(person_id),
            None,
        )

    def reset(self) -> None:
        self.history.clear()

    def status(self) -> Dict[str, Any]:
        return {
            "tracked_people": len(
                self.history
            ),
            "history_limit": self.history_limit,
            "people": {
                person_id: len(history)
                for person_id, history
                in self.history.items()
            },
        }