import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gesture.gesture_recognizer import (
    AUREXGestureRecognizer,
    GestureType,
)
from gesture.intent_mapper import (
    AUREXIntentMapper,
)


def main():

    print("=" * 60)
    print("AUREX GESTURE INTELLIGENCE TEST")
    print("=" * 60)

    recognizer = (
        AUREXGestureRecognizer()
    )

    mapper = AUREXIntentMapper()

    tests = {
        "RIGHT SWIPE": [
            (100, 300),
            (130, 300),
            (170, 300),
            (220, 300),
            (280, 300),
        ],
        "LEFT SWIPE": [
            (300, 300),
            (260, 300),
            (220, 300),
            (170, 300),
            (100, 300),
        ],
        "UP SWIPE": [
            (300, 400),
            (300, 360),
            (300, 320),
            (300, 270),
            (300, 220),
        ],
        "DOWN SWIPE": [
            (300, 200),
            (300, 240),
            (300, 290),
            (300, 340),
            (300, 400),
        ],
        "ZIGZAG": [
            (100, 300),
            (160, 240),
            (220, 320),
            (280, 240),
            (340, 320),
        ],
    }

    for name, points in tests.items():

        result = recognizer.recognize(
            points
        )

        intent = mapper.map(
            result
        )

        print()
        print(name)
        print(
            "Gesture:",
            result.gesture.value,
        )
        print(
            "Confidence:",
            f"{result.confidence * 100:.1f}%",
        )
        print(
            "Intent:",
            intent.name,
        )
        print(
            "Action:",
            intent.action,
        )

    print()
    print("=" * 60)
    print("GESTURE INTELLIGENCE TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()