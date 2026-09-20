import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from vision.camera import AUREXCamera
from vision.pose_estimator import AUREXPoseEstimator
from vision.posture_analyzer import AUREXPostureAnalyzer
from vision.fall_guard import AUREXFallGuard


def main():
    print("=" * 60)
    print("AUREX FALLGUARD TEST")
    print("=" * 60)

    estimator = AUREXPoseEstimator()
    analyzer = AUREXPostureAnalyzer()
    fall_guard = AUREXFallGuard()

    try:
        with AUREXCamera(
            width=640,
            height=480,
        ) as camera:

            print("Camera opened.")
            print("FallGuard is active.")
            print("Press Q to exit.")

            while True:

                frame = camera.read()

                if frame is None:
                    print("Failed to read camera frame.")
                    break

                pose = estimator.process(frame)

                posture = analyzer.analyze(pose)

                event = fall_guard.update(
                    person_id=1,
                    posture=posture,
                )

                output = estimator.draw(
                    frame,
                    pose,
                )

                posture_text = (
                    f"POSTURE: "
                    f"{posture.state.value}"
                )

                fall_text = (
                    "FALLGUARD: "
                    + (
                        "POSSIBLE FALL"
                        if event.possible_fall
                        else "NORMAL"
                    )
                )

                confidence_text = (
                    f"EVENT CONFIDENCE: "
                    f"{event.confidence * 100:.1f}%"
                )

                cv2.putText(
                    output,
                    posture_text,
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    output,
                    fall_text,
                    (15, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    output,
                    confidence_text,
                    (15, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.imshow(
                    "AUREX Spatial Intelligence - FallGuard",
                    output,
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        estimator.close()
        cv2.destroyAllWindows()

    print()
    print("FallGuard test completed successfully.")


if __name__ == "__main__":
    main()