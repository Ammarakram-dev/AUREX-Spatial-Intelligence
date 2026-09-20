from __future__ import annotations

import cv2

from core.security.multi_person import (
    AUREXMultiPersonSecurity,
)
from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector
from vision.person_tracker import AUREXPersonTracker


def draw_panel(
    frame,
    people,
    assessment,
):
    height, width = frame.shape[:2]

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (10, 10),
        (width - 10, 185),
        (0, 0, 0),
        -1,
    )

    frame = cv2.addWeighted(
        overlay,
        0.55,
        frame,
        0.45,
        0,
    )

    lines = [
        f"PEOPLE: {len(people)}",
        f"STATE: {assessment.state.value.upper()}",
        f"LEVEL: {assessment.level.value.upper()}",
        f"CONFIDENCE: {assessment.confidence:.2f}",
        f"NEAR PAIRS: {len(assessment.nearby_pairs)}",
        f"APPROACH PAIRS: {len(assessment.approaching_pairs)}",
        f"SEPARATION PAIRS: {len(assessment.separating_pairs)}",
    ]

    for index, line in enumerate(lines):
        cv2.putText(
            frame,
            line,
            (25, 38 + index * 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    return frame


def find_person(
    people,
    person_id,
):
    for person in people:
        if str(person.person_id) == str(person_id):
            return person

    return None


def main():

    camera = AUREXCamera()
    detector = AUREXHumanDetector()
    tracker = AUREXPersonTracker()

    security = AUREXMultiPersonSecurity(
        proximity_threshold=0.30,
        high_density_threshold=4,
        stability_frames=3,
    )

    camera.open()

    print("=" * 70)
    print("AUREX PHASE 31 — LIVE MULTI-PERSON SECURITY")
    print("=" * 70)
    print("Real camera validation started.")
    print()
    print("Q = Quit")
    print("R = Reset temporal history")
    print("=" * 70)

    try:

        while True:

            frame = camera.read()

            if frame is None:
                continue

            detections = detector.detect(frame)

            tracked_people = tracker.update(
                detections,
                frame.shape[1],
            )

            assessment = security.analyze(
                tracked_people
            )

            # -------------------------------------------------
            # Draw tracked people
            # -------------------------------------------------

            for person in tracked_people:

                x1 = person.x1
                y1 = person.y1
                x2 = person.x2
                y2 = person.y2

                cv2.rectangle(
                    frame,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    (255, 255, 255),
                    2,
                )

                label = (
                    f"{person.person_id} "
                    f"{person.movement_direction}"
                )

                cv2.putText(
                    frame,
                    label,
                    (
                        int(x1),
                        max(
                            20,
                            int(y1) - 8,
                        ),
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                center_x = int(
                    person.current_center[0]
                )

                center_y = int(
                    person.current_center[1]
                )

                cv2.circle(
                    frame,
                    (center_x, center_y),
                    5,
                    (255, 255, 255),
                    -1,
                )

            # -------------------------------------------------
            # Draw proximity relationships
            # -------------------------------------------------

            for pair in assessment.nearby_pairs:

                source = find_person(
                    tracked_people,
                    pair["source_id"],
                )

                target = find_person(
                    tracked_people,
                    pair["target_id"],
                )

                if source is None or target is None:
                    continue

                p1 = (
                    int(source.current_center[0]),
                    int(source.current_center[1]),
                )

                p2 = (
                    int(target.current_center[0]),
                    int(target.current_center[1]),
                )

                cv2.line(
                    frame,
                    p1,
                    p2,
                    (255, 255, 255),
                    2,
                )

                midpoint = (
                    (p1[0] + p2[0]) // 2,
                    (p1[1] + p2[1]) // 2,
                )

                distance_text = (
                    f"{pair['distance']:.2f}"
                )

                cv2.putText(
                    frame,
                    distance_text,
                    midpoint,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            # -------------------------------------------------
            # Draw approach relationships
            # -------------------------------------------------

            for pair in assessment.approaching_pairs:

                source = find_person(
                    tracked_people,
                    pair["source_id"],
                )

                target = find_person(
                    tracked_people,
                    pair["target_id"],
                )

                if source is None or target is None:
                    continue

                p1 = (
                    int(source.current_center[0]),
                    int(source.current_center[1]),
                )

                p2 = (
                    int(target.current_center[0]),
                    int(target.current_center[1]),
                )

                cv2.arrowedLine(
                    frame,
                    p1,
                    p2,
                    (255, 255, 255),
                    3,
                    tipLength=0.15,
                )

            # -------------------------------------------------
            # Draw separation relationships
            # -------------------------------------------------

            for pair in assessment.separating_pairs:

                source = find_person(
                    tracked_people,
                    pair["source_id"],
                )

                target = find_person(
                    tracked_people,
                    pair["target_id"],
                )

                if source is None or target is None:
                    continue

                p1 = (
                    int(source.current_center[0]),
                    int(source.current_center[1]),
                )

                p2 = (
                    int(target.current_center[0]),
                    int(target.current_center[1]),
                )

                cv2.line(
                    frame,
                    p1,
                    p2,
                    (255, 255, 255),
                    1,
                )

            # -------------------------------------------------
            # Information panel
            # -------------------------------------------------

            frame = draw_panel(
                frame,
                tracked_people,
                assessment,
            )

            cv2.imshow(
                "AUREX - Phase 31 Multi-Person Security",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("r"):
                security.reset()
                print(
                    "Temporal security history reset."
                )

    finally:

        camera.release()
        cv2.destroyAllWindows()

    print()
    print("=" * 70)
    print("PHASE 31 LIVE VALIDATION COMPLETE")
    print("=" * 70)
    print(security.status())


if __name__ == "__main__":
    main()