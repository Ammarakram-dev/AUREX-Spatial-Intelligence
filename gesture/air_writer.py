"""
AUREX Spatial Intelligence
Air Writing Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot


@dataclass
class AirStroke:
    points: list[tuple[int, int]]

    def add(
        self,
        point: tuple[int, int],
    ) -> None:

        self.points.append(point)


class AUREXAirWriter:
    """
    Converts fingertip movement into stable
    air-writing strokes.
    """

    def __init__(
        self,
        smoothing: float = 0.35,
        minimum_distance: float = 5.0,
    ) -> None:

        self.smoothing = smoothing
        self.minimum_distance = (
            minimum_distance
        )

        self.current_stroke: AirStroke | None = None

        self.strokes: list[AirStroke] = []

        self.last_point: (
            tuple[int, int] | None
        ) = None

    def update(
        self,
        point: tuple[int, int] | None,
        writing: bool,
    ) -> None:

        if not writing or point is None:

            self.finish_stroke()

            return

        point = self._smooth(point)

        if self.last_point is not None:

            distance = hypot(
                point[0]
                - self.last_point[0],
                point[1]
                - self.last_point[1],
            )

            if (
                distance
                < self.minimum_distance
            ):
                return

        if self.current_stroke is None:

            self.current_stroke = (
                AirStroke(points=[])
            )

            self.strokes.append(
                self.current_stroke
            )

        self.current_stroke.add(point)

        self.last_point = point

    def finish_stroke(self) -> None:

        self.current_stroke = None
        self.last_point = None

    def clear(self) -> None:

        self.strokes.clear()

        self.current_stroke = None
        self.last_point = None

    def _smooth(
        self,
        point: tuple[int, int],
    ) -> tuple[int, int]:

        if self.last_point is None:
            return point

        x = (
            self.last_point[0]
            * (1 - self.smoothing)
            +
            point[0]
            * self.smoothing
        )

        y = (
            self.last_point[1]
            * (1 - self.smoothing)
            +
            point[1]
            * self.smoothing
        )

        return (
            int(x),
            int(y),
        )

    def draw(
        self,
        frame,
    ):

        output = frame.copy()

        for stroke in self.strokes:

            points = stroke.points

            for index in range(
                1,
                len(points),
            ):

                start = points[index - 1]
                end = points[index]

                import cv2

                cv2.line(
                    output,
                    start,
                    end,
                    (0, 255, 255),
                    4,
                    cv2.LINE_AA,
                )

        return output

    @property
    def stroke_count(self) -> int:

        return len(self.strokes)

    @property
    def point_count(self) -> int:

        return sum(
            len(stroke.points)
            for stroke in self.strokes
        )