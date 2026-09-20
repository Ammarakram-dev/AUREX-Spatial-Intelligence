"""
AUREX Spatial Intelligence
Face Detection and Landmark Extraction
Phase 23
"""

from dataclasses import dataclass
from typing import Optional

import cv2
import mediapipe as mp


@dataclass
class FaceRepresentation:
    detected: bool
    confidence: float
    bbox: Optional[tuple]
    landmarks: list


class AUREXFaceDetector:
    """
    Face detection using the MediaPipe Tasks API.

    The detector uses the local MediaPipe face detector
    model and returns a normalized facial representation.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
    ) -> None:

        self.min_detection_confidence = (
            min_detection_confidence
        )

        self.detector = None

        try:

            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision

            model_path = (
                "models/face_detector/"
                "blaze_face_short_range.tflite"
            )

            base_options = (
                python.BaseOptions(
                    model_asset_path=model_path
                )
            )

            options = (
                vision.FaceDetectorOptions(
                    base_options=base_options,
                    min_detection_confidence=(
                        self.min_detection_confidence
                    ),
                )
            )

            self.detector = (
                vision.FaceDetector.create_from_options(
                    options
                )
            )

        except Exception as exc:

            raise RuntimeError(
                "AUREX face detector could not "
                "initialize MediaPipe Tasks. "
                f"Reason: {exc}"
            ) from exc

    def detect(
        self,
        frame,
    ) -> Optional[FaceRepresentation]:

        if frame is None:
            return FaceRepresentation(
                detected=False,
                confidence=0.0,
                bbox=None,
                landmarks=[],
            )

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb,
        )

        result = self.detector.detect(
            mp_image
        )

        if not result.detections:

            return FaceRepresentation(
                detected=False,
                confidence=0.0,
                bbox=None,
                landmarks=[],
            )

        detection = max(
            result.detections,
            key=lambda item: (
                item.categories[0].score
                if item.categories
                else 0.0
            ),
        )

        confidence = float(
            detection.categories[0].score
            if detection.categories
            else 0.0
        )

        bbox = detection.bounding_box

        height, width = frame.shape[:2]

        x1 = max(
            0,
            int(bbox.origin_x),
        )

        y1 = max(
            0,
            int(bbox.origin_y),
        )

        x2 = min(
            width - 1,
            int(
                bbox.origin_x
                + bbox.width
            ),
        )

        y2 = min(
            height - 1,
            int(
                bbox.origin_y
                + bbox.height
            ),
        )

        landmarks = []

        for keypoint in (
            detection.keypoints
            if hasattr(detection, "keypoints")
            else []
        ):

            landmarks.append(
                (
                    float(keypoint.x),
                    float(keypoint.y),
                )
            )

        return FaceRepresentation(
            detected=True,
            confidence=confidence,
            bbox=(x1, y1, x2, y2),
            landmarks=landmarks,
        )

    def close(self) -> None:

        if self.detector is not None:

            self.detector.close()
            self.detector = None