"""
AUREX Spatial Intelligence
Phase 23
Real Camera Face Enrollment and Identity Matching
"""

import sys
import time
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vision.camera import AUREXCamera
from identity.face_detector import AUREXFaceDetector
from identity.identity_manager import AUREXIdentityManager


IDENTITY_NAME = "AUREX_USER"


def main() -> None:

    print("=" * 78)
    print("AUREX — REAL CAMERA FACE IDENTITY")
    print("=" * 78)

    camera = AUREXCamera()
    detector = AUREXFaceDetector()
    manager = AUREXIdentityManager(
        threshold=0.90
    )

    if not camera.open():

        print()
        print("ERROR: Could not open camera.")
        detector.close()
        return

    print()
    print("Camera: ACTIVE")
    print("Face detection: ACTIVE")
    print("Face representation: ACTIVE")
    print()
    print("ENROLLMENT")
    print("Look directly toward the camera.")
    print("Keep your face visible for a few seconds.")
    print("Press E to enroll the current face.")
    print()
    print("After enrollment:")
    print("Move naturally and test live matching.")
    print("Press Q to quit.")
    print()

    enrolled = False
    enrollment_confidence = 0.0

    matched_frames = 0
    detected_frames = 0
    total_frames = 0

    last_identity = None
    last_confidence = 0.0

    try:

        while True:

            frame = camera.read()

            if frame is None:
                print("Camera frame unavailable.")
                break

            total_frames += 1

            result = detector.detect(frame)

            face_detected = (
                result is not None
                and result.detected
            )

            if face_detected:

                detected_frames += 1

                x1, y1, x2, y2 = (
                    result.bbox
                )

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 255, 255),
                    2,
                )

                for point in result.landmarks:

                    px = int(
                        point[0]
                        * frame.shape[1]
                    )

                    py = int(
                        point[1]
                        * frame.shape[0]
                    )

                    cv2.circle(
                        frame,
                        (px, py),
                        3,
                        (255, 255, 255),
                        -1,
                    )

                cv2.putText(
                    frame,
                    f"FACE "
                    f"{result.confidence * 100:.1f}%",
                    (x1, max(25, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

            identity_text = "NOT ENROLLED"
            state_text = "WAITING"

            if enrolled and face_detected:

                match = manager.match(
                    result.landmarks
                )

                last_identity = (
                    match.identity
                )

                last_confidence = (
                    match.confidence
                )

                if match.matched:

                    matched_frames += 1

                    identity_text = (
                        match.identity
                    )

                    state_text = "VERIFIED"

                else:

                    identity_text = "UNKNOWN"
                    state_text = "REJECTED"

            elif not enrolled:

                identity_text = "NOT ENROLLED"
                state_text = "ENROLLMENT REQUIRED"

            elif not face_detected:

                identity_text = "NO FACE"
                state_text = "WAITING"

            cv2.putText(
                frame,
                "FACE: "
                + (
                    "DETECTED"
                    if face_detected
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
                "IDENTITY: "
                + identity_text,
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "STATE: "
                + state_text,
                (20, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"CONFIDENCE: "
                f"{last_confidence:.3f}",
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "E = ENROLL CURRENT FACE",
                (20, frame.shape[0] - 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "Q = QUIT",
                (20, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
            )

            cv2.imshow(
                "AUREX - Face Identity",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("e"):

                if not face_detected:

                    print()
                    print(
                        "ENROLLMENT FAILED: "
                        "No face detected."
                    )

                else:

                    success = manager.enroll(
                        IDENTITY_NAME,
                        result.landmarks,
                    )

                    if success:

                        enrolled = True
                        enrollment_confidence = (
                            result.confidence
                        )

                        print()
                        print("=" * 78)
                        print(
                            "FACE ENROLLMENT COMPLETE"
                        )
                        print("=" * 78)
                        print(
                            f"Identity: "
                            f"{IDENTITY_NAME}"
                        )
                        print(
                            f"Face confidence: "
                            f"{enrollment_confidence:.3f}"
                        )
                        print()
                        print(
                            "Now move naturally "
                            "and test matching."
                        )
                        print("=" * 78)

                    else:

                        print()
                        print(
                            "ENROLLMENT FAILED."
                        )

            if key == ord("q"):
                break

            time.sleep(0.01)

    finally:

        camera.release()
        detector.close()
        cv2.destroyAllWindows()

        print()
        print("=" * 78)
        print("LIVE FACE IDENTITY SESSION COMPLETE")
        print("=" * 78)

        print(
            f"Total frames: "
            f"{total_frames}"
        )

        print(
            f"Frames with face: "
            f"{detected_frames}"
        )

        print(
            f"Matched frames: "
            f"{matched_frames}"
        )

        print(
            f"Enrollment status: "
            f"{'COMPLETE' if enrolled else 'NOT COMPLETED'}"
        )

        if enrolled:

            print(
                f"Enrolled identity: "
                f"{IDENTITY_NAME}"
            )

        print("=" * 78)


if __name__ == "__main__":
    main()