from __future__ import annotations

import cv2

from core.spatial.overlay import (
    AUREXRealityOverlay,
    OverlayType,
)
from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector
from vision.person_tracker import AUREXPersonTracker
from vision.scene.object_detector import (
    AUREXSceneObjectDetector,
)


def draw_overlay(
    frame,
    overlay,
):

    x = int(overlay.anchor.x)
    y = int(overlay.anchor.y)

    confidence = overlay.confidence

    label = (
        f"{overlay.label} "
        f"{confidence:.2f}"
    )

    # Person/object bounding box
    if (
        overlay.anchor.width > 0
        and overlay.anchor.height > 0
    ):

        x2 = int(
            x + overlay.anchor.width
        )

        y2 = int(
            y + overlay.anchor.height
        )

        cv2.rectangle(
            frame,
            (x, y),
            (x2, y2),
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            label,
            (
                x,
                max(
                    20,
                    y - 8,
                ),
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    else:

        text_size = cv2.getTextSize(
            label,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            2,
        )[0]

        tx = max(
            5,
            min(
                x,
                frame.shape[1]
                - text_size[0]
                - 10,
            ),
        )

        ty = max(
            25,
            min(
                y,
                frame.shape[0]
                - 10,
            ),
        )

        cv2.rectangle(
            frame,
            (
                tx - 6,
                ty - 22,
            ),
            (
                tx + text_size[0] + 6,
                ty + 7,
            ),
            (0, 0, 0),
            -1,
        )

        cv2.putText(
            frame,
            label,
            (tx, ty),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )


def main():

    camera = AUREXCamera()
    human_detector = AUREXHumanDetector()
    tracker = AUREXPersonTracker()

    object_detector = (
        AUREXSceneObjectDetector()
    )

    overlay_engine = (
        AUREXRealityOverlay()
    )

    camera.open()

    print("=" * 70)
    print("AUREX PHASE 32 — REALITY OVERLAY INTELLIGENCE")
    print("=" * 70)
    print("REAL CAMERA VALIDATION")
    print()
    print("Q = Quit")
    print("R = Reset overlay history")
    print("=" * 70)

    try:

        while True:

            frame = camera.read()

            if frame is None:
                continue

            height, width = frame.shape[:2]

            # ---------------------------------------------
            # Human perception
            # ---------------------------------------------

            detections = human_detector.detect(
                frame
            )

            tracked_people = tracker.update(
                detections,
                width,
            )

            # ---------------------------------------------
            # Scene/object perception
            # ---------------------------------------------

            scene_objects = (
                object_detector.detect(frame)
            )

            # ---------------------------------------------
            # Build reality overlays
            # ---------------------------------------------

            overlays = overlay_engine.build(
                people=tracked_people,
                objects=scene_objects,
                relationships=[],
                context=None,
                hazards=[],
                frame_width=width,
                frame_height=height,
            )

            # ---------------------------------------------
            # Draw overlays
            # ---------------------------------------------

            for overlay in overlays:

                draw_overlay(
                    frame,
                    overlay,
                )

            # ---------------------------------------------
            # Header
            # ---------------------------------------------

            cv2.rectangle(
                frame,
                (10, 10),
                (420, 58),
                (0, 0, 0),
                -1,
            )

            cv2.putText(
                frame,
                "AUREX REALITY OVERLAY",
                (25, 42),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.72,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # ---------------------------------------------
            # Status
            # ---------------------------------------------

            status_text = (
                f"PEOPLE: {len(tracked_people)}  "
                f"OBJECTS: {len(scene_objects)}  "
                f"OVERLAYS: {len(overlays)}"
            )

            cv2.putText(
                frame,
                status_text,
                (20, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "AUREX - Phase 32 Reality Overlay",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("r"):
                overlay_engine.reset()

                print(
                    "Reality overlay history reset."
                )

    finally:

        camera.release()
        cv2.destroyAllWindows()

    print()
    print("=" * 70)
    print("PHASE 32 LIVE VALIDATION COMPLETE")
    print("=" * 70)
    print(overlay_engine.status())


if __name__ == "__main__":
    main()