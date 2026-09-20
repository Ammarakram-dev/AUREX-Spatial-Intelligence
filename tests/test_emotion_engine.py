from identity.emotion_engine import AUREXEmotionEngine
from identity.emotion_state import EmotionType


def test_neutral_expression():
    engine = AUREXEmotionEngine()

    result = engine.analyze(
        external_features={
            "eye_opening": 0.21,
            "mouth_opening": 0.035,
            "mouth_width": 0.25,
            "mouth_curve": 0.0,
            "brow_height": 0.03,
        }
    )

    assert result.face_detected
    assert result.emotion in {
        EmotionType.NEUTRAL,
        EmotionType.UNKNOWN,
    }


def test_surprised_expression():
    engine = AUREXEmotionEngine()

    result = engine.analyze(
        external_features={
            "eye_opening": 0.28,
            "mouth_opening": 0.11,
            "mouth_width": 0.31,
            "mouth_curve": 0.0,
            "brow_height": 0.05,
        }
    )

    assert result.emotion == EmotionType.SURPRISED
    assert result.confidence > 0.45


def test_happy_expression():
    engine = AUREXEmotionEngine()

    result = engine.analyze(
        external_features={
            "eye_opening": 0.21,
            "mouth_opening": 0.045,
            "mouth_width": 0.32,
            "mouth_curve": 0.02,
            "brow_height": 0.035,
        }
    )

    assert result.emotion == EmotionType.HAPPY


def test_no_face():
    engine = AUREXEmotionEngine()

    result = engine.analyze(
        face_detected=False
    )

    assert result.emotion == EmotionType.UNKNOWN
    assert result.confidence == 0.0
    assert not result.face_detected


def test_temporal_stability():
    engine = AUREXEmotionEngine(history_size=6)

    for _ in range(6):
        result = engine.analyze(
            external_features={
                "eye_opening": 0.28,
                "mouth_opening": 0.11,
                "mouth_width": 0.31,
                "mouth_curve": 0.0,
                "brow_height": 0.05,
            }
        )

    assert result.emotion == EmotionType.SURPRISED
    assert result.stability >= 0.8


if __name__ == "__main__":
    test_neutral_expression()
    test_surprised_expression()
    test_happy_expression()
    test_no_face()
    test_temporal_stability()

    print("=" * 70)
    print("AUREX PHASE 28 EMOTION ENGINE TEST: PASSED")
    print("=" * 70)