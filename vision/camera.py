"""
AUREX Spatial Intelligence
Camera Input Layer
"""

from __future__ import annotations

import cv2


class AUREXCamera:
    """
    Webcam interface for AUREX.

    This layer is responsible only for acquiring frames.
    AI interpretation belongs to the perception layer.
    """

    def __init__(
        self,
        camera_index: int = 0,
        width: int = 1280,
        height: int = 720,
    ) -> None:

        self.camera_index = camera_index
        self.width = width
        self.height = height

        self.capture: cv2.VideoCapture | None = None

    def open(self) -> bool:
        """Open the camera."""

        self.capture = cv2.VideoCapture(
            self.camera_index
        )

        if not self.capture.isOpened():
            self.capture.release()
            self.capture = None
            return False

        self.capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.width,
        )

        self.capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.height,
        )

        return True

    def read(self):
        """Read one frame from the camera."""

        if self.capture is None:
            raise RuntimeError(
                "Camera is not open."
            )

        success, frame = self.capture.read()

        if not success:
            return None

        return frame

    def release(self) -> None:
        """Release the camera."""

        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def __enter__(self):
        if not self.open():
            raise RuntimeError(
                "Unable to open AUREX camera."
            )

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        self.release()