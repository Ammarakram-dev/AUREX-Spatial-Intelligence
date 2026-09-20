"""
AUREX Spatial Intelligence
Live Context Intelligence

Phase 18
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from core.intelligence.context_engine import (
    AUREXContextEngine,
)

from core.spatial.perception_bridge import (
    AUREXSpatialBridge,
)

from core.spatial.relationship_engine import (
    AUREXRelationshipEngine,
)

from vision.camera import (
    AUREXCamera,
)

from vision.human_detector import (
    AUREXHumanDetector,
)

from vision.person_tracker import (
    AUREXPersonTracker,
)


def main() -> None:

    camera = AUREXCamera(
        camera_index=0,
        width=1280,
        height=720,
    )

    detector = AUREXHumanDetector()

    tracker = AUREXPersonTracker()

    spatial_bridge = AUREXSpatialBridge()

    relationship_engine = (
        AUREXRelationshipEngine()
    )

    context_engine = (
        AUREXContextEngine()
    )

    if not camera.open():

        print(
            "Unable to open AUREX camera."
        )

        return

    print("=" * 75)
    print("AUREX — LIVE CONTEXT INTELLIGENCE")
    print("=" * 75)
    print("Q = Quit")
    print("=" * 75)

    try:

        while True:

            frame = camera.read()

            if frame is None:

                print(
                    "Unable to read camera frame."
                )

                break

            frame_height, frame_width = (
                frame.shape[:2]
            )

            detections = detector.detect(
                frame
            )

            tracked_people = tracker.update(
                detections,
                frame_width=frame_width,
            )

            world = (
                spatial_bridge.update_people(
                    tracked_people,
                    frame_width=frame_width,
                    frame_height=frame_height,
                )
            )

            relationships = (
                relationship_engine.apply_to_world(
                    world
                )
            )

            context = (
                context_engine.analyze_tracked_people(
                    tracked_people,
                    relationships=relationships,
                )
            )

            for person in tracked_people:

                center_x, center_y = (
                    person.current_center
                )

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
                    (
                        center_x + 12,
                        center_y,
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            cv2.rectangle(
                frame,
                (10, 10),
                (620, 185),
                (0, 0, 0),
                -1,
            )

            context_name = (
                context.context_type.value
                .replace("_", " ")
                .upper()
            )

            confidence_percent = int(
                context.confidence * 100
            )

            cv2.putText(
                frame,
                "AUREX CONTEXT INTELLIGENCE",
                (25, 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.68,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Context: {context_name}",
                (25, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.56,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Confidence: {confidence_percent}%",
                (25, 96),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.56,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"People: {context.people_count}",
                (25, 122),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.56,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Moving: {len(context.moving_people)}",
                (25, 148),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.56,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Relationships: {context.relationship_count}",
                (250, 122),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.56,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Evidence: {len(context.evidence)}",
                (250, 148),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.56,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            if context.approaching_people:

                cv2.putText(
                    frame,
                    "Approaching activity detected",
                    (25, 174),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

            elif context.lying_people:

                cv2.putText(
                    frame,
                    "Potential incident context",
                    (25, 174),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

            cv2.imshow(
                "AUREX - Context Intelligence",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                break

    finally:

        camera.release()

        cv2.destroyAllWindows()

    print()
    print(
        "Live Context Intelligence test stopped."
    )


if __name__ == "__main__":
    main()