import cv2
import time

from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector
from vision.person_tracker import AUREXPersonTracker

from core.spatial.perception_bridge import AUREXSpatialBridge
from core.spatial.relationship_engine import AUREXRelationshipEngine
from core.spatial.human_state import AUREXHumanSpatialFusion

from core.intelligence.environment import AUREXEnvironmentEngine
from core.intelligence.behavior.behavior_engine import AUREXBehaviorEngine
from core.intelligence.hazard_engine import AUREXHazardEngine

from core.spatial.memory import (
    AUREXTemporalMemory,
    MemoryEventType,
)


def main():
    camera = AUREXCamera()
    detector = AUREXHumanDetector()
    tracker = AUREXPersonTracker()

    spatial_bridge = AUREXSpatialBridge()
    relationship_engine = AUREXRelationshipEngine()
    human_fusion = AUREXHumanSpatialFusion()

    environment_engine = AUREXEnvironmentEngine()
    behavior_engine = AUREXBehaviorEngine()
    hazard_engine = AUREXHazardEngine()

    temporal_memory = AUREXTemporalMemory(
        history_limit=120,
        event_limit=240,
    )

    if not camera.open():
        print("ERROR: Could not open camera.")
        return

    print("=" * 72)
    print("AUREX PHASE 35 - LIVE TEMPORAL WORLD MEMORY")
    print("=" * 72)
    print("REAL CAMERA: ACTIVE")
    print()
    print("The system now remembers changes between observations.")
    print()
    print("Controls:")
    print("  R = Reset temporal memory")
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

            relationships = relationship_engine.apply_to_world(world)

            # ---------------------------------------------------------
            # HUMAN SPATIAL STATES
            # ---------------------------------------------------------
            human_states = []

            for person in tracked_people:
                entity = world.get_entity(person.person_id)

                if entity is None:
                    continue

                human_state = human_fusion.build(
                    tracked_person=person,
                    spatial_entity=entity,
                    posture_result=None,
                    pose_available=False,
                )

                human_states.append(human_state)

                behavior_engine.observe_state(human_state)

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
            memory_state = temporal_memory.observe(
                human_states=human_states,
                environment=environment,
                security=None,
                hazards=hazards,
                behavior=behavior_result,
                timestamp=time.time(),
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
            # MEMORY EVENT
            # ---------------------------------------------------------
            recent_events = temporal_memory.recent_events(3)

            if recent_events:
                latest_event = recent_events[-1]

                event_text = (
                    f"EVENT: {latest_event.event_type.value}"
                )
            else:
                event_text = "EVENT: none"

            # ---------------------------------------------------------
            # UI
            # ---------------------------------------------------------
            cv2.rectangle(
                frame,
                (10, 10),
                (590, 215),
                (15, 15, 15),
                -1,
            )

            cv2.putText(
                frame,
                "AUREX TEMPORAL WORLD MEMORY",
                (25, 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"FRAME: {memory_state.frame_index}",
                (25, 68),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"PEOPLE: {len(memory_state.people_ids)}",
                (25, 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"ENVIRONMENT: {memory_state.environment_state}",
                (25, 122),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"HAZARDS: {memory_state.hazard_count}",
                (25, 149),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"EVENTS: {len(temporal_memory.events)}",
                (220, 149),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                event_text[:55],
                (25, 176),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "R RESET   Q QUIT",
                (25, 202),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (255, 255, 255),
                2,
            )

            cv2.imshow(
                "AUREX - Phase 35 Temporal Memory",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("r"):
                temporal_memory.reset()
                environment_engine.reset()
                behavior_engine.reset()
                hazard_engine.reset()

                print("Temporal memory reset.")

            time.sleep(0.001)

    finally:
        camera.release()
        cv2.destroyAllWindows()

        print()
        print("=" * 72)
        print("AUREX PHASE 35 STOPPED")
        print("=" * 72)

        print(
            "Frames remembered:",
            temporal_memory.frame_index,
        )

        print(
            "Events recorded:",
            len(temporal_memory.events),
        )

        print()
        print("Recent temporal events:")

        for event in temporal_memory.recent_events(10):
            print(
                f"- {event.event_type.value}: "
                f"{event.description}"
            )


if __name__ == "__main__":
    main()