from __future__ import annotations

import math
from typing import Any, Dict, Iterable, Optional, Sequence, Tuple


Point = Tuple[float, float]


class AUREXEmotionFeatures:
    """
    Extracts geometric facial-expression signals from normalized
    face landmarks.

    These are visible facial-expression features, not direct measurements
    of a person's internal emotional state.
    """

    def __init__(self) -> None:
        self.previous: Optional[Dict[str, float]] = None

    @staticmethod
    def _point(landmarks: Sequence[Any], index: int) -> Optional[Point]:
        if index < 0 or index >= len(landmarks):
            return None

        point = landmarks[index]

        try:
            return float(point[0]), float(point[1])
        except (TypeError, ValueError, IndexError):
            pass

        try:
            return float(point.x), float(point.y)
        except (AttributeError, TypeError, ValueError):
            return None

    @staticmethod
    def _distance(a: Optional[Point], b: Optional[Point]) -> float:
        if a is None or b is None:
            return 0.0

        return math.sqrt(
            (a[0] - b[0]) ** 2 +
            (a[1] - b[1]) ** 2
        )

    @staticmethod
    def _ratio(
        numerator_a: Optional[Point],
        numerator_b: Optional[Point],
        denominator_a: Optional[Point],
        denominator_b: Optional[Point],
    ) -> float:
        denominator = AUREXEmotionFeatures._distance(
            denominator_a,
            denominator_b,
        )

        if denominator <= 1e-8:
            return 0.0

        return (
            AUREXEmotionFeatures._distance(
                numerator_a,
                numerator_b,
            ) / denominator
        )

    def extract(self, landmarks: Optional[Iterable[Any]]) -> Dict[str, float]:
        if landmarks is None:
            return {}

        landmarks = list(landmarks)

        if len(landmarks) < 468:
            return {}

        # MediaPipe Face Mesh landmark indices.
        left_eye_top = self._point(landmarks, 159)
        left_eye_bottom = self._point(landmarks, 145)
        right_eye_top = self._point(landmarks, 386)
        right_eye_bottom = self._point(landmarks, 374)

        left_eye_left = self._point(landmarks, 33)
        left_eye_right = self._point(landmarks, 133)
        right_eye_left = self._point(landmarks, 362)
        right_eye_right = self._point(landmarks, 263)

        mouth_left = self._point(landmarks, 61)
        mouth_right = self._point(landmarks, 291)
        mouth_top = self._point(landmarks, 13)
        mouth_bottom = self._point(landmarks, 14)

        upper_lip = self._point(landmarks, 0)
        lower_lip = self._point(landmarks, 17)

        brow_left = self._point(landmarks, 105)
        brow_right = self._point(landmarks, 334)

        nose_tip = self._point(landmarks, 1)
        nose_bridge = self._point(landmarks, 168)

        chin = self._point(landmarks, 152)
        forehead = self._point(landmarks, 10)

        face_width = self._distance(
            self._point(landmarks, 234),
            self._point(landmarks, 454),
        )

        face_height = self._distance(
            forehead,
            chin,
        )

        if face_width <= 1e-8:
            face_width = 1.0

        if face_height <= 1e-8:
            face_height = 1.0

        left_eye = self._ratio(
            left_eye_top,
            left_eye_bottom,
            left_eye_left,
            left_eye_right,
        )

        right_eye = self._ratio(
            right_eye_top,
            right_eye_bottom,
            right_eye_left,
            right_eye_right,
        )

        eye_opening = (left_eye + right_eye) / 2.0

        mouth_width = self._distance(mouth_left, mouth_right) / face_width
        mouth_opening = self._distance(mouth_top, mouth_bottom) / face_height

        brow_height_left = 0.0
        brow_height_right = 0.0

        if brow_left and left_eye_top:
            brow_height_left = abs(brow_left[1] - left_eye_top[1]) / face_height

        if brow_right and right_eye_top:
            brow_height_right = abs(brow_right[1] - right_eye_top[1]) / face_height

        brow_height = (brow_height_left + brow_height_right) / 2.0

        nose_mouth_distance = self._distance(
            nose_tip,
            mouth_top,
        ) / face_height

        mouth_center_y = 0.0
        if mouth_left and mouth_right:
            mouth_center_y = (mouth_left[1] + mouth_right[1]) / 2.0

        mouth_curve = 0.0

        if mouth_left and mouth_right and mouth_top and mouth_bottom:
            mouth_mid_x = (mouth_left[0] + mouth_right[0]) / 2.0
            mouth_mid_y = (mouth_top[1] + mouth_bottom[1]) / 2.0

            corner_y = (mouth_left[1] + mouth_right[1]) / 2.0

            mouth_curve = (
                (corner_y - mouth_mid_y) / face_height
            )

        features = {
            "eye_opening": eye_opening,
            "left_eye_opening": left_eye,
            "right_eye_opening": right_eye,
            "mouth_width": mouth_width,
            "mouth_opening": mouth_opening,
            "brow_height": brow_height,
            "nose_mouth_distance": nose_mouth_distance,
            "mouth_curve": mouth_curve,
            "face_width": face_width,
            "face_height": face_height,
        }

        self.previous = dict(features)

        return features

    def reset(self) -> None:
        self.previous = None