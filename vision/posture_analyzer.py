"""
AUREX Spatial Intelligence
Human Posture Analysis Layer
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import atan2, degrees, hypot

from vision.pose_estimator import HumanPose


class PostureState(str, Enum):
    UNKNOWN = "UNKNOWN"
    STANDING = "STANDING"
    WALKING = "WALKING"
    SITTING = "SITTING"
    CROUCHING = "CROUCHING"
    LYING = "LYING"


@dataclass
class PostureResult:
    state: PostureState
    confidence: float
    torso_angle: float
    body_width: float
    body_height: float
    vertical_ratio: float


class AUREXPostureAnalyzer:
    """
    Geometry-based human posture analyzer.

    The classifier uses body landmark relationships rather
    than treating a single frame as a medical diagnosis.
    """

    # YOLO pose landmark indices:
    # 0 nose
    # 5 left shoulder
    # 6 right shoulder
    # 11 left hip
    # 12 right hip
    # 13 left knee
    # 14 right knee
    # 15 left ankle
    # 16 right ankle

    LEFT_SHOULDER = 5
    RIGHT_SHOULDER = 6
    LEFT_HIP = 11
    RIGHT_HIP = 12
    LEFT_KNEE = 13
    RIGHT_KNEE = 14
    LEFT_ANKLE = 15
    RIGHT_ANKLE = 16

    def analyze(
        self,
        pose: HumanPose | None,
    ) -> PostureResult:

        if pose is None:
            return PostureResult(
                state=PostureState.UNKNOWN,
                confidence=0.0,
                torso_angle=0.0,
                body_width=0.0,
                body_height=0.0,
                vertical_ratio=0.0,
            )

        points = {
            point.landmark_id: point
            for point in pose.points
            if point.confidence >= 0.25
        }

        required = [
            self.LEFT_SHOULDER,
            self.RIGHT_SHOULDER,
            self.LEFT_HIP,
            self.RIGHT_HIP,
        ]

        if not all(index in points for index in required):
            return PostureResult(
                state=PostureState.UNKNOWN,
                confidence=0.0,
                torso_angle=0.0,
                body_width=0.0,
                body_height=0.0,
                vertical_ratio=0.0,
            )

        left_shoulder = points[self.LEFT_SHOULDER]
        right_shoulder = points[self.RIGHT_SHOULDER]
        left_hip = points[self.LEFT_HIP]
        right_hip = points[self.RIGHT_HIP]

        shoulder_x = (
            left_shoulder.x + right_shoulder.x
        ) / 2

        shoulder_y = (
            left_shoulder.y + right_shoulder.y
        ) / 2

        hip_x = (
            left_hip.x + right_hip.x
        ) / 2

        hip_y = (
            left_hip.y + right_hip.y
        ) / 2

        torso_dx = hip_x - shoulder_x
        torso_dy = hip_y - shoulder_y

        torso_angle = abs(
            degrees(
                atan2(
                    torso_dx,
                    torso_dy,
                )
            )
        )

        body_points = list(points.values())

        min_x = min(point.x for point in body_points)
        max_x = max(point.x for point in body_points)
        min_y = min(point.y for point in body_points)
        max_y = max(point.y for point in body_points)

        body_width = max_x - min_x
        body_height = max_y - min_y

        if body_width <= 0:
            vertical_ratio = 0.0
        else:
            vertical_ratio = body_height / body_width

        confidence = min(
            1.0,
            max(
                0.0,
                pose.confidence,
            ),
        )

        state = self._classify(
            points=points,
            torso_angle=torso_angle,
            vertical_ratio=vertical_ratio,
        )

        return PostureResult(
            state=state,
            confidence=confidence,
            torso_angle=torso_angle,
            body_width=body_width,
            body_height=body_height,
            vertical_ratio=vertical_ratio,
        )

    def _classify(
        self,
        points,
        torso_angle: float,
        vertical_ratio: float,
    ) -> PostureState:

        # A nearly horizontal torso with a wide horizontal
        # body footprint is a possible lying posture.
        if (
            torso_angle > 65
            and vertical_ratio < 0.85
        ):
            return PostureState.LYING

        # Strongly vertical body.
        if torso_angle < 25:

            if self._is_sitting(points):
                return PostureState.SITTING

            if self._is_crouching(points):
                return PostureState.CROUCHING

            return PostureState.STANDING

        # Intermediate torso angles can indicate crouching
        # or transitional movement.
        if torso_angle < 50:

            if self._is_crouching(points):
                return PostureState.CROUCHING

            return PostureState.WALKING

        return PostureState.UNKNOWN

    def _is_sitting(self, points) -> bool:

        if not all(
            index in points
            for index in [
                self.LEFT_HIP,
                self.RIGHT_HIP,
                self.LEFT_KNEE,
                self.RIGHT_KNEE,
            ]
        ):
            return False

        left_hip = points[self.LEFT_HIP]
        right_hip = points[self.RIGHT_HIP]

        left_knee = points[self.LEFT_KNEE]
        right_knee = points[self.RIGHT_KNEE]

        hip_y = (
            left_hip.y + right_hip.y
        ) / 2

        knee_y = (
            left_knee.y + right_knee.y
        ) / 2

        return knee_y < hip_y + 0.12

    def _is_crouching(self, points) -> bool:

        if not all(
            index in points
            for index in [
                self.LEFT_HIP,
                self.RIGHT_HIP,
                self.LEFT_KNEE,
                self.RIGHT_KNEE,
            ]
        ):
            return False

        left_hip = points[self.LEFT_HIP]
        right_hip = points[self.RIGHT_HIP]

        left_knee = points[self.LEFT_KNEE]
        right_knee = points[self.RIGHT_KNEE]

        hip_y = (
            left_hip.y + right_hip.y
        ) / 2

        knee_y = (
            left_knee.y + right_knee.y
        ) / 2

        return abs(knee_y - hip_y) < 0.15