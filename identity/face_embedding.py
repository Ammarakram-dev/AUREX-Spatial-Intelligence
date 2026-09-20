"""
AUREX Spatial Intelligence
Face Representation Engine
Phase 23
"""

from typing import List

import math


class AUREXFaceEmbedding:

    """
    Converts normalized facial landmark coordinates into
    a deterministic normalized face representation.

    This is a lightweight local representation designed
    for the AUREX prototype pipeline.
    """

    def __init__(
        self,
        dimensions: int = 32,
    ) -> None:

        self.dimensions = dimensions

    @staticmethod
    def _distance(
        point_a,
        point_b,
    ) -> float:

        dx = point_a[0] - point_b[0]
        dy = point_a[1] - point_b[1]

        return math.sqrt(
            dx * dx + dy * dy
        )

    def create(
        self,
        landmarks: List[tuple],
    ) -> List[float]:

        if not landmarks:
            return []

        features = []

        anchor = landmarks[0]

        for point in landmarks:

            features.append(
                self._distance(
                    anchor,
                    point,
                )
            )

        while len(features) < self.dimensions:
            features.append(0.0)

        features = features[: self.dimensions]

        magnitude = math.sqrt(
            sum(
                value * value
                for value in features
            )
        )

        if magnitude == 0.0:
            return [
                0.0
                for _ in features
            ]

        return [
            value / magnitude
            for value in features
        ]

    @staticmethod
    def similarity(
        first: List[float],
        second: List[float],
    ) -> float:

        if not first or not second:
            return 0.0

        size = min(
            len(first),
            len(second),
        )

        dot = sum(
            first[index]
            * second[index]
            for index in range(size)
        )

        first_norm = math.sqrt(
            sum(
                value * value
                for value in first[:size]
            )
        )

        second_norm = math.sqrt(
            sum(
                value * value
                for value in second[:size]
            )
        )

        if (
            first_norm == 0.0
            or second_norm == 0.0
        ):
            return 0.0

        cosine = (
            dot
            / (
                first_norm
                * second_norm
            )
        )

        return max(
            0.0,
            min(
                1.0,
                (cosine + 1.0) / 2.0,
            ),
        )