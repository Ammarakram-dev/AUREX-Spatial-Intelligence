from __future__ import annotations

import cv2

from vision.camera import AUREXCamera
from vision.scene.object_detector import (
    AUREXSceneObjectDetector,
)
from vision.scene.scene_engine import (
    AUREXSceneIntelligence,
)


def draw_scene_panel(
    frame,
    snapshot,
):
    height, width = frame.shape[:2]

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (15, 15),
        (530, 205),
        (8, 8, 8),
        -1,
    )

    frame[:] = cv2.addWeighted(
        overlay,
        0.72,
        frame,
        0.28,
        0,
    )

    cv2.putText(
        frame,
        "AUREX SCENE INTELLIGENCE",
        (35, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.70,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"OBJECTS: {snapshot.object_count}",
        (35, 78),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"RELATIONSHIPS: {len(snapshot.relationships)}",
        (35, 108),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"SCENE CONFIDENCE: {snapshot.scene_confidence:.2f}",
        (35, 138),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    classes = ", ".join(
        f"{name}:{count}"
        for name, count
        in snapshot.class_counts.items()
    )

    if len(classes) > 58:
        classes = classes[:58] + "..."

    cv2.putText(
        frame,
        f"VISIBLE: {classes or 'none'}",
        (35, 168),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (220, 220, 220),
        1,
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

    detector = AUREXSceneObjectDetector(
        model_name="yolo11n.pt",
        confidence_threshold=0.40,
    )

    scene_engine = AUREXSceneIntelligence()

    if not camera.open():
        print("ERROR: Camera could not be opened.")
        return

    print("=" * 70)
    print("AUREX PHASE 29 - LIVE SCENE & OBJECT INTELLIGENCE")
    print("=" * 70)
    print("Real camera validation started.")
    print("Place several visible objects in front of the camera.")
    print("Move objects in and out of the scene to test scene changes.")
    print("Q = quit")
    print("R = reset")
    print("=" * 70)

    try:
        while True:
            frame = camera.read()

            if frame is None:
                print("Camera frame unavailable.")
                break

            height, width = frame.shape[:2]

            objects = detector.detect(
                frame
            )

            snapshot = scene_engine.analyze(
                objects,
                width,
                height,
            )

            detector.draw(
                frame,
                objects,
            )

            draw_scene_panel(
                frame,
                snapshot,
            )

            cv2.imshow(
                "AUREX - Advanced Scene Intelligence",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("r"):
                scene_engine.reset()
                print(
                    "Scene intelligence history reset."
                )

    finally:
        camera.release()

        try:
            detector.close()
        except Exception:
            pass

        cv2.destroyAllWindows()

        print("=" * 70)
        print("AUREX PHASE 29 LIVE TEST ENDED")
        print("=" * 70)


if __name__ == "__main__":
    main()