import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from vision.camera import AUREXCamera
from vision.pose_estimator import AUREXPoseEstimator
from vision.posture_analyzer import AUREXPostureAnalyzer


def main():
    print("=" * 60)
    print("AUREX POSTURE INTELLIGENCE TEST")
    print("=" * 60)

    estimator = AUREXPoseEstimator()
    analyzer = AUREXPostureAnalyzer()

    try:
        with AUREXCamera(
            width=640,
            height=480,
        ) as camera:

            print("Camera opened.")
            print("Posture intelligence is active.")
            print("Try standing, sitting and moving.")
            print("Press Q to exit.")

            while True:

                frame = camera.read()

                if frame is None:
                    print("Failed to read camera frame.")
                    break

                pose = estimator.process(frame)

                posture = analyzer.analyze(pose)

                output = estimator.draw(
                    frame,
                    pose,
                )

                label = (
                    f"AUREX | "
                    f"{posture.state.value}"
                )

                details = (
                    f"Confidence: "
                    f"{posture.confidence * 100:.1f}%"
                )

                cv2.putText(
                    output,
                    label,
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    output,
                    details,
                    (15, 58),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.imshow(
                    "AUREX Spatial Intelligence - Posture",
                    output,
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        estimator.close()
        cv2.destroyAllWindows()

    print()
    print("Posture analysis test completed successfully.")


if __name__ == "__main__":
    main()