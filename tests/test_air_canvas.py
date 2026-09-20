import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from vision.camera import AUREXCamera
from gesture.hand_tracker import AUREXHandTracker
from gesture.air_writer import AUREXAirWriter


def main():

    print("=" * 60)
    print("AUREX AIRCANVAS TEST")
    print("=" * 60)

    tracker = AUREXHandTracker()

    writer = AUREXAirWriter()

    try:

        with AUREXCamera(
            width=960,
            height=540,
        ) as camera:

            print("Camera opened.")
            print()
            print("Raise one hand.")
            print("Extend your index finger.")
            print("Move it through the air to write.")
            print("Pinch thumb + index to stop writing.")
            print("Press C to clear.")
            print("Press Q to quit.")
            print()

            while True:

                frame = camera.read()

                if frame is None:
                    break

                state = tracker.process(
                    frame
                )

                writing = (
                    state.detected
                    and state.index_extended
                    and not state.pinch
                )

                if (
                    state.index_tip
                    is not None
                ):

                    point = (
                        state.index_tip.pixel
                    )

                else:

                    point = None

                writer.update(
                    point=point,
                    writing=writing,
                )

                output = writer.draw(
                    frame
                )

                output = tracker.draw(
                    output,
                    state,
                )

                status = (
                    "AIR WRITING"
                    if writing
                    else "READY"
                )

                cv2.putText(
                    output,
                    f"AUREX AIRCANVAS | {status}",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    output,
                    (
                        f"STROKES: "
                        f"{writer.stroke_count}"
                    ),
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.imshow(
                    "AUREX AirCanvas",
                    output,
                )

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                if key == ord("q"):
                    break

                if key == ord("c"):
                    writer.clear()

    finally:

        tracker.close()

        cv2.destroyAllWindows()

    print()
    print("=" * 60)
    print("AIRCANVAS TEST COMPLETED")
    print(
        f"Strokes created: "
        f"{writer.stroke_count}"
    )
    print(
        f"Points captured: "
        f"{writer.point_count}"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()