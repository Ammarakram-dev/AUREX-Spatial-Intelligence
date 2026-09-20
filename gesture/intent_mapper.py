"""
AUREX Spatial Intelligence
Gesture-to-Intent Mapping
"""

from __future__ import annotations

from dataclasses import dataclass

from gesture.gesture_recognizer import (
    GestureResult,
    GestureType,
)


@dataclass
class SpatialIntent:
    name: str
    action: str
    confidence: float


class AUREXIntentMapper:
    """
    Converts recognized gestures into
    high-level spatial intentions.
    """

    def map(
        self,
        result: GestureResult,
    ) -> SpatialIntent:

        mapping = {
            GestureType.POINT: (
                "POINT",
                "SELECT_TARGET",
            ),
            GestureType.TAP: (
                "TAP",
                "SELECT_TARGET",
            ),
            GestureType.SWIPE_LEFT: (
                "SWIPE_LEFT",
                "MOVE_LEFT",
            ),
            GestureType.SWIPE_RIGHT: (
                "SWIPE_RIGHT",
                "MOVE_RIGHT",
            ),
            GestureType.SWIPE_UP: (
                "SWIPE_UP",
                "MOVE_UP",
            ),
            GestureType.SWIPE_DOWN: (
                "SWIPE_DOWN",
                "MOVE_DOWN",
            ),
            GestureType.CIRCLE: (
                "CIRCLE",
                "CREATE_ORBIT",
            ),
            GestureType.ZIGZAG: (
                "ZIGZAG",
                "ERASE_STROKE",
            ),
            GestureType.CLEAR: (
                "CLEAR",
                "CLEAR_CANVAS",
            ),
        }

        name, action = mapping.get(
            result.gesture,
            ("UNKNOWN", "NO_ACTION"),
        )

        return SpatialIntent(
            name=name,
            action=action,
            confidence=result.confidence,
        )