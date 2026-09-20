import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector
from vision.person_tracker import AUREXPersonTracker


def main():
    print("=" * 60)
    print("AUREX SPATIAL HUMAN TRACKING TEST")
    print("=" * 60)

    detector = AUREXHumanDetector()
    tracker = AUREXPersonTracker()

    with AUREXCamera(width=640, height=480) as camera:

        print("Camera opened.")
        print("Human detection + tracking is active.")
        print("Press Q to exit.")

        while True:

            frame = camera.read()

            if frame is None:
                print("Failed to read camera frame.")
                break

            detections = detector.detect(frame)

            tracked_people = tracker.update(
                detections,
                frame_width=frame.shape[1],
            )

            output = frame.copy()

            for person in tracked_people:

                cv2.rectangle(
                    output,
                    (person.x1, person.y1),
                    (person.x2, person.y2),
                    (0, 255, 0),
                    2,
                )

                label = (
                    f"PERSON {person.person_id} | "
                    f"{person.confidence * 100:.1f}%"
                )

                spatial_info = (
                    f"{person.zone} | "
                    f"{person.movement_direction}"
                )

                cv2.putText(
                    output,
                    label,
                    (
                        person.x1,
                        max(25, person.y1 - 28),
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    output,
                    spatial_info,
                    (
                        person.x1,
                        max(45, person.y1 - 7),
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            cv2.putText(
                output,
                f"AUREX | Tracked People: {len(tracked_people)}",
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "AUREX Spatial Intelligence - Spatial Tracking",
                output,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()

    print()
    print("Spatial tracking test completed successfully.")


if __name__ == "__main__":
    main()