from voice.voice_engine import (
    AUREXVoiceEngine,
)

from core.intent.multimodal import (
    AUREXMultimodalFusion,
)


def test_voice_emergency():

    voice = AUREXVoiceEngine()

    command = voice.parse(
        "emergency"
    )

    assert (
        command.intent.value
        == "emergency"
    )

    assert command.confidence >= 0.90


def test_voice_object():

    voice = AUREXVoiceEngine()

    command = voice.parse(
        "show me the phone"
    )

    assert (
        command.intent.value
        == "show"
    )

    assert (
        command.entities["object"]
        == "phone"
    )


def test_multimodal_agreement():

    voice = AUREXVoiceEngine()

    command = voice.parse(
        "show me the phone"
    )

    fusion = AUREXMultimodalFusion()

    decision = fusion.combine(
        voice_command=command,
        gesture_intent="show",
    )

    assert decision.intent == "show"
    assert decision.confidence >= 0.80
    assert "voice" in decision.sources
    assert "gesture" in decision.sources


def test_unknown():

    voice = AUREXVoiceEngine()

    command = voice.parse("hello")

    fusion = AUREXMultimodalFusion()

    decision = fusion.combine(
        voice_command=command
    )

    assert decision.intent == "unknown"


if __name__ == "__main__":

    test_voice_emergency()
    test_voice_object()
    test_multimodal_agreement()
    test_unknown()

    print(
        "PHASE 33 MULTIMODAL TESTS PASSED"
    )