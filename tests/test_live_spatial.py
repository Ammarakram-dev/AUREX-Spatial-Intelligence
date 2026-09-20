import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from core.spatial.perception_bridge import (
    AUREXSpatialBridge,
)
from vision.camera import AUREXCamera
from vision.human_detector import (
    AUREXHumanDetector,
)
from vision.person_tracker import (
    AUREXPersonTracker,
)


def main():

    print("=" * 60)
    print("AUREX LIVE SPATIAL PERCEPTION")
    print("=" * 60)

    detector = AUREXHumanDetector(
        confidence=0.45
    )

    tracker = AUREXPersonTracker()

    bridge = AUREXSpatialBridge()

    try:

        with AUREXCamera(
            width=640,
            height=480,
        ) as camera:

            print()
            print("Camera opened.")
            print("Live spatial perception active.")
            print("Press Q to exit.")
            print()

            while True:

                frame = camera.read()

                if frame is None:
                    break

                height, width = (
                    frame.shape[:2]
                )

                detections = detector.detect(
                    frame
                )

                people = tracker.update(
                    detections,
                    frame_width=width,
                )

                world = bridge.update_people(
                    people=people,
                    frame_width=width,
                    frame_height=height,
                )

                output = detector.draw(
                    frame,
                    detections,
                )

                for person in people:

                    cv2.putText(
                        output,
                        (
                            f"P{person.person_id} "
                            f"{person.movement_direction}"
                        ),
                        (
                            person.x1,
                            max(
                                25,
                                person.y1 - 10,
                            ),
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

                status = world.status()

                cv2.putText(
                    output,
                    (
                        f"SPATIAL ENTITIES: "
                        f"{status['entities']}"
                    ),
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    output,
                    (
                        f"PEOPLE: "
                        f"{status['people']}"
                    ),
                    (15, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    output,
                    (
                        f"RELATIONSHIPS: "
                        f"{status['relationships']}"
                    ),
                    (15, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.imshow(
                    "AUREX Live Spatial World",
                    output,
                )

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                if key == ord("q"):
                    break

    finally:

        cv2.destroyAllWindows()

    print()
    print("=" * 60)
    print("LIVE SPATIAL TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()