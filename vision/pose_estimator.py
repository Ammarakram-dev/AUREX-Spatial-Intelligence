"""
AUREX Spatial Intelligence
Human Pose Estimation Layer
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import cv2
from ultralytics import YOLO


@dataclass
class PosePoint:
    landmark_id: int
    x: float
    y: float
    confidence: float


@dataclass
class HumanPose:
    points: List[PosePoint]
    confidence: float


class AUREXPoseEstimator:
    """
    YOLO-based human pose estimator.

    Uses a lightweight pose model and exposes
    normalized body landmarks for AUREX.
    """

    def __init__(
        self,
        model_name: str = "yolo11n-pose.pt",
        confidence: float = 0.45,
    ) -> None:

        self.model_name = model_name
        self.confidence = confidence

        self.model = YOLO(model_name)

    def process(self, frame) -> HumanPose | None:

        if frame is None:
            return None

        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            classes=[0],
            verbose=False,
        )

        if not results:
            return None

        result = results[0]

        if result.keypoints is None:
            return None

        if len(result.keypoints) == 0:
            return None

        # Select the most confident detected person.
        person_index = 0

        if result.boxes is not None and len(result.boxes) > 1:
            confidences = result.boxes.conf.cpu().tolist()
            person_index = max(
                range(len(confidences)),
                key=lambda index: confidences[index],
            )

        keypoints = result.keypoints

        xy = keypoints.xy[person_index].cpu().tolist()

        if keypoints.conf is not None:
            point_confidences = (
                keypoints.conf[person_index]
                .cpu()
                .tolist()
            )
        else:
            point_confidences = [1.0] * len(xy)

        frame_height, frame_width = frame.shape[:2]

        points: List[PosePoint] = []

        for index, point in enumerate(xy):

            x_pixel, y_pixel = point

            x_normalized = x_pixel / frame_width
            y_normalized = y_pixel / frame_height

            confidence = float(
                point_confidences[index]
            )

            points.append(
                PosePoint(
                    landmark_id=index,
                    x=x_normalized,
                    y=y_normalized,
                    confidence=confidence,
                )
            )

        person_confidence = 0.0

        if result.boxes is not None:
            person_confidence = float(
                result.boxes.conf[person_index].item()
            )

        return HumanPose(
            points=points,
            confidence=person_confidence,
        )

    def draw(
        self,
        frame,
        pose: HumanPose | None,
    ):
        output = frame.copy()

        if pose is None:
            return output

        height, width = output.shape[:2]

        # YOLO pose skeleton connections.
        connections = [
            (0, 1), (0, 2),
            (1, 3), (2, 4),
            (5, 6),
            (5, 7), (7, 9),
            (6, 8), (8, 10),
            (5, 11), (6, 12),
            (11, 12),
            (11, 13), (13, 15),
            (12, 14), (14, 16),
        ]

        visible = {}

        for point in pose.points:

            if point.confidence < 0.25:
                continue

            x = int(point.x * width)
            y = int(point.y * height)

            visible[point.landmark_id] = (x, y)

            cv2.circle(
                output,
                (x, y),
                4,
                (0, 255, 255),
                -1,
            )

        for start, end in connections:

            if start not in visible or end not in visible:
                continue

            cv2.line(
                output,
                visible[start],
                visible[end],
                (0, 255, 0),
                2,
            )

        return output

    def close(self) -> None:
        """
        Release pose resources.
        """
        self.model = None