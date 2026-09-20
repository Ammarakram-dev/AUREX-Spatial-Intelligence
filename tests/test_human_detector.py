import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector


def main():
    print("=" * 60)
    print("AUREX HUMAN DETECTION TEST")
    print("=" * 60)

    detector = AUREXHumanDetector()

    with AUREXCamera(width=640, height=480) as camera:
        print("Camera opened.")
        print("Human detection is active.")
        print("Press Q to exit.")

        while True:
            frame = camera.read()

            if frame is None:
                print("Failed to read camera frame.")
                break

            detections = detector.detect(frame)

            output = detector.draw(frame, detections)

            cv2.putText(
                output,
                f"AUREX | Humans: {len(detections)}",
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "AUREX Spatial Intelligence - Human Detection",
                output,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()

    print()
    print("Human detection test completed successfully.")


if __name__ == "__main__":
    main()