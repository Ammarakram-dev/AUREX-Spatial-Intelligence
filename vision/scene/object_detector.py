from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ultralytics import YOLO


@dataclass
class SceneObject:
    object_id: str
    label: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int
    class_id: int
    center_x: float
    center_y: float
    width: int
    height: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "object_id": self.object_id,
            "label": self.label,
            "confidence": round(float(self.confidence), 4),
            "bbox": [
                self.x1,
                self.y1,
                self.x2,
                self.y2,
            ],
            "class_id": self.class_id,
            "center": [
                round(float(self.center_x), 4),
                round(float(self.center_y), 4),
            ],
            "width": self.width,
            "height": self.height,
            "metadata": dict(self.metadata),
        }


class AUREXSceneObjectDetector:
    """
    General-purpose scene object detector using Ultralytics YOLO.

    The detector reports visible object categories and bounding boxes.
    It does not infer hidden object properties or human intentions.
    """

    def __init__(
        self,
        model_name: str = "yolo11n.pt",
        confidence_threshold: float = 0.40,
    ) -> None:
        self.model_name = model_name
        self.confidence_threshold = float(confidence_threshold)

        self.model = YOLO(model_name)

        self.names = self.model.names

        self.frame_count = 0

    def detect(self, frame) -> List[SceneObject]:
        self.frame_count += 1

        results = self.model.predict(
            source=frame,
            conf=self.confidence_threshold,
            verbose=False,
        )

        objects: List[SceneObject] = []

        if not results:
            return objects

        result = results[0]

        if result.boxes is None:
            return objects

        boxes = result.boxes

        for index in range(len(boxes)):
            box = boxes[index]

            try:
                class_id = int(
                    box.cls[0].item()
                )

                confidence = float(
                    box.conf[0].item()
                )

                coordinates = (
                    box.xyxy[0]
                    .cpu()
                    .numpy()
                    .tolist()
                )

                x1, y1, x2, y2 = [
                    int(round(value))
                    for value in coordinates
                ]

            except Exception:
                continue

            if isinstance(self.names, dict):
                label = str(
                    self.names.get(
                        class_id,
                        str(class_id),
                    )
                )
            else:
                label = str(
                    self.names[class_id]
                )

            width = max(
                0,
                x2 - x1,
            )

            height = max(
                0,
                y2 - y1,
            )

            center_x = (
                (x1 + x2) / 2.0
            )

            center_y = (
                (y1 + y2) / 2.0
            )

            object_id = (
                f"{label}_{index}"
            )

            objects.append(
                SceneObject(
                    object_id=object_id,
                    label=label,
                    confidence=confidence,
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    class_id=class_id,
                    center_x=center_x,
                    center_y=center_y,
                    width=width,
                    height=height,
                    metadata={
                        "frame": self.frame_count,
                        "model": self.model_name,
                    },
                )
            )

        return objects

    def draw(
        self,
        frame,
        objects: List[SceneObject],
    ):
        import cv2

        for obj in objects:
            cv2.rectangle(
                frame,
                (obj.x1, obj.y1),
                (obj.x2, obj.y2),
                (0, 220, 255),
                2,
            )

            label = (
                f"{obj.label} "
                f"{obj.confidence:.2f}"
            )

            cv2.putText(
                frame,
                label,
                (obj.x1, max(20, obj.y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 220, 255),
                2,
                cv2.LINE_AA,
            )

        return frame

    def close(self) -> None:
        self.model = None