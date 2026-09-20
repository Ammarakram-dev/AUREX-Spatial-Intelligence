"""
AUREX Spatial Intelligence
Live Spatial Relationship Integration
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from core.spatial.perception_bridge import AUREXSpatialBridge
from core.spatial.relationship_engine import AUREXRelationshipEngine
from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector
from vision.person_tracker import AUREXPersonTracker


def main() -> None:

    camera = AUREXCamera(
        camera_index=0,
        width=1280,
        height=720,
    )

    detector = AUREXHumanDetector()

    tracker = AUREXPersonTracker()

    spatial_bridge = AUREXSpatialBridge()

    relationship_engine = AUREXRelationshipEngine()

    if not camera.open():
        print("Unable to open AUREX camera.")
        return

    print("=" * 70)
    print("AUREX — LIVE SPATIAL RELATIONSHIPS")
    print("=" * 70)
    print("Q = Quit")
    print("=" * 70)

    try:

        while True:

            frame = camera.read()

            if frame is None:
                print("Unable to read camera frame.")
                break

            frame_height, frame_width = frame.shape[:2]

            detections = detector.detect(frame)

            tracked_people = tracker.update(
                detections,
                frame_width=frame_width,
            )

            world = spatial_bridge.update_people(
                tracked_people,
                frame_width=frame_width,
                frame_height=frame_height,
            )

            relationships = relationship_engine.apply_to_world(
                world
            )

            for person in tracked_people:

                center_x, center_y = person.current_center

                center_x = int(center_x)
                center_y = int(center_y)

                cv2.circle(
                    frame,
                    (center_x, center_y),
                    8,
                    (255, 255, 255),
                    -1,
                )

                label = (
                    f"ID {person.person_id} | "
                    f"{person.movement_direction}"
                )

                cv2.putText(
                    frame,
                    label,
                    (center_x + 12, center_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            cv2.rectangle(
                frame,
                (10, 10),
                (500, 125),
                (0, 0, 0),
                -1,
            )

            cv2.putText(
                frame,
                "AUREX SPATIAL RELATIONSHIPS",
                (25, 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.68,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Humans: {len(tracked_people)}",
                (25, 66),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Relationships: {len(relationships)}",
                (25, 91),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            if relationships:

                relationship = relationships[0]

                relation_text = (
                    f"{relationship.source_id} "
                    f"{relationship.relationship.value} "
                    f"{relationship.target_id}"
                )

                cv2.putText(
                    frame,
                    relation_text[:65],
                    (25, 116),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

            cv2.imshow(
                "AUREX - Spatial Relationships",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    finally:

        camera.release()

        cv2.destroyAllWindows()

    print()
    print("Live Spatial Relationship test stopped.")


if __name__ == "__main__":
    main()