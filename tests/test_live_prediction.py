import time
import cv2

from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector
from vision.person_tracker import AUREXPersonTracker

from core.spatial.perception_bridge import AUREXSpatialBridge
from core.spatial.relationship_engine import AUREXRelationshipEngine
from core.spatial.human_state import AUREXHumanSpatialFusion
from core.spatial.memory import AUREXTemporalMemory

from core.intelligence.environment import (
    AUREXEnvironmentEngine,
)

from core.intelligence.behavior.behavior_engine import (
    AUREXBehaviorEngine,
)

from core.intelligence.hazard_engine import (
    AUREXHazardEngine,
)

from core.intelligence.prediction import (
    AUREXPredictiveEngine,
)


def main():
    camera = AUREXCamera()
    detector = AUREXHumanDetector()
    tracker = AUREXPersonTracker()

    spatial_bridge = AUREXSpatialBridge()
    relationship_engine = AUREXRelationshipEngine()
    human_fusion = AUREXHumanSpatialFusion()

    behavior_engine = AUREXBehaviorEngine()
    hazard_engine = AUREXHazardEngine()

    environment_engine = AUREXEnvironmentEngine()
    temporal_memory = AUREXTemporalMemory()

    prediction_engine = AUREXPredictiveEngine()

    if not camera.open():
        print("ERROR: Could not open camera.")
        return

    print("=" * 72)
    print("AUREX PHASE 36 - LIVE PREDICTIVE TEMPORAL REASONING")
    print("=" * 72)
    print("REAL CAMERA: ACTIVE")
    print()
    print("AUREX is analyzing temporal patterns from live perception.")
    print()
    print("Controls:")
    print("  R = Reset temporal + prediction memory")
    print("  Q = Quit")
    print("=" * 72)

    try:
        while True:
            frame = camera.read()

            if frame is None:
                break

            frame_height, frame_width = frame.shape[:2]

            # ---------------------------------------------------------
            # HUMAN PERCEPTION
            # ---------------------------------------------------------
            detections = detector.detect(frame)

            tracked_people = tracker.update(
                detections,
                frame_width=frame_width,
            )

            # ---------------------------------------------------------
            # SPATIAL WORLD
            # ---------------------------------------------------------
            world = spatial_bridge.update_people(
                tracked_people,
                frame_width,
                frame_height,
            )

            relationships = relationship_engine.apply_to_world(
                world
            )

            # ---------------------------------------------------------
            # HUMAN STATES
            # ---------------------------------------------------------
            human_states = []

            for person in tracked_people:
                entity = world.get_entity(
                    person.person_id
                )

                if entity is None:
                    continue

                human_state = human_fusion.build(
                    tracked_person=person,
                    spatial_entity=entity,
                    posture_result=None,
                    pose_available=False,
                )

                human_states.append(
                    human_state
                )

                behavior_engine.observe_state(
                    human_state
                )

            # ---------------------------------------------------------
            # BEHAVIOR
            # ---------------------------------------------------------
            behavior_result = behavior_engine.analyze()

            # ---------------------------------------------------------
            # HAZARD
            # ---------------------------------------------------------
            try:
                hazards = hazard_engine.analyze(
                    human_states=human_states,
                    relationships=relationships,
                )
            except Exception:
                hazards = []

            # ---------------------------------------------------------
            # ENVIRONMENT
            # ---------------------------------------------------------
            environment = environment_engine.analyze(
                human_states=human_states,
                relationships=relationships,
                behavior=behavior_result,
                hazards=hazards,
            )

            # ---------------------------------------------------------
            # TEMPORAL MEMORY
            # ---------------------------------------------------------
            temporal_memory.observe(
                human_states=human_states,
                environment=environment,
                hazards=hazards,
                behavior=behavior_result,
                timestamp=time.time(),
            )

            # ---------------------------------------------------------
            # PREDICTION
            # ---------------------------------------------------------
            predictions = prediction_engine.analyze(
                temporal_memory
            )

            highest = (
                prediction_engine.highest_risk()
            )

            # ---------------------------------------------------------
            # DRAW PEOPLE
            # ---------------------------------------------------------
            for person in tracked_people:
                x1 = int(person.x1)
                y1 = int(person.y1)
                x2 = int(person.x2)
                y2 = int(person.y2)

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    str(person.person_id),
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                )

            # ---------------------------------------------------------
            # PREDICTION UI
            # ---------------------------------------------------------
            cv2.rectangle(
                frame,
                (10, 10),
                (650, 235),
                (15, 15, 15),
                -1,
            )

            cv2.putText(
                frame,
                "AUREX PREDICTIVE INTELLIGENCE",
                (25, 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"ENVIRONMENT: {environment.state.value}",
                (25, 68),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"MEMORY FRAMES: {temporal_memory.frame_index}",
                (25, 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"PREDICTIONS: {len(predictions)}",
                (25, 122),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"LEVEL: {highest.level.value}",
                (25, 149),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"TYPE: {highest.prediction_type.value}",
                (25, 176),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"CONFIDENCE: {highest.confidence:.2f}",
                (25, 203),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "R RESET   Q QUIT",
                (25, 225),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                2,
            )

            cv2.imshow(
                "AUREX - Phase 36 Predictive Intelligence",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("r"):
                temporal_memory.reset()
                prediction_engine.reset()
                environment_engine.reset()
                behavior_engine.reset()
                hazard_engine.reset()

                print("Predictive temporal system reset.")

            time.sleep(0.001)

    finally:
        camera.release()
        cv2.destroyAllWindows()

        print()
        print("=" * 72)
        print("AUREX PHASE 36 STOPPED")
        print("=" * 72)

        highest = prediction_engine.highest_risk()

        print(
            "Frames analyzed:",
            temporal_memory.frame_index,
        )

        print(
            "Predictions generated:",
            len(prediction_engine.assessments),
        )

        print(
            "Highest prediction:",
            highest.prediction_type.value,
        )

        print(
            "Prediction level:",
            highest.level.value,
        )

        print(
            "Prediction confidence:",
            round(highest.confidence, 3),
        )


if __name__ == "__main__":
    main()