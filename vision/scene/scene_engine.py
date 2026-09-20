from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional

from .scene_state import (
    SceneChange,
    SceneChangeType,
    SceneRelationship,
    SceneRelationshipType,
    SceneSnapshot,
)
from .object_detector import SceneObject


class AUREXSceneIntelligence:
    """
    Converts object detections into a structured scene representation.

    Capabilities:
    - object counting
    - spatial relationships
    - person/object proximity
    - scene change detection
    - temporal scene snapshots
    """

    def __init__(
        self,
        near_distance: float = 0.22,
        overlap_threshold: float = 0.12,
    ) -> None:
        self.near_distance = float(
            near_distance
        )

        self.overlap_threshold = float(
            overlap_threshold
        )

        self.previous_counts: Dict[str, int] = {}

        self.frame_number = 0

        self.history: List[
            SceneSnapshot
        ] = []

    @staticmethod
    def _center_distance(
        a: SceneObject,
        b: SceneObject,
        frame_width: int,
        frame_height: int,
    ) -> float:
        dx = (
            a.center_x - b.center_x
        ) / max(1, frame_width)

        dy = (
            a.center_y - b.center_y
        ) / max(1, frame_height)

        return (
            dx * dx +
            dy * dy
        ) ** 0.5

    @staticmethod
    def _iou(
        a: SceneObject,
        b: SceneObject,
    ) -> float:
        left = max(a.x1, b.x1)
        top = max(a.y1, b.y1)
        right = min(a.x2, b.x2)
        bottom = min(a.y2, b.y2)

        intersection_width = max(
            0,
            right - left,
        )

        intersection_height = max(
            0,
            bottom - top,
        )

        intersection = (
            intersection_width *
            intersection_height
        )

        area_a = max(
            0,
            a.x2 - a.x1,
        ) * max(
            0,
            a.y2 - a.y1,
        )

        area_b = max(
            0,
            b.x2 - b.x1,
        ) * max(
            0,
            b.y2 - b.y1,
        )

        union = (
            area_a +
            area_b -
            intersection
        )

        if union <= 0:
            return 0.0

        return intersection / union

    @staticmethod
    def _direction_relationship(
        source: SceneObject,
        target: SceneObject,
    ) -> SceneRelationshipType:
        dx = (
            source.center_x -
            target.center_x
        )

        dy = (
            source.center_y -
            target.center_y
        )

        if abs(dx) >= abs(dy):
            if dx < 0:
                return SceneRelationshipType.LEFT_OF

            return SceneRelationshipType.RIGHT_OF

        if dy < 0:
            return SceneRelationshipType.ABOVE

        return SceneRelationshipType.BELOW

    def _relationship_pair(
        self,
        source: SceneObject,
        target: SceneObject,
        frame_width: int,
        frame_height: int,
    ) -> Optional[
        SceneRelationship
    ]:
        distance = self._center_distance(
            source,
            target,
            frame_width,
            frame_height,
        )

        iou = self._iou(
            source,
            target,
        )

        if iou >= self.overlap_threshold:
            relationship = (
                SceneRelationshipType.OVERLAPPING
            )

            confidence = min(
                0.98,
                0.70 + iou * 0.30,
            )

        elif distance <= self.near_distance:
            if (
                source.label == "person"
                and target.label != "person"
            ):
                relationship = (
                    SceneRelationshipType.PERSON_NEAR_OBJECT
                )
            elif (
                target.label == "person"
                and source.label != "person"
            ):
                relationship = (
                    SceneRelationshipType.PERSON_NEAR_OBJECT
                )
            else:
                relationship = (
                    SceneRelationshipType.NEAR
                )

            confidence = max(
                0.50,
                min(
                    0.95,
                    1.0 - distance,
                ),
            )

        else:
            relationship = (
                self._direction_relationship(
                    source,
                    target,
                )
            )

            # Directional relationships are lower confidence
            # than actual proximity/overlap.
            confidence = 0.55

        return SceneRelationship(
            source_id=source.object_id,
            source_label=source.label,
            relationship=relationship,
            target_id=target.object_id,
            target_label=target.label,
            confidence=confidence,
            distance=distance,
            metadata={
                "iou": round(iou, 4),
            },
        )

    def analyze_relationships(
        self,
        objects: List[SceneObject],
        frame_width: int,
        frame_height: int,
    ) -> List[SceneRelationship]:
        relationships: List[
            SceneRelationship
        ] = []

        for index, source in enumerate(objects):
            for target in objects[index + 1:]:
                relationship = (
                    self._relationship_pair(
                        source,
                        target,
                        frame_width,
                        frame_height,
                    )
                )

                if relationship is None:
                    continue

                relationships.append(
                    relationship
                )

        return relationships

    def detect_changes(
        self,
        class_counts: Dict[str, int],
    ) -> List[SceneChange]:
        changes: List[SceneChange] = []

        all_labels = set(
            self.previous_counts
        ) | set(class_counts)

        for label in sorted(all_labels):
            before = self.previous_counts.get(
                label,
                0,
            )

            after = class_counts.get(
                label,
                0,
            )

            if before == after:
                continue

            if before == 0 and after > 0:
                change_type = (
                    SceneChangeType.OBJECT_APPEARED
                )

            elif before > 0 and after == 0:
                change_type = (
                    SceneChangeType.OBJECT_DISAPPEARED
                )

            else:
                change_type = (
                    SceneChangeType.COUNT_CHANGED
                )

            difference = abs(
                after - before
            )

            confidence = min(
                0.95,
                0.55 + difference * 0.10,
            )

            changes.append(
                SceneChange(
                    change_type=change_type,
                    label=label,
                    count_before=before,
                    count_after=after,
                    confidence=confidence,
                )
            )

        self.previous_counts = dict(
            class_counts
        )

        return changes

    def analyze(
        self,
        objects: List[SceneObject],
        frame_width: int,
        frame_height: int,
    ) -> SceneSnapshot:
        self.frame_number += 1

        class_counts = dict(
            Counter(
                obj.label
                for obj in objects
            )
        )

        relationships = (
            self.analyze_relationships(
                objects,
                frame_width,
                frame_height,
            )
        )

        changes = self.detect_changes(
            class_counts
        )

        if objects:
            object_confidence = sum(
                obj.confidence
                for obj in objects
            ) / len(objects)
        else:
            object_confidence = 0.50

        relationship_bonus = min(
            0.15,
            len(relationships) * 0.01,
        )

        scene_confidence = min(
            0.98,
            object_confidence +
            relationship_bonus,
        )

        snapshot = SceneSnapshot(
            frame_number=self.frame_number,
            object_count=len(objects),
            class_counts=class_counts,
            objects=[
                obj.to_dict()
                for obj in objects
            ],
            relationships=[
                item.to_dict()
                for item in relationships
            ],
            changes=[
                item.to_dict()
                for item in changes
            ],
            scene_confidence=scene_confidence,
            metadata={
                "frame_width": frame_width,
                "frame_height": frame_height,
            },
        )

        self.history.append(snapshot)

        if len(self.history) > 60:
            self.history.pop(0)

        return snapshot

    def reset(self) -> None:
        self.previous_counts.clear()
        self.history.clear()
        self.frame_number = 0

    def status(self) -> Dict[str, Any]:
        return {
            "frame_number": self.frame_number,
            "history_size": len(self.history),
            "previous_classes": dict(
                self.previous_counts
            ),
        }