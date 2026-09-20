import time

import cv2

from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector
from vision.person_tracker import AUREXPersonTracker
from vision.scene.object_detector import AUREXSceneObjectDetector
from vision.scene.scene_engine import AUREXSceneIntelligence

from core.spatial.relationship_engine import AUREXRelationshipEngine
from core.spatial.perception_bridge import AUREXSpatialBridge
from core.spatial.human_state import AUREXHumanSpatialFusion

from core.intelligence.behavior.behavior_engine import AUREXBehaviorEngine
from core.intelligence.hazard_engine import AUREXHazardEngine
from core.intelligence.environment import AUREXEnvironmentEngine


def main():
    camera = AUREXCamera()
    detector = AUREXHumanDetector()
    tracker = AUREXPersonTracker()

    scene_detector = AUREXSceneObjectDetector()
    scene_engine = AUREXSceneIntelligence()

    spatial_bridge = AUREXSpatialBridge()
    relationship_engine = AUREXRelationshipEngine()

    human_fusion = AUREXHumanSpatialFusion()

    behavior_engine = AUREXBehaviorEngine()
    hazard_engine = AUREXHazardEngine()

    environment_engine = AUREXEnvironmentEngine()

    if not camera.open():
        print("ERROR: Could not open camera.")
        return

    print("=" * 70)
    print("AUREX PHASE 34 - LIVE ENVIRONMENT INTELLIGENCE")
    print("=" * 70)
    print("REAL CAMERA: ACTIVE")
    print()
    print("Controls:")
    print("  R = Reset environment history")
    print("  Q = Quit")
    print("=" * 70)

    latest_environment = None
    latest_scene = None
    latest_hazards = []

    try:
        while True:
            frame = camera.read()

            if frame is None:
                print("Camera frame unavailable.")
                break

            frame_height, frame_width = frame.shape[:2]

            # ---------------------------------------------------------
            # 1. HUMAN DETECTION
            # ---------------------------------------------------------
            detections = detector.detect(frame)

            # ---------------------------------------------------------
            # 2. HUMAN TRACKING
            # ---------------------------------------------------------
            tracked_people = tracker.update(
                detections,
                frame_width=frame_width,
            )

            # ---------------------------------------------------------
            # 3. SPATIAL WORLD MODEL
            # ---------------------------------------------------------
            world = spatial_bridge.update_people(
                tracked_people,
                frame_width,
                frame_height,
            )

            # ---------------------------------------------------------
            # 4. PERSON-TO-PERSON RELATIONSHIPS
            # ---------------------------------------------------------
            relationships = relationship_engine.apply_to_world(world)

            # ---------------------------------------------------------
            # 5. HUMAN SPATIAL STATES
            # ---------------------------------------------------------
            human_states = []

            for person in tracked_people:
                entity = world.get_entity(person.person_id)

                if entity is None:
                    continue

                state = human_fusion.build(
                    tracked_person=person,
                    spatial_entity=entity,
                    posture_result=None,
                    pose_available=False,
                )

                human_states.append(state)

                behavior_engine.observe_state(state)

            # ---------------------------------------------------------
            # 6. BEHAVIOR INTELLIGENCE
            # ---------------------------------------------------------
            behavior_result = behavior_engine.analyze()

            # ---------------------------------------------------------
            # 7. SCENE / OBJECT INTELLIGENCE
            # ---------------------------------------------------------
            try:
                objects = scene_detector.detect(frame)

                latest_scene = scene_engine.analyze(
                    objects,
                    frame_width=frame_width,
                    frame_height=frame_height,
                )

                scene_detector.draw(frame, objects)

            except Exception:
                objects = []

            # ---------------------------------------------------------
            # 8. HAZARD INTELLIGENCE
            # ---------------------------------------------------------
            try:
                context_stub = None

                latest_hazards = hazard_engine.analyze(
                    human_states=human_states,
                    relationships=relationships,
                    context=context_stub,
                )

            except TypeError:
                try:
                    latest_hazards = hazard_engine.analyze(
                        human_states=human_states,
                        relationships=relationships,
                    )
                except Exception:
                    latest_hazards = []

            except Exception:
                latest_hazards = []

            # ---------------------------------------------------------
            # 9. ENVIRONMENT FUSION
            # ---------------------------------------------------------
            latest_environment = environment_engine.analyze(
                human_states=human_states,
                objects=objects,
                relationships=relationships,
                behavior=behavior_result,
                hazards=latest_hazards,
            )

            # ---------------------------------------------------------
            # 10. DRAW PEOPLE
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

                label = (
                    f"{person.person_id} "
                    f"{person.confidence:.2f}"
                )

                cv2.putText(
                    frame,
                    label,
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                )

            # ---------------------------------------------------------
            # 11. ENVIRONMENT UI
            # ---------------------------------------------------------
            state_text = latest_environment.state.value
            confidence_text = (
                f"{latest_environment.confidence:.2f}"
            )

            cv2.rectangle(
                frame,
                (10, 10),
                (470, 190),
                (15, 15, 15),
                -1,
            )

            cv2.putText(
                frame,
                "AUREX ENVIRONMENT INTELLIGENCE",
                (25, 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"STATE: {state_text.upper()}",
                (25, 68),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"CONFIDENCE: {confidence_text}",
                (25, 94),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"PEOPLE: {latest_environment.people_count}",
                (25, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"OBJECTS: {latest_environment.object_count}",
                (180, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"RELATIONSHIPS: {latest_environment.relationship_count}",
                (25, 146),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"HAZARDS: {latest_environment.hazard_count}",
                (250, 146),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "R RESET   Q QUIT",
                (25, 174),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (255, 255, 255),
                2,
            )

            # ---------------------------------------------------------
            # 12. DISPLAY
            # ---------------------------------------------------------
            cv2.imshow(
                "AUREX - Phase 34 Environment Intelligence",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("r"):
                environment_engine.reset()
                behavior_engine.reset()
                hazard_engine.reset()

                latest_environment = None
                latest_hazards = []

                print("Environment intelligence reset.")

            time.sleep(0.001)

    finally:
        camera.release()
        cv2.destroyAllWindows()

        print()
        print("=" * 70)
        print("AUREX PHASE 34 STOPPED")
        print("=" * 70)

        if latest_environment is not None:
            print(
                "Last environment state:",
                latest_environment.state.value,
            )
            print(
                "Last confidence:",
                round(latest_environment.confidence, 3),
            )
            print(
                "People:",
                latest_environment.people_count,
            )
            print(
                "Objects:",
                latest_environment.object_count,
            )
            print(
                "Relationships:",
                latest_environment.relationship_count,
            )
            print(
                "Hazards:",
                latest_environment.hazard_count,
            )


if __name__ == "__main__":
    main()