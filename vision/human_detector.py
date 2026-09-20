from __future__ import annotations

from dataclasses import dataclass
from typing import List

import cv2
from ultralytics import YOLO


@dataclass
class HumanDetection:
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    class_id: int = 0

    @property
    def center(self) -> tuple[int, int]:
        return (
            (self.x1 + self.x2) // 2,
            (self.y1 + self.y2) // 2,
        )

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1


class AUREXHumanDetector:
    """
    Lightweight human detector for the AUREX perception pipeline.

    Only the COCO 'person' class is returned.
    """

    PERSON_CLASS_ID = 0

    def __init__(
        self,
        model_name: str = "yolo11n.pt",
        confidence: float = 0.45,
    ) -> None:
        self.model_name = model_name
        self.confidence = confidence
        self.model = YOLO(model_name)

    def detect(self, frame) -> List[HumanDetection]:
        if frame is None:
            return []

        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            classes=[self.PERSON_CLASS_ID],
            verbose=False,
        )

        detections: List[HumanDetection] = []

        if not results:
            return detections

        result = results[0]

        if result.boxes is None:
            return detections

        for box in result.boxes:
            xyxy = box.xyxy[0].tolist()

            x1, y1, x2, y2 = map(int, xyxy)
            confidence = float(box.conf[0].item())
            class_id = int(box.cls[0].item())

            detections.append(
                HumanDetection(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    confidence=confidence,
                    class_id=class_id,
                )
            )

        return detections

    @staticmethod
    def draw(frame, detections: List[HumanDetection]):
        output = frame.copy()

        for index, detection in enumerate(detections, start=1):
            cv2.rectangle(
                output,
                (detection.x1, detection.y1),
                (detection.x2, detection.y2),
                (0, 255, 0),
                2,
            )

            label = (
                f"PERSON {index} "
                f"{detection.confidence * 100:.1f}%"
            )

            cv2.putText(
                output,
                label,
                (detection.x1, max(25, detection.y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

        return output