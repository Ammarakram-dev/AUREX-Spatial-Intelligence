"""
AUREX Spatial Intelligence
Camera Test
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import cv2

from vision.camera import AUREXCamera


def main() -> None:

    print("=" * 64)
    print("AUREX CAMERA TEST")
    print("=" * 64)
    print()

    camera = AUREXCamera()

    if not camera.open():
        print("ERROR: Unable to access the webcam.")
        return

    print("Camera connected successfully.")
    print("Press Q to close the camera.")
    print()

    try:

        while True:

            frame = camera.read()

            if frame is None:
                print("ERROR: Unable to read camera frame.")
                break

            cv2.imshow(
                "AUREX Spatial Intelligence - Vision",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    finally:

        camera.release()
        cv2.destroyAllWindows()

    print()
    print("Camera test completed successfully.")


if __name__ == "__main__":
    main()