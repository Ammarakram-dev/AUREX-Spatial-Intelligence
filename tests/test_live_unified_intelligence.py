import time

import cv2

from vision.camera import AUREXCamera
from core.intelligence.situation import AUREXUnifiedIntelligence


def main():
    print("=" * 70)
    print("AUREX STEP 1 — LIVE UNIFIED INTELLIGENCE")
    print("=" * 70)
    print()
    print("Starting real camera...")
    print("This test validates the unified intelligence layer with")
    print("real-time camera activity.")
    print()
    print("Controls:")
    print("  R = Reset")
    print("  Q = Quit")
    print()

    camera = AUREXCamera()
    intelligence = AUREXUnifiedIntelligence()

    if not camera.open():
        print("ERROR: Could not open camera.")
        return

    previous_gray = None
    last_update = 0.0
    state = None

    try:
        while True:
            frame = camera.read()

            if frame is None:
                print("Camera frame unavailable.")
                break

            height, width = frame.shape[:2]

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (320, 240))

            activity = 0.0

            if previous_gray is not None:
                difference = cv2.absdiff(
                    previous_gray,
                    gray,
                )

                activity = float(difference.mean()) / 255.0

            previous_gray = gray

            now = time.time()

            if now - last_update >= 0.20:

                if activity >= 0.08:
                    human_states = [
                        {
                            "person_id": "camera_activity",
                            "movement_distance": min(
                                1.0,
                                activity * 2.0,
                            ),
                            "movement_direction": "movement",
                            "zone": "camera",
                        }
                    ]
                else:
                    human_states = []

                state = intelligence.update(
                    human_states=human_states,
                    scene={
                        "object_count": 0,
                    },
                    security={
                        "state": "unknown",
                        "level": "unknown",
                        "confidence": 0.0,
                    },
                )

                last_update = now

            display = frame.copy()

            cv2.rectangle(
                display,
                (15, 15),
                (width - 15, 205),
                (10, 10, 10),
                -1,
            )

            if state is not None:
                situation = state.situation.value.upper()
                activity_level = state.activity_level.value.upper()
                priority = state.priority.value.upper()

                lines = [
                    f"AUREX SITUATION: {situation}",
                    f"ACTIVITY: {activity_level}",
                    f"PRIORITY: {priority}",
                    f"PEOPLE/SIGNALS: {state.people_count}",
                    f"CONFIDENCE: {state.confidence:.2f}",
                    f"MODE: {state.recommended_mode.upper()}",
                ]

                y = 48

                for line in lines:
                    cv2.putText(
                        display,
                        line,
                        (30, y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

                    y += 27

            cv2.putText(
                display,
                "R = RESET    Q = QUIT",
                (30, height - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "AUREX - Unified Intelligence",
                display,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("r"):
                intelligence.reset()
                state = None
                print("Unified intelligence reset.")

            elif key == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

    print()
    print("=" * 70)
    print("LIVE UNIFIED INTELLIGENCE TEST FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()