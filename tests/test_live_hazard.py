import cv2
import time

from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector
from vision.person_tracker import AUREXPersonTracker
from vision.pose_estimator import AUREXPoseEstimator
from vision.posture_analyzer import AUREXPostureAnalyzer

from core.spatial.perception_bridge import (
    AUREXSpatialBridge,
)

from core.spatial.human_state import (
    AUREXHumanSpatialFusion,
)

from core.spatial.relationship_engine import (
    AUREXRelationshipEngine,
)

from core.intelligence.context_engine import (
    AUREXContextEngine,
)

from core.intelligence.hazard_engine import (
    AUREXHazardEngine,
)


WINDOW_NAME = "AUREX Phase 27 - Predictive Hazard Engine"


def main():

    camera = AUREXCamera()
    detector = AUREXHumanDetector()
    tracker = AUREXPersonTracker()
    pose_estimator = AUREXPoseEstimator()
    posture_analyzer = AUREXPostureAnalyzer()

    spatial_bridge = AUREXSpatialBridge()
    fusion = AUREXHumanSpatialFusion()
    relationship_engine = AUREXRelationshipEngine()
    context_engine = AUREXContextEngine()
    hazard_engine = AUREXHazardEngine()

    print("=" * 72)
    print("AUREX PHASE 27: LIVE PREDICTIVE HAZARD ENGINE")
    print("=" * 72)
    print()
    print("Controls:")
    print("  R = reset hazard history")
    print("  Q = quit")
    print()
    print("Monitoring:")
    print("  Human presence")
    print("  Movement")
    print("  Posture")
    print("  Spatial relationships")
    print("  Context")
    print("  Potential hazards")
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

            # ==================================================
            # HUMAN DETECTION
            # ==================================================

            detections = detector.detect(frame)

            # ==================================================
            # TRACKING
            # ==================================================

            tracked_people = tracker.update(
                detections,
                width,
            )

            # ==================================================
            # SPATIAL WORLD
            # ==================================================

            world = spatial_bridge.update_people(
                tracked_people,
                width,
                height,
            )

            # ==================================================
            # POSE
            # ==================================================

            pose_result = pose_estimator.process(
                frame
            )

            # ==================================================
            # HUMAN SPATIAL STATES
            # ==================================================

            human_states = []

            for person in tracked_people:

                person_id = str(
                    person.person_id
                )

                spatial_entity = world.get_entity(
                    person_id
                )

                if spatial_entity is None:
                    continue

                posture_result = None

                if pose_result is not None:

                    try:
                        posture_result = (
                            posture_analyzer.analyze(
                                pose_result
                            )
                        )

                    except (
                        AttributeError,
                        TypeError,
                    ):
                        posture_result = None

                state = fusion.build(
                    tracked_person=person,
                    spatial_entity=spatial_entity,
                    posture_result=posture_result,
                    pose_available=(
                        pose_result is not None
                    ),
                )

                human_states.append(state)

            # ==================================================
            # RELATIONSHIPS
            # ==================================================

            relationships = (
                relationship_engine.analyze_world(
                    world
                )
            )

            # ==================================================
            # CONTEXT
            # ==================================================

            context = context_engine.analyze(
                human_states=human_states,
                relationships=relationships,
            )

            # ==================================================
            # HAZARD INTELLIGENCE
            # ==================================================

            hazards = hazard_engine.analyze(
                human_states=human_states,
                relationships=relationships,
                context=context,
            )

            highest = hazard_engine.highest_risk(
                hazards
            )

            # ==================================================
            # DRAW TRACKED PEOPLE
            # ==================================================

            for person in tracked_people:

                cx, cy = person.current_center

                cv2.circle(
                    frame,
                    (int(cx), int(cy)),
                    5,
                    (255, 255, 255),
                    -1,
                )

                cv2.putText(
                    frame,
                    f"ID {person.person_id}",
                    (
                        int(cx) - 30,
                        int(cy) - 12,
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

            # ==================================================
            # HAZARD DISPLAY
            # ==================================================

            if highest is not None:

                hazard_text = (
                    highest.hazard_type.value.upper()
                )

                severity_text = (
                    highest.severity.value.upper()
                )

                confidence_text = (
                    f"{highest.confidence:.2f}"
                )

                cv2.putText(
                    frame,
                    f"HAZARD: {hazard_text}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.70,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    frame,
                    f"Severity: {severity_text}",
                    (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.60,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    frame,
                    f"Confidence: {confidence_text}",
                    (20, 105),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.60,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    frame,
                    f"Response: {highest.response.value}",
                    (20, 135),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            else:

                cv2.putText(
                    frame,
                    "HAZARD: NONE",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.70,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    frame,
                    "Environment monitoring normal",
                    (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            # ==================================================
            # SCENE INFORMATION
            # ==================================================

            cv2.putText(
                frame,
                f"People: {len(human_states)}",
                (20, 165),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Context: {context.context_type.value}",
                (20, 195),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                "R:Reset  Q:Quit",
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

            if key == ord("r"):

                hazard_engine.reset()

                print(
                    "Hazard engine reset."
                )

            elif key == ord("q"):

                break

            time.sleep(0.003)

    finally:

        camera.release()

        try:
            pose_estimator.close()
        except AttributeError:
            pass

        try:
            detector.close()
        except AttributeError:
            pass

        try:
            spatial_bridge.close()
        except AttributeError:
            pass

        cv2.destroyAllWindows()

        print()
        print("=" * 72)
        print("PHASE 27 LIVE HAZARD TEST ENDED")
        print("=" * 72)


if __name__ == "__main__":
    main()