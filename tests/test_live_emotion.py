from __future__ import annotations

import cv2

from vision.camera import AUREXCamera
from identity.face_landmarks import AUREXFaceLandmarks
from identity.emotion_engine import AUREXEmotionEngine


def draw_panel(
    frame,
    emotion,
    confidence,
    stability,
    face_detected,
):
    height, width = frame.shape[:2]

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (20, 20),
        (500, 190),
        (10, 10, 10),
        -1,
    )

    frame[:] = cv2.addWeighted(
        overlay,
        0.70,
        frame,
        0.30,
        0,
    )

    status = (
        "FACE: DETECTED"
        if face_detected
        else "FACE: SEARCHING"
    )

    cv2.putText(
        frame,
        status,
        (40, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 255, 0) if face_detected else (0, 180, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"AFFECT: {emotion.upper()}",
        (40, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.85,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"CONFIDENCE: {confidence:.2f}",
        (40, 130),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"STABILITY: {stability:.2f}",
        (40, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        "Q = quit | R = reset",
        (width - 250, height - 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )


def main():
    camera = AUREXCamera()
    landmarks = AUREXFaceLandmarks()
    emotion_engine = AUREXEmotionEngine()

    if not camera.open():
        print("ERROR: Camera could not be opened.")
        return

    print("=" * 70)
    print("AUREX PHASE 28 - LIVE EMOTION & AFFECTIVE STATE")
    print("=" * 70)
    print("Real camera validation started.")
    print("Show your face clearly to the camera.")
    print("Try natural expressions.")
    print("Q = quit")
    print("R = reset temporal history")
    print("=" * 70)

    try:
        while True:
            frame = camera.read()

            if frame is None:
                print("Camera frame unavailable.")
                break

            result = landmarks.process(frame)

            if result is not None and result.detected:
                decision = emotion_engine.analyze(
                    landmarks=result.landmarks,
                    face_detected=True,
                )

                if result.landmarks:
                    points = result.landmarks

                    for index in (
                        33,
                        133,
                        362,
                        263,
                        61,
                        291,
                        13,
                        14,
                    ):
                        if index < len(points):
                            point = points[index]

                            try:
                                x = int(point[0] * frame.shape[1])
                                y = int(point[1] * frame.shape[0])
                            except (TypeError, IndexError):
                                x = int(point.x * frame.shape[1])
                                y = int(point.y * frame.shape[0])

                            cv2.circle(
                                frame,
                                (x, y),
                                2,
                                (0, 255, 255),
                                -1,
                            )
            else:
                decision = emotion_engine.analyze(
                    face_detected=False
                )

            draw_panel(
                frame,
                decision.emotion.value,
                decision.confidence,
                decision.stability,
                decision.face_detected,
            )

            cv2.imshow(
                "AUREX - Emotion & Affective Intelligence",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("r"):
                emotion_engine.reset()
                print("Emotion temporal history reset.")

    finally:
        camera.release()

        try:
            landmarks.close()
        except AttributeError:
            pass

        cv2.destroyAllWindows()

        print("=" * 70)
        print("AUREX PHASE 28 LIVE TEST ENDED")
        print("=" * 70)


if __name__ == "__main__":
    main()