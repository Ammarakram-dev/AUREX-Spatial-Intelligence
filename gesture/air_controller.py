"""
AUREX Spatial Intelligence
Live Air Gesture Controller
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from gesture.air_writer import AUREXAirWriter
from gesture.gesture_recognizer import (
    AUREXGestureRecognizer,
    GestureType,
)
from gesture.hand_tracker import AUREXHandTracker
from gesture.intent_mapper import (
    AUREXIntentMapper,
)
from vision.camera import AUREXCamera


class AUREXAirController:
    """
    Live bridge between hand movement,
    AirCanvas strokes, gesture recognition,
    and spatial intent.
    """

    def __init__(self) -> None:

        self.hand_tracker = (
            AUREXHandTracker()
        )

        self.writer = AUREXAirWriter()

        self.recognizer = (
            AUREXGestureRecognizer()
        )

        self.intent_mapper = (
            AUREXIntentMapper()
        )

        self.active_points: list[
            tuple[int, int]
        ] = []

        self.last_intent = "READY"

    def process_frame(
        self,
        frame,
    ):

        state = self.hand_tracker.process(
            frame
        )

        writing = (
            state.detected
            and state.index_extended
            and not state.pinch
        )

        point = None

        if state.index_tip is not None:
            point = state.index_tip.pixel

        previous_writing = bool(
            self.active_points
        )

        if writing and point is not None:

            self.active_points.append(
                point
            )

            self.writer.update(
                point=point,
                writing=True,
            )

        else:

            if previous_writing:

                self._finish_stroke()

            self.writer.update(
                point=None,
                writing=False,
            )

            self.active_points.clear()

        output = self.writer.draw(
            frame
        )

        output = self.hand_tracker.draw(
            output,
            state,
        )

        return output, state

    def _finish_stroke(self) -> None:

        if len(self.active_points) < 5:
            self.active_points.clear()
            return

        result = (
            self.recognizer.recognize(
                self.active_points
            )
        )

        intent = self.intent_mapper.map(
            result
        )

        self.last_intent = (
            f"{intent.name} → "
            f"{intent.action}"
        )

        if result.gesture == GestureType.ZIGZAG:

            self.writer.clear()

        self.active_points.clear()

    def clear(self) -> None:

        self.writer.clear()
        self.active_points.clear()
        self.last_intent = "CLEARED"

    def close(self) -> None:

        self.hand_tracker.close()
        cv2.destroyAllWindows()


def main():

    print("=" * 60)
    print("AUREX LIVE SPATIAL CONTROL")
    print("=" * 60)

    controller = (
        AUREXAirController()
    )

    try:

        with AUREXCamera(
            width=960,
            height=540,
        ) as camera:

            print()
            print("AUREX spatial control active.")
            print()
            print("INDEX FINGER  = write")
            print("PINCH          = stop stroke")
            print("ZIGZAG         = erase")
            print("C              = clear")
            print("Q              = quit")
            print()

            while True:

                frame = camera.read()

                if frame is None:
                    break

                output, state = (
                    controller.process_frame(
                        frame
                    )
                )

                hand_status = (
                    "HAND DETECTED"
                    if state.detected
                    else "SEARCHING FOR HAND"
                )

                cv2.putText(
                    output,
                    hand_status,
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    output,
                    (
                        "INTENT: "
                        + controller.last_intent
                    ),
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    output,
                    (
                        f"STROKES: "
                        f"{controller.writer.stroke_count}"
                    ),
                    (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.imshow(
                    "AUREX Live Spatial Control",
                    output,
                )

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                if key == ord("q"):
                    break

                if key == ord("c"):
                    controller.clear()

    finally:

        controller.close()

    print()
    print("=" * 60)
    print("AUREX LIVE SPATIAL CONTROL CLOSED")
    print("=" * 60)


if __name__ == "__main__":
    main()