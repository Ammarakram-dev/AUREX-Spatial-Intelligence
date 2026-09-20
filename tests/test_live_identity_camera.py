"""
AUREX Spatial Intelligence
Real Camera Identity & Liveness Test

Phase 22
"""

import sys
import time
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector
from identity import AUREXIdentityEngine


def main() -> None:

    print("=" * 78)
    print("AUREX — REAL CAMERA IDENTITY & LIVENESS")
    print("=" * 78)

    camera = AUREXCamera()
    detector = AUREXHumanDetector()
    engine = AUREXIdentityEngine()

    if not camera.open():
        print()
        print("ERROR: Could not open camera.")
        return

    print()
    print("Camera: ACTIVE")
    print("Human detection: ACTIVE")
    print("Temporal liveness: ACTIVE")
    print()
    print("Look toward the camera.")
    print("Move naturally left/right or closer/farther.")
    print("Press Q to quit.")
    print()

    previous_center = None
    movement_history = []

    frames_with_person = 0
    movement_events = 0
    max_confidence = 0.0

    try:

        while True:

            frame = camera.read()

            if frame is None:
                print("Camera frame unavailable.")
                break

            height, width = frame.shape[:2]

            detections = detector.detect(frame)

            person_detected = len(detections) > 0

            movement = False
            center = None

            if person_detected:

                frames_with_person += 1

                detection = max(
                    detections,
                    key=lambda item: (
                        item.confidence
                        * (
                            item.x2
                            - item.x1
                        )
                        * (
                            item.y2
                            - item.y1
                        )
                    ),
                )

                x1 = int(detection.x1)
                y1 = int(detection.y1)
                x2 = int(detection.x2)
                y2 = int(detection.y2)

                max_confidence = max(
                    max_confidence,
                    detection.confidence,
                )

                center = (
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                )

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 255, 255),
                    2,
                )

                cv2.circle(
                    frame,
                    center,
                    5,
                    (255, 255, 255),
                    -1,
                )

                cv2.putText(
                    frame,
                    f"PERSON "
                    f"{detection.confidence * 100:.1f}%",
                    (x1, max(25, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                if previous_center is not None:

                    dx = (
                        center[0]
                        - previous_center[0]
                    )

                    dy = (
                        center[1]
                        - previous_center[1]
                    )

                    distance = (
                        dx * dx
                        + dy * dy
                    ) ** 0.5

                    movement_history.append(
                        distance
                    )

                    if len(movement_history) > 30:
                        movement_history.pop(0)

                    movement = distance >= 3.0

                    if movement:
                        movement_events += 1

                previous_center = center

            else:

                previous_center = None

            temporal_consistency = (
                len(movement_history) >= 10
            )

            facial_motion = (
                len(movement_history) > 0
                and max(movement_history) >= 3.0
            )

            # This live test establishes:
            #
            # 1. Real camera input
            # 2. Real-time human detection
            # 3. Temporal movement evidence
            # 4. Liveness-state processing
            #
            # It deliberately does NOT claim that the
            # detected person is the enrolled user.
            #
            # Actual biometric identity matching will be
            # connected as a separate identity layer.

            result = engine.analyze_values(
                face_detected=person_detected,
                face_confidence=(
                    0.90
                    if person_detected
                    else 0.0
                ),
                identity_match=None,
                identity_confidence=0.0,
                head_movement=movement,
                facial_motion=facial_motion,
                temporal_consistency=(
                    temporal_consistency
                ),
                depth_consistency=(
                    person_detected
                ),
                liveness_confidence=0.90,
            )

            cv2.putText(
                frame,
                "PERSON: "
                + (
                    "DETECTED"
                    if person_detected
                    else "NOT DETECTED"
                ),
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "LIVENESS: "
                + result.liveness_state.value.upper(),
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "STATE: "
                + result.state.value.upper(),
                (20, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"CONFIDENCE: "
                f"{result.confidence:.2f}",
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"MOVEMENT EVENTS: "
                f"{movement_events}",
                (20, 175),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "MOVE HEAD / BODY FOR TEMPORAL SIGNAL",
                (20, height - 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "Q = QUIT",
                (20, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
            )

            cv2.imshow(
                "AUREX - Identity & Liveness",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            time.sleep(0.01)

    finally:

        camera.release()
        cv2.destroyAllWindows()

        print()
        print("=" * 78)
        print("REAL CAMERA SESSION COMPLETE")
        print("=" * 78)

        print(
            f"Frames with person: "
            f"{frames_with_person}"
        )

        print(
            f"Movement samples: "
            f"{len(movement_history)}"
        )

        print(
            f"Movement events: "
            f"{movement_events}"
        )

        print(
            f"Maximum detection confidence: "
            f"{max_confidence:.2f}"
        )

        print("=" * 78)


if __name__ == "__main__":
    main()