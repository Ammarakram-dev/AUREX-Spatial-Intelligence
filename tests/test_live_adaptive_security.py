import cv2
import time

from vision.camera import AUREXCamera
from identity.face_detector import AUREXFaceDetector
from identity.face_embedding import AUREXFaceEmbedding
from identity.identity_manager import AUREXIdentityManager
from identity.liveness import AUREXLivenessEvaluator
from core.security.adaptive_security import AUREXAdaptiveSecurity


WINDOW_NAME = "AUREX Phase 24 - Adaptive Security"


def main():
    camera = AUREXCamera()
    face_detector = AUREXFaceDetector()
    identity_manager = AUREXIdentityManager()
    liveness_evaluator = AUREXLivenessEvaluator()
    adaptive_security = AUREXAdaptiveSecurity()

    enrolled = False
    enrollment_landmarks = None

    print("=" * 70)
    print("AUREX PHASE 24: LIVE ADAPTIVE SECURITY")
    print("=" * 70)
    print()
    print("Controls:")
    print("  E = enroll current face")
    print("  R = reset adaptive security history")
    print("  Q = quit")
    print()
    print("Stand in front of the camera.")
    print("Enroll your face first using E.")
    print()

    try:
        if not camera.open():
            print("ERROR: Camera could not be opened.")
            return

        while True:
            frame = camera.read()

            if frame is None:
                print("Camera frame unavailable.")
                break

            height, width = frame.shape[:2]

            face = face_detector.detect(frame)

            face_detected = face.detected
            face_confidence = face.confidence if face_detected else 0.0

            identity_match = None
            identity_value = None
            identity_confidence = 0.0

            if face_detected and face.landmarks:
                if enrolled:
                    identity_match = identity_manager.match(face.landmarks)

                    identity_value = identity_match.matched
                    identity_confidence = identity_match.confidence

                elif enrollment_landmarks is not None:
                    identity_value = False

            # Lightweight temporal liveness signal.
            # This phase intentionally combines real face presence,
            # identity matching, and temporal evidence without claiming
            # production-grade biometric liveness.
            liveness_value = face_detected
            liveness_confidence = face_confidence if face_detected else 0.0

            decision = adaptive_security.evaluate(
                presence=face_detected,
                liveness=liveness_value,
                identity=identity_value,
                face_detected=face_detected,
                behavior=None,
                presence_confidence=face_confidence,
                liveness_confidence=liveness_confidence,
                identity_confidence=identity_confidence,
                face_confidence=face_confidence,
                behavior_confidence=1.0,
            )

            state = decision.state.value
            confidence = decision.confidence

            if state == "TRUSTED":
                status_text = "TRUSTED"
            elif state == "SUSPICIOUS":
                status_text = "SUSPICIOUS"
            elif state == "DENIED":
                status_text = "DENIED"
            elif state == "NO_PRESENCE":
                status_text = "NO PRESENCE"
            else:
                status_text = "VERIFYING"

            cv2.rectangle(
                frame,
                (10, 10),
                (width - 10, height - 10),
                (80, 180, 255),
                2,
            )

            if face_detected:
                x1, y1, x2, y2 = face.bbox

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2,
                )

            cv2.putText(
                frame,
                f"Security: {status_text}",
                (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Confidence: {confidence:.2f}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Face: {'YES' if face_detected else 'NO'}",
                (20, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Enrolled: {'YES' if enrolled else 'NO'}",
                (20, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            if identity_match is not None:
                cv2.putText(
                    frame,
                    f"Identity: {'MATCH' if identity_match.matched else 'NO MATCH'}",
                    (20, 185),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

            cv2.putText(
                frame,
                f"Trusted streak: {decision.consecutive_trusted}",
                (20, 220),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "E: Enroll | R: Reset | Q: Quit",
                (20, height - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("e"):
                if face_detected and face.landmarks:
                    if identity_manager.enroll(
                        "AUREX_USER",
                        face.landmarks,
                    ):
                        enrolled = True
                        enrollment_landmarks = face.landmarks

                        print()
                        print("FACE ENROLLMENT: PASS")
                        print("Identity: AUREX_USER")
                        print()
                    else:
                        print("FACE ENROLLMENT: FAILED")
                else:
                    print("No face detected. Enrollment skipped.")

            elif key == ord("r"):
                adaptive_security.reset()
                print("Adaptive security history reset.")

            elif key == ord("q"):
                break

            time.sleep(0.005)

    finally:
        camera.release()
        face_detector.close()
        cv2.destroyAllWindows()

        print()
        print("=" * 70)
        print("PHASE 24 LIVE TEST ENDED")
        print("=" * 70)


if __name__ == "__main__":
    main()