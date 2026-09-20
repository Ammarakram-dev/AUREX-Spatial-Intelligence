from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    import cv2

    from vision.camera import AUREXCamera
    from vision.human_detector import AUREXHumanDetector
    from vision.person_tracker import AUREXPersonTracker
    from vision.pose_estimator import AUREXPoseEstimator

    print()
    print("=" * 72)
    print("AUREX STEP 3 — LIVE SYSTEM VALIDATION")
    print("=" * 72)
    print()
    print("Initializing live perception pipeline...")
    print()

    camera = AUREXCamera()
    detector = AUREXHumanDetector()
    tracker = AUREXPersonTracker()
    pose = AUREXPoseEstimator()

    if not camera.open():
        print("ERROR: Could not open the camera.")
        return 1

    print("[1/6] Camera ................. PASS")
    print("[2/6] Human detector ......... READY")
    print("[3/6] Person tracker ......... READY")
    print("[4/6] Pose estimator ......... READY")
    print()
    print("LIVE CAMERA VALIDATION")
    print("-" * 72)
    print("Look at the camera and move naturally.")
    print("Press Q to stop.")
    print()

    frames = 0
    frames_with_people = 0
    total_people = 0
    start_time = time.perf_counter()
    last_report = start_time

    try:
        while True:
            frame = camera.read()

            if frame is None:
                print("WARNING: Camera returned an empty frame.")
                continue

            frames += 1

            height, width = frame.shape[:2]

            detections = detector.detect(frame)

            if detections:
                frames_with_people += 1
                total_people += len(detections)

            tracked_people = tracker.update(
                detections,
                width
            )

            pose_result = pose.process(frame)

            display = frame.copy()

            for person in tracked_people:
                x1 = int(person.x1)
                y1 = int(person.y1)
                x2 = int(person.x2)
                y2 = int(person.y2)

                cv2.rectangle(
                    display,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                label = (
                    f"Person {person.person_id} "
                    f"{person.confidence:.2f}"
                )

                cv2.putText(
                    display,
                    label,
                    (x1, max(25, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

            try:
                pose.draw(display, pose_result)
            except Exception:
                pass

            elapsed = time.perf_counter() - start_time
            fps = frames / elapsed if elapsed > 0 else 0.0

            cv2.putText(
                display,
                f"AUREX LIVE | FPS: {fps:.1f}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                display,
                f"People: {len(tracked_people)}",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "AUREX - Live System Validation",
                display
            )

            now = time.perf_counter()

            if now - last_report >= 2.0:
                print(
                    f"Frames: {frames:5d} | "
                    f"People: {len(tracked_people):2d} | "
                    f"FPS: {fps:5.1f}"
                )
                last_report = now

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    except KeyboardInterrupt:
        print()
        print("Validation interrupted by user.")

    finally:
        camera.release()

        try:
            pose.close()
        except Exception:
            pass

        cv2.destroyAllWindows()

    elapsed = time.perf_counter() - start_time
    fps = frames / elapsed if elapsed > 0 else 0.0
    detection_rate = (
        (frames_with_people / frames) * 100
        if frames > 0
        else 0.0
    )

    print()
    print("=" * 72)
    print("STEP 3 — LIVE VALIDATION SUMMARY")
    print("=" * 72)
    print()
    print(f"Total frames ............. {frames}")
    print(f"Frames with people ...... {frames_with_people}")
    print(f"Total detected people ... {total_people}")
    print(f"Detection frame rate .... {detection_rate:.1f}%")
    print(f"Average FPS ............. {fps:.1f}")
    print()

    if frames > 0:
        print("[5/6] Live perception ......... PASS")
        print("[6/6] Runtime processing ...... PASS")
        print()
        print("=" * 72)
        print("STEP 3 LIVE SYSTEM VALIDATION PASSED")
        print("=" * 72)
        print()
        return 0

    print("[5/6] Live perception ......... FAILED")
    print("[6/6] Runtime processing ...... FAILED")
    print()
    print("No camera frames were processed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())