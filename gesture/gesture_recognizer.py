"""
AUREX Spatial Intelligence
Air Gesture Recognition Layer
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import atan2, degrees, hypot


class GestureType(str, Enum):
    UNKNOWN = "UNKNOWN"
    POINT = "POINT"
    TAP = "TAP"
    SWIPE_LEFT = "SWIPE_LEFT"
    SWIPE_RIGHT = "SWIPE_RIGHT"
    SWIPE_UP = "SWIPE_UP"
    SWIPE_DOWN = "SWIPE_DOWN"
    CIRCLE = "CIRCLE"
    ZIGZAG = "ZIGZAG"
    CLEAR = "CLEAR"


@dataclass
class GestureResult:
    gesture: GestureType
    confidence: float
    point_count: int
    distance: float
    direction: str


class AUREXGestureRecognizer:
    """
    Geometry-based gesture recognizer.

    This layer interprets completed air strokes.
    """

    def __init__(
        self,
        minimum_points: int = 5,
    ) -> None:

        self.minimum_points = minimum_points

    @staticmethod
    def _distance(
        a: tuple[int, int],
        b: tuple[int, int],
    ) -> float:

        return hypot(
            b[0] - a[0],
            b[1] - a[1],
        )

    @staticmethod
    def _direction(
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> str:

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        if abs(dx) >= abs(dy):
            return (
                "RIGHT"
                if dx >= 0
                else "LEFT"
            )

        return (
            "DOWN"
            if dy >= 0
            else "UP"
        )

    def recognize(
        self,
        points: list[tuple[int, int]],
    ) -> GestureResult:

        count = len(points)

        if count < self.minimum_points:

            return GestureResult(
                gesture=GestureType.UNKNOWN,
                confidence=0.0,
                point_count=count,
                distance=0.0,
                direction="NONE",
            )

        start = points[0]
        end = points[-1]

        total_distance = sum(
            self._distance(
                points[index - 1],
                points[index],
            )
            for index in range(1, count)
        )

        direct_distance = self._distance(
            start,
            end,
        )

        direction = self._direction(
            start,
            end,
        )

        if direct_distance < 20:

            if self._is_circle(
                points
            ):

                return GestureResult(
                    gesture=GestureType.CIRCLE,
                    confidence=0.82,
                    point_count=count,
                    distance=total_distance,
                    direction=direction,
                )

            return GestureResult(
                gesture=GestureType.TAP,
                confidence=0.72,
                point_count=count,
                distance=total_distance,
                direction=direction,
            )

        straightness = (
            direct_distance
            / max(total_distance, 1.0)
        )

        if (
            direct_distance > 100
            and straightness > 0.72
        ):

            gesture_map = {
                "LEFT": GestureType.SWIPE_LEFT,
                "RIGHT": GestureType.SWIPE_RIGHT,
                "UP": GestureType.SWIPE_UP,
                "DOWN": GestureType.SWIPE_DOWN,
            }

            return GestureResult(
                gesture=gesture_map[direction],
                confidence=min(
                    0.95,
                    0.55 + straightness * 0.4,
                ),
                point_count=count,
                distance=total_distance,
                direction=direction,
            )

        if self._is_zigzag(points):

            return GestureResult(
                gesture=GestureType.ZIGZAG,
                confidence=0.78,
                point_count=count,
                distance=total_distance,
                direction=direction,
            )

        return GestureResult(
            gesture=GestureType.UNKNOWN,
            confidence=0.30,
            point_count=count,
            distance=total_distance,
            direction=direction,
        )

    def _is_circle(
        self,
        points: list[tuple[int, int]],
    ) -> bool:

        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        width = max(xs) - min(xs)
        height = max(ys) - min(ys)

        if width < 30 or height < 30:
            return False

        aspect = width / max(height, 1)

        if not 0.55 <= aspect <= 1.8:
            return False

        center_x = sum(xs) / len(xs)
        center_y = sum(ys) / len(ys)

        radii = [
            hypot(
                point[0] - center_x,
                point[1] - center_y,
            )
            for point in points
        ]

        average_radius = (
            sum(radii) / len(radii)
        )

        if average_radius < 10:
            return False

        variation = sum(
            abs(
                radius
                - average_radius
            )
            for radius in radii
        ) / len(radii)

        return (
            variation
            / average_radius
            < 0.45
        )

    def _is_zigzag(
        self,
        points: list[tuple[int, int]],
    ) -> bool:

        directions = []

        for index in range(
            2,
            len(points),
        ):

            previous = points[index - 2]
            current = points[index - 1]
            current_next = points[index]

            dx1 = (
                current[0]
                - previous[0]
            )

            dx2 = (
                current_next[0]
                - current[0]
            )

            if (
                abs(dx1) > 8
                and abs(dx2) > 8
                and dx1 * dx2 < 0
            ):
                directions.append(
                    True
                )

        return len(directions) >= 2