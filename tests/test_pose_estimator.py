import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from vision.camera import AUREXCamera
from vision.pose_estimator import AUREXPoseEstimator


def main():
    print("=" * 60)
    print("AUREX HUMAN POSE TEST")
    print("=" * 60)

    estimator = AUREXPoseEstimator()

    try:
        with AUREXCamera(
            width=640,
            height=480,
        ) as camera:

            print("Camera opened.")
            print("Pose estimation is active.")
            print("Press Q to exit.")

            while True:

                frame = camera.read()

                if frame is None:
                    print("Failed to read camera frame.")
                    break

                pose = estimator.process(frame)

                output = estimator.draw(
                    frame,
                    pose,
                )

                status = (
                    "POSE DETECTED"
                    if pose is not None
                    else "NO POSE"
                )

                cv2.putText(
                    output,
                    f"AUREX | {status}",
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.imshow(
                    "AUREX Spatial Intelligence - Pose",
                    output,
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        estimator.close()
        cv2.destroyAllWindows()

    print()
    print("Pose estimation test completed successfully.")


if __name__ == "__main__":
    main()