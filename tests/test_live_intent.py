"""
AUREX Spatial Intelligence
Live Intent Intelligence

Phase 19
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

from core.intent.intent_engine import (
    AUREXIntentEngine,
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

    intent_engine = (
        AUREXIntentEngine()
    )

    if not camera.open():

        print(
            "Unable to open AUREX camera."
        )

        return

    print("=" * 78)
    print("AUREX — LIVE INTENT INTELLIGENCE")
    print("=" * 78)
    print("Q = Quit")
    print("=" * 78)

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

            intent = intent_engine.infer(
                context=context,
                human_states=tracked_people,
                relationships=relationships,
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
                    f"ID {person.person_id}"
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
                (700, 225),
                (0, 0, 0),
                -1,
            )

            intent_name = (
                intent.primary.intent_type.value
                .replace("_", " ")
                .upper()
            )

            action_name = (
                intent.action.action_type.value
                .replace("_", " ")
                .upper()
                if intent.action
                else "NONE"
            )

            confidence_percent = int(
                intent.primary.confidence * 100
            )

            cv2.putText(
                frame,
                "AUREX INTENT INTELLIGENCE",
                (25, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.70,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Context: {context.context_type.value}",
                (25, 72),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Intent: {intent_name}",
                (25, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.58,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Confidence: {confidence_percent}%",
                (25, 128),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Proposed Action: {action_name}",
                (25, 156),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            confirmation = (
                "YES"
                if (
                    intent.action
                    and intent.action.requires_confirmation
                )
                else "NO"
            )

            cv2.putText(
                frame,
                f"Confirmation Required: {confirmation}",
                (25, 184),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Evidence: {len(intent.primary.evidence)}",
                (25, 212),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "AUREX - Intent Intelligence",
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
        "Live Intent Intelligence test stopped."
    )


if __name__ == "__main__":
    main()