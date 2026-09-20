"""
AUREX Spatial Intelligence
AirCanvas Hand Tracking Layer
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import mediapipe as mp


@dataclass
class FingerPoint:
    x: float
    y: float
    z: float
    confidence: float

    @property
    def pixel(self) -> tuple[int, int]:
        return (
            int(self.x),
            int(self.y),
        )


@dataclass
class HandState:
    detected: bool
    index_tip: FingerPoint | None
    thumb_tip: FingerPoint | None
    index_extended: bool
    pinch: bool


class AUREXHandTracker:
    """
    MediaPipe Tasks-based hand tracker.

    AUREX uses the index fingertip as the primary
    spatial writing pointer.
    """

    INDEX_TIP = 8
    INDEX_PIP = 6
    THUMB_TIP = 4
    THUMB_IP = 3

    def __init__(
        self,
        model_path: str = (
            "models/hand/hand_landmarker.task"
        ),
        confidence: float = 0.5,
    ) -> None:

        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Hand model not found: "
                f"{self.model_path}"
            )

        self.confidence = confidence

        BaseOptions = (
            mp.tasks.BaseOptions
        )

        HandLandmarkerOptions = (
            mp.tasks.vision.HandLandmarkerOptions
        )

        VisionRunningMode = (
            mp.tasks.vision.RunningMode
        )

        self.landmarker = (
            mp.tasks.vision.HandLandmarker.create_from_options(
                HandLandmarkerOptions(
                    base_options=BaseOptions(
                        model_asset_path=str(
                            self.model_path
                        )
                    ),
                    running_mode=(
                        VisionRunningMode.IMAGE
                    ),
                    num_hands=1,
                    min_hand_detection_confidence=(
                        self.confidence
                    ),
                    min_hand_presence_confidence=(
                        self.confidence
                    ),
                    min_tracking_confidence=(
                        self.confidence
                    ),
                )
            )
        )

    def process(
        self,
        frame,
    ) -> HandState:

        if frame is None:
            return HandState(
                detected=False,
                index_tip=None,
                thumb_tip=None,
                index_extended=False,
                pinch=False,
            )

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        image = mp.Image(
            image_format=(
                mp.ImageFormat.SRGB
            ),
            data=rgb,
        )

        result = self.landmarker.detect(
            image
        )

        if not result.hand_landmarks:
            return HandState(
                detected=False,
                index_tip=None,
                thumb_tip=None,
                index_extended=False,
                pinch=False,
            )

        landmarks = result.hand_landmarks[0]

        height, width = frame.shape[:2]

        index = landmarks[self.INDEX_TIP]
        index_pip = landmarks[self.INDEX_PIP]

        thumb = landmarks[self.THUMB_TIP]
        thumb_ip = landmarks[self.THUMB_IP]

        index_point = FingerPoint(
            x=index.x * width,
            y=index.y * height,
            z=index.z,
            confidence=1.0,
        )

        thumb_point = FingerPoint(
            x=thumb.x * width,
            y=thumb.y * height,
            z=thumb.z,
            confidence=1.0,
        )

        index_extended = (
            index.y < index_pip.y
        )

        pinch_distance = (
            (
                index.x - thumb.x
            ) ** 2
            +
            (
                index.y - thumb.y
            ) ** 2
        ) ** 0.5

        pinch = pinch_distance < 0.08

        return HandState(
            detected=True,
            index_tip=index_point,
            thumb_tip=thumb_point,
            index_extended=index_extended,
            pinch=pinch,
        )

    def draw(
        self,
        frame,
        state: HandState,
    ):

        output = frame.copy()

        if not state.detected:
            return output

        if state.index_tip is not None:

            x, y = (
                state.index_tip.pixel
            )

            cv2.circle(
                output,
                (x, y),
                9,
                (0, 255, 255),
                -1,
            )

            cv2.circle(
                output,
                (x, y),
                15,
                (255, 255, 255),
                2,
            )

        if state.thumb_tip is not None:

            x, y = (
                state.thumb_tip.pixel
            )

            cv2.circle(
                output,
                (x, y),
                7,
                (255, 0, 255),
                -1,
            )

        return output

    def close(self) -> None:

        if self.landmarker is not None:
            self.landmarker.close()
            self.landmarker = None