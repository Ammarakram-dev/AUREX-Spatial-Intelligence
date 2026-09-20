from __future__ import annotations

import time

import cv2

from vision.camera import AUREXCamera
from vision.human_detector import (
    AUREXHumanDetector,
)
from vision.person_tracker import (
    AUREXPersonTracker,
)

from core.intelligence.behavior.behavior_engine import (
    AUREXBehaviorEngine,
)


def draw_panel(
    frame,
    analysis,
):
    height, width = frame.shape[:2]

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (15, 15),
        (620, 235),
        (8, 8, 8),
        -1,
    )

    frame[:] = cv2.addWeighted(
        overlay,
        0.75,
        frame,
        0.25,
        0,
    )

    cv2.putText(
        frame,
        "AUREX BEHAVIORAL INTELLIGENCE",
        (35, 48),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.70,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"PEOPLE: {len(analysis.profiles)}",
        (35, 82),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"ANOMALIES: {len(analysis.anomalies)}",
        (35, 112),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"GLOBAL SCORE: "
        f"{analysis.global_anomaly_score:.2f}",
        (35, 142),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    if analysis.profiles:
        profile = analysis.profiles[0]

        text = (
            f"P{profile.person_id} | "
            f"{profile.recent_pattern.value} | "
            f"avg {profile.average_movement:.3f}"
        )

        cv2.putText(
            frame,
            text[:70],
            (35, 174),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (220, 220, 220),
            1,
            cv2.LINE_AA,
        )

    if analysis.anomalies:
        anomaly = analysis.anomalies[0]

        text = (
            f"ANOMALY: "
            f"{anomaly.pattern.value} | "
            f"{anomaly.severity.value}"
        )

        cv2.putText(
            frame,
            text[:70],
            (35, 204),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (0, 200, 255),
            1,
            cv2.LINE_AA,
        )

    cv2.putText(
        frame,
        "Q = quit | R = reset",
        (width - 250, height - 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )


def main():
    camera = AUREXCamera()

    detector = AUREXHumanDetector()

    tracker = AUREXPersonTracker()

    behavior = AUREXBehaviorEngine(
        history_limit=60,
        movement_threshold=0.05,
        rapid_movement_threshold=0.35,
        prolonged_stationary_frames=45,
    )

    if not camera.open():
        print(
            "ERROR: Camera could not be opened."
        )
        return

    print("=" * 70)
    print(
        "AUREX PHASE 30 - LIVE BEHAVIORAL INTELLIGENCE"
    )
    print("=" * 70)
    print("REAL CAMERA validation started.")
    print()
    print("Test movement naturally:")
    print("1. Stay still for several seconds.")
    print("2. Walk left/right.")
    print("3. Change direction repeatedly.")
    print("4. Move quickly across the camera view.")
    print("5. Stop and observe the behavior history.")
    print()
    print("Q = quit")
    print("R = reset behavioral history")
    print("=" * 70)

    try:
        while True:
            frame = camera.read()

            if frame is None:
                print(
                    "Camera frame unavailable."
                )
                break

            height, width = frame.shape[:2]

            detections = detector.detect(
                frame
            )

            tracked_people = tracker.update(
                detections,
                frame_width=width,
            )

            now = time.time()

            for person in tracked_people:
                direction = (
                    getattr(
                        person,
                        "movement_direction",
                        "",
                    )
                    or ""
                )

                movement = float(
                    getattr(
                        person,
                        "movement_distance",
                        0.0,
                    )
                    or 0.0
                )

                zone = (
                    getattr(
                        person,
                        "zone",
                        "",
                    )
                    or ""
                )

                behavior.observe(
                    person_id=str(
                        person.person_id
                    ),
                    movement_distance=movement,
                    movement_direction=direction,
                    zone=zone,
                    posture="unknown",
                    timestamp=now,
                )

            analysis = behavior.analyze()

            for person in tracked_people:
                center = getattr(
                    person,
                    "current_center",
                    None,
                )

                if center is None:
                    continue

                x, y = center

                cv2.circle(
                    frame,
                    (
                        int(x),
                        int(y),
                    ),
                    6,
                    (0, 255, 255),
                    -1,
                )

                cv2.putText(
                    frame,
                    f"P{person.person_id}",
                    (
                        int(x) + 10,
                        int(y) - 10,
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            draw_panel(
                frame,
                analysis,
            )

            cv2.imshow(
                "AUREX - Behavioral Intelligence",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("r"):
                behavior.reset()
                print(
                    "Behavior history reset."
                )

    finally:
        camera.release()

        try:
            detector.close()
        except Exception:
            pass

        cv2.destroyAllWindows()

        print("=" * 70)
        print(
            "AUREX PHASE 30 LIVE TEST ENDED"
        )
        print("=" * 70)


if __name__ == "__main__":
    main()