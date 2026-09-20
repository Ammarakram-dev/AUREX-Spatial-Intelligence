"""
AUREX Spatial Intelligence
Live Human Spatial State Integration
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from core.spatial.human_state import AUREXHumanSpatialFusion
from core.spatial.perception_bridge import AUREXSpatialBridge
from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector
from vision.person_tracker import AUREXPersonTracker
from vision.pose_estimator import AUREXPoseEstimator
from vision.posture_analyzer import AUREXPostureAnalyzer


def main() -> None:
    camera = AUREXCamera(
        camera_index=0,
        width=1280,
        height=720,
    )

    detector = AUREXHumanDetector()

    tracker = AUREXPersonTracker()

    pose_estimator = AUREXPoseEstimator()

    posture_analyzer = AUREXPostureAnalyzer()

    spatial_bridge = AUREXSpatialBridge()

    fusion = AUREXHumanSpatialFusion()

    if not camera.open():
        print("Unable to open AUREX camera.")
        return

    print("=" * 70)
    print("AUREX — LIVE HUMAN SPATIAL STATE")
    print("=" * 70)
    print("Q = Quit")
    print("=" * 70)

    states = []

    try:
        while True:
            frame = camera.read()

            if frame is None:
                print("Unable to read camera frame.")
                break

            detections = detector.detect(frame)

            tracked_people = tracker.update(
    detections,
    frame_width=frame.shape[1],
)

            pose = pose_estimator.process(frame)

            posture = None

            if pose is not None:
                posture = posture_analyzer.analyze(pose)

            spatial_entities = spatial_bridge.update_people(
    tracked_people,
    frame_width=frame.shape[1],
    frame_height=frame.shape[0],
)

            states = []

            for person in tracked_people:
                entity_id = f"person_{person.person_id:03d}"

                spatial_entity = spatial_entities.get(entity_id)

                if spatial_entity is None:
                    continue

                state = fusion.build(
                    tracked_person=person,
                    spatial_entity=spatial_entity,
                    posture_result=posture,
                    pose_available=pose is not None,
                )

                states.append(state)

                x1, y1, x2, y2 = person.bbox

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 255, 255),
                    2,
                )

                label = (
                    f"ID {state.person_id} | "
                    f"{state.posture} | "
                    f"{state.movement_direction}"
                )

                cv2.putText(
                    frame,
                    label,
                    (x1, max(25, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                position = state.position

                spatial_text = (
                    f"XYZ: "
                    f"{position.x:.2f}, "
                    f"{position.y:.2f}, "
                    f"{position.z:.2f}"
                )

                cv2.putText(
                    frame,
                    spatial_text,
                    (x1, y2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

                zone_text = (
                    f"Zone: {state.zone} | "
                    f"Move: {state.movement_distance:.1f}"
                )

                cv2.putText(
                    frame,
                    zone_text,
                    (x1, y2 + 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

            cv2.rectangle(
                frame,
                (10, 10),
                (470, 105),
                (0, 0, 0),
                -1,
            )

            cv2.putText(
                frame,
                "AUREX HUMAN SPATIAL STATE",
                (25, 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.70,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Humans: {len(states)}",
                (25, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            pose_status = "AVAILABLE" if pose is not None else "WAITING"

            cv2.putText(
                frame,
                f"Pose: {pose_status}",
                (25, 88),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "AUREX - Human Spatial State",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

    print()
    print("Live Human Spatial State stopped.")
    print(f"Final tracked states: {len(states)}")


if __name__ == "__main__":
    main()