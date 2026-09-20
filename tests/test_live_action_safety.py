import cv2
import time

from vision.camera import AUREXCamera
from identity.face_detector import AUREXFaceDetector
from identity.identity_manager import AUREXIdentityManager

from core.security import (
    AUREXAdaptiveSecurity,
    AUREXActionSafetyGate,
    SecurityState,
    SecurityLevel,
)

from core.actions.action import (
    ActionRequest,
    ActionRisk,
)


WINDOW_NAME = "AUREX Phase 25 - Security Action Gate"


def create_action(risk=ActionRisk.LOW):
    return ActionRequest(
        action_id="live-phase25-action",
        action_type="display",
        source_intent="observe",
        confidence=0.95,
        risk=risk,
        requires_confirmation=False,
        parameters={
            "message": "AUREX safety-gate validation"
        },
        reason="Phase 25 live integration test",
    )


def main():
    camera = AUREXCamera()
    face_detector = AUREXFaceDetector()
    identity_manager = AUREXIdentityManager()

    adaptive_security = AUREXAdaptiveSecurity()
    safety_gate = AUREXActionSafetyGate()

    enrolled = False
    last_identity_match = None

    print("=" * 70)
    print("AUREX PHASE 25: LIVE SECURITY + ACTION SAFETY GATE")
    print("=" * 70)
    print()
    print("Controls:")
    print("  E = enroll current face")
    print("  R = reset security")
    print("  L = evaluate LOW-risk action")
    print("  H = evaluate HIGH-risk action")
    print("  Q = quit")
    print()
    print("First enroll your face with E.")
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

            face_detected = bool(face.detected)
            face_confidence = (
                float(face.confidence)
                if face_detected
                else 0.0
            )

            identity_value = None
            identity_confidence = 0.0

            if face_detected and face.landmarks and enrolled:
                last_identity_match = identity_manager.match(
                    face.landmarks
                )

                identity_value = (
                    last_identity_match.matched
                )

                identity_confidence = (
                    float(last_identity_match.confidence)
                )

            # Real face presence is used as the current
            # liveness/presence signal for this integration.
            liveness_value = face_detected
            liveness_confidence = face_confidence

            security_decision = adaptive_security.evaluate(
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

            security_state = security_decision.state

            if security_state == SecurityState.TRUSTED:
                security_level = SecurityLevel.LOW
            elif security_state == SecurityState.SUSPICIOUS:
                security_level = SecurityLevel.HIGH
            elif security_state == SecurityState.DENIED:
                security_level = SecurityLevel.HIGH
            else:
                security_level = SecurityLevel.MEDIUM

            # Default action evaluation.
            action_request = create_action(ActionRisk.LOW)

            gate_result = safety_gate.evaluate(
                action_request=action_request,
                security_state=security_state,
                security_level=security_level,
                security_confidence=security_decision.confidence,
                authorized=security_decision.authorized,
            )

            state_text = security_state.value.upper()
            gate_text = gate_result.decision

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
                f"Security: {state_text}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.85,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Confidence: {security_decision.confidence:.2f}",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Face: {'YES' if face_detected else 'NO'}",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Enrolled: {'YES' if enrolled else 'NO'}",
                (20, 145),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            if last_identity_match is not None:
                identity_text = (
                    "MATCH"
                    if last_identity_match.matched
                    else "NO MATCH"
                )

                cv2.putText(
                    frame,
                    f"Identity: {identity_text}",
                    (20, 180),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2,
                )

            cv2.putText(
                frame,
                f"Trusted streak: "
                f"{security_decision.consecutive_trusted}",
                (20, 215),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Safety Gate: {gate_text}",
                (20, 250),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.70,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "E:Enroll  R:Reset  L:Low  H:High  Q:Quit",
                (20, height - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.58,
                (255, 255, 255),
                2,
            )

            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF

            # --------------------------------------------------
            # ENROLL
            # --------------------------------------------------

            if key == ord("e"):
                if face_detected and face.landmarks:
                    success = identity_manager.enroll(
                        "AUREX_USER",
                        face.landmarks,
                    )

                    if success:
                        enrolled = True
                        adaptive_security.reset()
                        safety_gate.reset()

                        print()
                        print("FACE ENROLLMENT: PASS")
                        print("Identity: AUREX_USER")
                        print("Security history reset.")
                        print()

                    else:
                        print("FACE ENROLLMENT: FAILED")

                else:
                    print("No face detected.")

            # --------------------------------------------------
            # RESET
            # --------------------------------------------------

            elif key == ord("r"):
                adaptive_security.reset()
                safety_gate.reset()
                last_identity_match = None

                print("Security and safety-gate history reset.")

            # --------------------------------------------------
            # LOW-RISK ACTION
            # --------------------------------------------------

            elif key == ord("l"):
                request = create_action(ActionRisk.LOW)

                result = safety_gate.evaluate(
                    action_request=request,
                    security_state=security_state,
                    security_level=security_level,
                    security_confidence=(
                        security_decision.confidence
                    ),
                    authorized=security_decision.authorized,
                )

                print()
                print("LOW-RISK ACTION")
                print(f"Security: {security_state.value}")
                print(f"Confidence: {security_decision.confidence:.2f}")
                print(f"Gate: {result.decision}")
                print(f"Allowed: {result.allowed}")
                print()

            # --------------------------------------------------
            # HIGH-RISK ACTION
            # --------------------------------------------------

            elif key == ord("h"):
                request = create_action(ActionRisk.HIGH)

                result = safety_gate.evaluate(
                    action_request=request,
                    security_state=security_state,
                    security_level=security_level,
                    security_confidence=(
                        security_decision.confidence
                    ),
                    authorized=security_decision.authorized,
                )

                print()
                print("HIGH-RISK ACTION")
                print(f"Security: {security_state.value}")
                print(f"Confidence: {security_decision.confidence:.2f}")
                print(f"Gate: {result.decision}")
                print(
                    f"Confirmation required: "
                    f"{result.requires_confirmation}"
                )
                print()

            elif key == ord("q"):
                break

            time.sleep(0.005)

    finally:
        camera.release()
        face_detector.close()
        cv2.destroyAllWindows()

        print()
        print("=" * 70)
        print("PHASE 25 LIVE TEST ENDED")
        print("=" * 70)


if __name__ == "__main__":
    main()