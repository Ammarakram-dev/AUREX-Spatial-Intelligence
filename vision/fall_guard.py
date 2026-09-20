"""
AUREX Spatial Intelligence
FallGuard Temporal Safety Engine
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque

from vision.posture_analyzer import (
    AUREXPostureAnalyzer,
    PostureResult,
    PostureState,
)


@dataclass
class FallGuardEvent:
    possible_fall: bool
    confidence: float
    reason: str
    person_id: int | None
    posture: PostureState


@dataclass
class _PersonHistory:
    postures: Deque[PostureState]
    vertical_ratios: Deque[float]
    torso_angles: Deque[float]
    movement_distances: Deque[float]


class AUREXFallGuard:
    """
    Temporal fall-detection prototype.

    A fall is considered only when multiple signals occur
    across consecutive observations.

    This is an assistive safety detector, not a medical
    diagnostic system.
    """

    def __init__(
        self,
        history_size: int = 12,
        confirmation_frames: int = 3,
    ) -> None:

        self.history_size = history_size
        self.confirmation_frames = confirmation_frames

        self.histories: dict[int, _PersonHistory] = {}

    def _get_history(
        self,
        person_id: int,
    ) -> _PersonHistory:

        if person_id not in self.histories:
            self.histories[person_id] = _PersonHistory(
                postures=deque(
                    maxlen=self.history_size
                ),
                vertical_ratios=deque(
                    maxlen=self.history_size
                ),
                torso_angles=deque(
                    maxlen=self.history_size
                ),
                movement_distances=deque(
                    maxlen=self.history_size
                ),
            )

        return self.histories[person_id]

    def update(
        self,
        person_id: int,
        posture: PostureResult,
        movement_distance: float = 0.0,
    ) -> FallGuardEvent:

        history = self._get_history(person_id)

        history.postures.append(posture.state)
        history.vertical_ratios.append(
            posture.vertical_ratio
        )
        history.torso_angles.append(
            posture.torso_angle
        )
        history.movement_distances.append(
            movement_distance
        )

        if len(history.postures) < self.confirmation_frames:
            return FallGuardEvent(
                possible_fall=False,
                confidence=0.0,
                reason="INSUFFICIENT_HISTORY",
                person_id=person_id,
                posture=posture.state,
            )

        recent_postures = list(history.postures)[
            -self.confirmation_frames:
        ]

        recent_ratios = list(
            history.vertical_ratios
        )[-self.confirmation_frames:]

        recent_angles = list(
            history.torso_angles
        )[-self.confirmation_frames:]

        recent_movement = list(
            history.movement_distances
        )[-self.confirmation_frames:]

        low_posture = posture.state in {
            PostureState.LYING,
        }

        large_torso_angle = posture.torso_angle > 55

        low_vertical_ratio = (
            posture.vertical_ratio < 0.9
        )

        recent_motion = (
            max(recent_movement) >= 15
        )

        previous_upright = any(
            state in {
                PostureState.STANDING,
                PostureState.WALKING,
            }
            for state in recent_postures[
                :-1
            ]
        )

        posture_transition = (
            previous_upright
            and low_posture
        )

        geometry_signal = (
            large_torso_angle
            and low_vertical_ratio
        )

        sustained_low_posture = all(
            state == PostureState.LYING
            for state in recent_postures
        )

        signals = 0

        if posture_transition:
            signals += 1

        if geometry_signal:
            signals += 1

        if recent_motion:
            signals += 1

        if sustained_low_posture:
            signals += 1

        if signals >= 3:
            confidence = min(
                0.95,
                0.55 + signals * 0.10,
            )

            return FallGuardEvent(
                possible_fall=True,
                confidence=confidence,
                reason=(
                    "MULTI_SIGNAL_FALL_PATTERN"
                ),
                person_id=person_id,
                posture=posture.state,
            )

        return FallGuardEvent(
            possible_fall=False,
            confidence=min(
                0.49,
                signals * 0.12,
            ),
            reason="NO_CONFIRMED_FALL_PATTERN",
            person_id=person_id,
            posture=posture.state,
        )

    def remove_person(
        self,
        person_id: int,
    ) -> None:

        self.histories.pop(
            person_id,
            None,
        )

    def clear(self) -> None:
        self.histories.clear()