"""
AUREX Spatial Intelligence
Person Tracking Layer
"""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import List

from vision.human_detector import HumanDetection


@dataclass
class TrackedPerson:
    person_id: int
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float

    previous_center: tuple[int, int] | None = None
    current_center: tuple[int, int] = (0, 0)
    movement_distance: float = 0.0
    movement_direction: str = "STATIONARY"
    zone: str = "CENTER"

    def update(self, detection: HumanDetection) -> None:
        old_center = self.current_center

        self.x1 = detection.x1
        self.y1 = detection.y1
        self.x2 = detection.x2
        self.y2 = detection.y2
        self.confidence = detection.confidence

        new_center = detection.center

        self.previous_center = old_center
        self.current_center = new_center

        dx = new_center[0] - old_center[0]
        dy = new_center[1] - old_center[1]

        self.movement_distance = hypot(dx, dy)

        threshold = 8

        if self.movement_distance < threshold:
            self.movement_direction = "STATIONARY"

        elif abs(dx) > abs(dy):
            if dx > 0:
                self.movement_direction = "RIGHT"
            else:
                self.movement_direction = "LEFT"

        else:
            if dy > 0:
                self.movement_direction = "DOWN"
            else:
                self.movement_direction = "UP"

    def update_zone(self, frame_width: int) -> None:
        x = self.current_center[0]

        left_boundary = frame_width / 3
        right_boundary = frame_width * 2 / 3

        if x < left_boundary:
            self.zone = "LEFT"
        elif x > right_boundary:
            self.zone = "RIGHT"
        else:
            self.zone = "CENTER"


class AUREXPersonTracker:
    """
    Lightweight centroid-based person tracker.

    Designed as a foundation for AUREX spatial intelligence.
    """

    def __init__(
        self,
        max_match_distance: float = 120.0,
    ) -> None:

        self.max_match_distance = max_match_distance
        self.next_person_id = 1
        self.people: dict[int, TrackedPerson] = {}

    @staticmethod
    def _distance(
        point_a: tuple[int, int],
        point_b: tuple[int, int],
    ) -> float:

        return hypot(
            point_a[0] - point_b[0],
            point_a[1] - point_b[1],
        )

    def update(
        self,
        detections: List[HumanDetection],
        frame_width: int,
    ) -> List[TrackedPerson]:

        unmatched_detections = set(range(len(detections)))
        matched_people: set[int] = set()

        # Match existing people to the closest detection.
        for person_id, person in list(self.people.items()):

            best_index = None
            best_distance = self.max_match_distance

            for index in unmatched_detections:

                detection = detections[index]

                distance = self._distance(
                    person.current_center,
                    detection.center,
                )

                if distance < best_distance:
                    best_distance = distance
                    best_index = index

            if best_index is not None:

                detection = detections[best_index]

                person.update(detection)
                person.update_zone(frame_width)

                unmatched_detections.remove(best_index)
                matched_people.add(person_id)

        # Create IDs for new people.
        for index in unmatched_detections:

            detection = detections[index]

            person = TrackedPerson(
                person_id=self.next_person_id,
                x1=detection.x1,
                y1=detection.y1,
                x2=detection.x2,
                y2=detection.y2,
                confidence=detection.confidence,
                current_center=detection.center,
            )

            person.update_zone(frame_width)

            self.people[self.next_person_id] = person

            matched_people.add(self.next_person_id)

            self.next_person_id += 1

        # Remove people no longer detected.
        lost_people = set(self.people.keys()) - matched_people

        for person_id in lost_people:
            del self.people[person_id]

        return list(self.people.values())