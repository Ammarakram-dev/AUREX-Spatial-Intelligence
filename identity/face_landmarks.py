"""
AUREX Spatial Intelligence
Real Face Landmark Analyzer

Phase 26
Provides:
- Eye openness measurement
- Blink detection support
- Head movement measurement
- Facial movement measurement
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


@dataclass
class FaceLandmarkResult:
    detected: bool
    confidence: float
    landmarks: List[Tuple[float, float]]
    left_eye_ratio: float
    right_eye_ratio: float
    eye_ratio: float
    eye_state: str
    head_movement: bool
    facial_motion: bool
    nose_position: Optional[Tuple[float, float]]

    def to_dict(self):
        return {
            "detected": self.detected,
            "confidence": self.confidence,
            "landmark_count": len(self.landmarks),
            "left_eye_ratio": self.left_eye_ratio,
            "right_eye_ratio": self.right_eye_ratio,
            "eye_ratio": self.eye_ratio,
            "eye_state": self.eye_state,
            "head_movement": self.head_movement,
            "facial_motion": self.facial_motion,
            "nose_position": self.nose_position,
        }


class AUREXFaceLandmarks:
    """
    Real-time MediaPipe Face Landmarker wrapper.

    Uses actual facial landmarks to estimate:
    - eye openness
    - eye state
    - head movement
    - facial movement
    """

    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    NOSE_INDEX = 1

    def __init__(
        self,
        model_path: str = "models/face_landmarker/face_landmarker.task",
        eye_closed_threshold: float = 0.21,
        eye_open_threshold: float = 0.25,
        movement_threshold: float = 0.018,
    ):
        self.model_path = model_path
        self.eye_closed_threshold = eye_closed_threshold
        self.eye_open_threshold = eye_open_threshold
        self.movement_threshold = movement_threshold

        self.previous_nose: Optional[Tuple[float, float]] = None
        self.previous_face_center: Optional[Tuple[float, float]] = None

        base_options = python.BaseOptions(
            model_asset_path=self.model_path
        )

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.landmarker = vision.FaceLandmarker.create_from_options(
            options
        )

    @staticmethod
    def _distance(
        a: Tuple[float, float],
        b: Tuple[float, float],
    ) -> float:
        return math.sqrt(
            (a[0] - b[0]) ** 2 +
            (a[1] - b[1]) ** 2
        )

    @classmethod
    def _eye_aspect_ratio(
        cls,
        points: List[Tuple[float, float]],
        indices: List[int],
    ) -> float:
        p1 = points[indices[0]]
        p2 = points[indices[1]]
        p3 = points[indices[2]]
        p4 = points[indices[3]]
        p5 = points[indices[4]]
        p6 = points[indices[5]]

        vertical_1 = cls._distance(p2, p6)
        vertical_2 = cls._distance(p3, p5)
        horizontal = cls._distance(p1, p4)

        if horizontal <= 1e-8:
            return 0.0

        return (vertical_1 + vertical_2) / (2.0 * horizontal)

    def process(self, frame) -> FaceLandmarkResult:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb,
        )

        result = self.landmarker.detect(mp_image)

        if not result.face_landmarks:
            self.previous_nose = None
            self.previous_face_center = None

            return FaceLandmarkResult(
                detected=False,
                confidence=0.0,
                landmarks=[],
                left_eye_ratio=0.0,
                right_eye_ratio=0.0,
                eye_ratio=0.0,
                eye_state="unknown",
                head_movement=False,
                facial_motion=False,
                nose_position=None,
            )

        face = result.face_landmarks[0]

        points = [
            (float(point.x), float(point.y))
            for point in face
        ]

        if len(points) < 400:
            return FaceLandmarkResult(
                detected=False,
                confidence=0.0,
                landmarks=points,
                left_eye_ratio=0.0,
                right_eye_ratio=0.0,
                eye_ratio=0.0,
                eye_state="unknown",
                head_movement=False,
                facial_motion=False,
                nose_position=None,
            )

        left_ratio = self._eye_aspect_ratio(
            points,
            self.LEFT_EYE,
        )

        right_ratio = self._eye_aspect_ratio(
            points,
            self.RIGHT_EYE,
        )

        eye_ratio = (left_ratio + right_ratio) / 2.0

        if eye_ratio <= self.eye_closed_threshold:
            eye_state = "closed"
        elif eye_ratio >= self.eye_open_threshold:
            eye_state = "open"
        else:
            eye_state = "unknown"

        nose = points[self.NOSE_INDEX]

        face_center_x = (
            points[10][0] +
            points[152][0]
        ) / 2.0

        face_center_y = (
            points[10][1] +
            points[152][1]
        ) / 2.0

        face_center = (
            face_center_x,
            face_center_y,
        )

        head_movement = False
        facial_motion = False

        if self.previous_nose is not None:
            nose_delta = self._distance(
                nose,
                self.previous_nose,
            )

            if nose_delta >= self.movement_threshold:
                head_movement = True
                facial_motion = True

        if self.previous_face_center is not None:
            center_delta = self._distance(
                face_center,
                self.previous_face_center,
            )

            if center_delta >= self.movement_threshold:
                head_movement = True

        self.previous_nose = nose
        self.previous_face_center = face_center

        confidence = 0.90

        return FaceLandmarkResult(
            detected=True,
            confidence=confidence,
            landmarks=points,
            left_eye_ratio=left_ratio,
            right_eye_ratio=right_ratio,
            eye_ratio=eye_ratio,
            eye_state=eye_state,
            head_movement=head_movement,
            facial_motion=facial_motion,
            nose_position=nose,
        )

    def reset(self):
        self.previous_nose = None
        self.previous_face_center = None

    def close(self):
        self.landmarker.close()