import cv2
import time
import math

from vision.camera import AUREXCamera
from identity.face_detector import AUREXFaceDetector
from identity.face_landmarks import AUREXFaceLandmarks
from identity.identity_manager import AUREXIdentityManager
from identity.eye_liveness import AUREXEyeLiveness
from identity.eye_lock import AUREXEyeLock


WINDOW_NAME = "AUREX Phase 26 - EyeLock"


def draw_glow_circle(
    frame,
    center,
    radius,
    intensity=1.0,
):
    """
    Draws a soft visual scan glow.
    This is a screen effect only.
    """

    overlay = frame.copy()

    x, y = center

    for offset in range(18, 0, -3):
        current_radius = radius + offset

        alpha = (
            intensity
            * (18 - offset)
            / 18.0
            * 0.08
        )

        cv2.circle(
            overlay,
            (x, y),
            current_radius,
            (255, 245, 210),
            2,
            cv2.LINE_AA,
        )

        frame[:] = cv2.addWeighted(
            overlay,
            alpha,
            frame,
            1.0 - alpha,
            0,
        )


def draw_retinal_scan(
    frame,
    landmarks,
    eye_state,
    frame_counter,
):
    """
    Futuristic retinal-scan visualization.

    The effect is rendered on the camera preview only.
    No physical light is emitted.
    """

    if not landmarks.detected:
        return

    if eye_state != "open":
        return

    if len(landmarks.landmarks) < 400:
        return

    points = landmarks.landmarks

    # MediaPipe eye landmark groups.
    left_eye_indices = [
        33,
        160,
        158,
        133,
        153,
        144,
    ]

    right_eye_indices = [
        362,
        385,
        387,
        263,
        373,
        380,
    ]

    height, width = frame.shape[:2]

    def eye_center(indices):

        coords = []

        for index in indices:
            x = int(points[index][0] * width)
            y = int(points[index][1] * height)

            coords.append((x, y))

        if not coords:
            return None

        center_x = int(
            sum(p[0] for p in coords) / len(coords)
        )

        center_y = int(
            sum(p[1] for p in coords) / len(coords)
        )

        return center_x, center_y

    left_center = eye_center(left_eye_indices)
    right_center = eye_center(right_eye_indices)

    if left_center is None or right_center is None:
        return

    # Animated scan pulse.
    pulse = (
        math.sin(frame_counter * 0.18) + 1.0
    ) / 2.0

    left_radius = int(
        11 + pulse * 5
    )

    right_radius = int(
        11 + pulse * 5
    )

    # Soft eye glow.
    draw_glow_circle(
        frame,
        left_center,
        left_radius,
        1.0,
    )

    draw_glow_circle(
        frame,
        right_center,
        right_radius,
        1.0,
    )

    # Retinal scan rings.
    overlay = frame.copy()

    cv2.circle(
        overlay,
        left_center,
        left_radius,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    cv2.circle(
        overlay,
        right_center,
        right_radius,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    # Inner scan points.
    cv2.circle(
        overlay,
        left_center,
        3,
        (255, 255, 255),
        -1,
        cv2.LINE_AA,
    )

    cv2.circle(
        overlay,
        right_center,
        3,
        (255, 255, 255),
        -1,
        cv2.LINE_AA,
    )

    # Animated scan sweep.
    sweep = int(
        (
            math.sin(frame_counter * 0.10) + 1
        )
        * 0.5
        * 12
    )

    cv2.line(
        overlay,
        (
            left_center[0] - 18,
            left_center[1] + sweep - 6,
        ),
        (
            left_center[0] + 18,
            left_center[1] + sweep - 6,
        ),
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    cv2.line(
        overlay,
        (
            right_center[0] - 18,
            right_center[1] + sweep - 6,
        ),
        (
            right_center[0] + 18,
            right_center[1] + sweep - 6,
        ),
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    # Small scanning brackets.
    bracket = 13

    for cx, cy in [
        left_center,
        right_center,
    ]:

        cv2.line(
            overlay,
            (cx - bracket, cy - bracket),
            (cx - bracket + 6, cy - bracket),
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        cv2.line(
            overlay,
            (cx - bracket, cy - bracket),
            (cx - bracket, cy - bracket + 6),
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        cv2.line(
            overlay,
            (cx + bracket, cy + bracket),
            (cx + bracket - 6, cy + bracket),
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        cv2.line(
            overlay,
            (cx + bracket, cy + bracket),
            (cx + bracket, cy + bracket - 6),
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    frame[:] = cv2.addWeighted(
        overlay,
        0.88,
        frame,
        0.12,
        0,
    )


def draw_scan_status(
    frame,
    landmarks,
    liveness,
):
    """
    Displays retinal scanning status.
    """

    if (
        landmarks.detected
        and landmarks.eye_state == "open"
    ):
        text = "RETINAL SCAN ACTIVE"

        cv2.putText(
            frame,
            text,
            (20, 370),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    elif liveness.blink_detected:

        cv2.putText(
            frame,
            "BLINK VERIFIED",
            (20, 370),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )


def main():

    camera = AUREXCamera()
    face_detector = AUREXFaceDetector()
    landmarks = AUREXFaceLandmarks()

    identity_manager = AUREXIdentityManager()

    eye_liveness = AUREXEyeLiveness(
        live_threshold=0.70,
        minimum_signals=2,
    )

    eye_lock = AUREXEyeLock()

    enrolled = False
    last_identity_match = None
    frame_counter = 0

    print("=" * 72)
    print("AUREX PHASE 26: REAL EYELOCK + RETINAL SCAN")
    print("=" * 72)
    print()
    print("Controls:")
    print("  E = enroll current face")
    print("  R = reset EyeLock")
    print("  Q = quit")
    print()
    print("Retinal scan:")
    print("  Activates automatically when real eye landmarks")
    print("  detect the eyes as OPEN.")
    print()
    print("IMPORTANT:")
    print("  This is a visual camera effect only.")
    print("  No physical light is emitted toward the eyes.")
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

            frame_counter += 1

            # ==================================================
            # FACE DETECTION
            # ==================================================

            face = face_detector.detect(frame)

            face_detected = bool(
                face.detected
            )

            face_confidence = (
                float(face.confidence)
                if face_detected
                else 0.0
            )

            # ==================================================
            # FACE LANDMARKS
            # ==================================================

            landmark_result = landmarks.process(
                frame
            )

            # ==================================================
            # IDENTITY
            # ==================================================

            identity_matched = False
            identity_confidence = 0.0

            if (
                face_detected
                and landmark_result.detected
                and landmark_result.landmarks
                and enrolled
            ):

                last_identity_match = (
                    identity_manager.match(
                        landmark_result.landmarks
                    )
                )

                identity_matched = bool(
                    last_identity_match.matched
                )

                identity_confidence = float(
                    last_identity_match.confidence
                )

            # ==================================================
            # REAL LIVENESS
            # ==================================================

            liveness = eye_liveness.update(
                eye_state=landmark_result.eye_state,
                head_movement=(
                    landmark_result.head_movement
                ),
                facial_motion=(
                    landmark_result.facial_motion
                ),
                confidence=(
                    landmark_result.confidence
                    if landmark_result.detected
                    else 0.0
                ),
            )

            # ==================================================
            # EYELOCK
            # ==================================================

            decision = eye_lock.evaluate(
                identity_matched=identity_matched,
                identity_confidence=identity_confidence,
                liveness=liveness,
            )

            # ==================================================
            # FACE BOX
            # ==================================================

            if face_detected:

                x1, y1, x2, y2 = face.bbox

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 255, 255),
                    2,
                )

            # ==================================================
            # RETINAL SCAN VISUAL
            # ==================================================

            draw_retinal_scan(
                frame,
                landmark_result,
                landmark_result.eye_state,
                frame_counter,
            )

            # ==================================================
            # TOP STATUS
            # ==================================================

            state_text = (
                decision.state.value.upper()
            )

            cv2.putText(
                frame,
                f"EyeLock: {state_text}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Confidence: {decision.confidence:.2f}",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # ==================================================
            # FACE / IDENTITY
            # ==================================================

            cv2.putText(
                frame,
                f"Face: {'YES' if face_detected else 'NO'}",
                (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Enrolled: {'YES' if enrolled else 'NO'}",
                (20, 125),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            identity_text = (
                "MATCH"
                if identity_matched
                else "NO MATCH"
            )

            cv2.putText(
                frame,
                f"Identity: {identity_text}",
                (20, 155),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # ==================================================
            # EYES
            # ==================================================

            cv2.putText(
                frame,
                f"Eyes: {landmark_result.eye_state.upper()}",
                (20, 185),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Eye Ratio: {landmark_result.eye_ratio:.3f}",
                (20, 215),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Blink: {'YES' if liveness.blink_detected else 'NO'}",
                (20, 245),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # ==================================================
            # MOVEMENT
            # ==================================================

            cv2.putText(
                frame,
                (
                    "Head Motion: "
                    f"{'YES' if liveness.head_movement_detected else 'NO'}"
                ),
                (20, 275),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                (
                    "Facial Motion: "
                    f"{'YES' if liveness.facial_motion_detected else 'NO'}"
                ),
                (20, 305),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # ==================================================
            # LIVENESS
            # ==================================================

            cv2.putText(
                frame,
                (
                    "Liveness: "
                    f"{'LIVE' if liveness.live else 'VERIFYING'}"
                ),
                (20, 335),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            draw_scan_status(
                frame,
                landmark_result,
                liveness,
            )

            # ==================================================
            # CONTROLS
            # ==================================================

            cv2.putText(
                frame,
                "E:Enroll  R:Reset  Q:Quit",
                (20, height - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # ==================================================
            # SHOW
            # ==================================================

            cv2.imshow(
                WINDOW_NAME,
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            # ==================================================
            # ENROLL
            # ==================================================

            if key == ord("e"):

                if (
                    face_detected
                    and landmark_result.detected
                    and landmark_result.landmarks
                ):

                    success = (
                        identity_manager.enroll(
                            "AUREX_USER",
                            landmark_result.landmarks,
                        )
                    )

                    if success:

                        enrolled = True

                        eye_liveness.reset()
                        eye_lock.reset()
                        landmarks.reset()

                        last_identity_match = None

                        print()
                        print(
                            "FACE ENROLLMENT: PASS"
                        )
                        print(
                            "Identity: AUREX_USER"
                        )
                        print(
                            "Real EyeLock signals reset."
                        )
                        print()

                    else:

                        print(
                            "FACE ENROLLMENT: FAILED"
                        )

                else:

                    print(
                        "No valid face landmarks detected."
                    )

            # ==================================================
            # RESET
            # ==================================================

            elif key == ord("r"):

                eye_liveness.reset()
                eye_lock.reset()
                landmarks.reset()

                last_identity_match = None

                print(
                    "EyeLock state reset."
                )

            # ==================================================
            # QUIT
            # ==================================================

            elif key == ord("q"):
                break

            time.sleep(0.003)

    finally:

        camera.release()
        face_detector.close()
        landmarks.close()

        cv2.destroyAllWindows()

        print()
        print("=" * 72)
        print(
            "PHASE 26 REAL EYELOCK TEST ENDED"
        )
        print("=" * 72)


if __name__ == "__main__":
    main()