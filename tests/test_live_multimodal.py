from __future__ import annotations

import os
import tempfile
import threading
import time

import cv2
import speech_recognition as sr
from faster_whisper import WhisperModel

from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector
from core.intent.multimodal.fusion import AUREXMultimodalFusion
from voice.voice_engine import AUREXVoiceEngine


MODEL_SIZE = "tiny.en"


class LocalSpeechRecognizer:
    def __init__(self):
        print()
        print("=" * 70)
        print("Loading local Faster-Whisper model...")
        print("Model:", MODEL_SIZE)
        print("CPU mode: int8")
        print("=" * 70)

        self.model = WhisperModel(
            MODEL_SIZE,
            device="cpu",
            compute_type="int8",
        )

        self.recognizer = sr.Recognizer()

        self.recognizer.energy_threshold = 250
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.2
        self.recognizer.non_speaking_duration = 0.5

        print("Local speech model READY.")


    def listen_and_transcribe(self):
        print()
        print("-" * 70)
        print("Adjusting microphone...")
        print("-" * 70)

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1.0,
                )

                print()
                print("LISTENING... SPEAK NOW")
                print("Example: show me the phone")
                print()

                audio = self.recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=8,
                )

            print("Audio captured.")
            print("Transcribing locally...")

            wav_data = audio.get_wav_data()
            temp_path = None

            try:
                with tempfile.NamedTemporaryFile(
                    suffix=".wav",
                    delete=False,
                ) as temp_file:
                    temp_file.write(wav_data)
                    temp_path = temp_file.name

                segments, info = self.model.transcribe(
                    temp_path,
                    beam_size=1,
                    language="en",
                    vad_filter=True,
                    condition_on_previous_text=False,
                )

                text = " ".join(
                    segment.text.strip()
                    for segment in segments
                    if segment.text.strip()
                ).strip()

                if not text:
                    print("No speech recognized.")
                    return ""

                print()
                print("=" * 70)
                print("LOCAL TRANSCRIPTION")
                print("=" * 70)
                print("Heard:", text)
                print("Language:", info.language)
                print("=" * 70)

                return text

            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass

        except sr.WaitTimeoutError:
            print("No speech detected before timeout.")
            return ""

        except Exception as exc:
            print()
            print("Speech error:", type(exc).__name__)
            print(exc)
            return ""


class VoiceWorker:
    def __init__(self, speech_recognizer):
        self.speech_recognizer = speech_recognizer
        self.busy = False
        self.latest_text = ""
        self.thread = None

    def start(self):
        if self.busy:
            return False

        self.busy = True
        self.latest_text = ""

        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self.thread.start()
        return True

    def _run(self):
        try:
            self.latest_text = (
                self.speech_recognizer.listen_and_transcribe()
                or ""
            )
        finally:
            self.busy = False


def draw_text(frame, text, x, y, scale=0.65):
    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )


def main():
    print("=" * 70)
    print("AUREX PHASE 33 — MULTIMODAL INTELLIGENCE")
    print("=" * 70)
    print()
    print("REAL CAMERA + LOCAL MICROPHONE + LOCAL WHISPER")
    print()
    print("Press V to speak")
    print("Press R to reset")
    print("Press Q to quit")
    print("=" * 70)

    speech = LocalSpeechRecognizer()

    camera = AUREXCamera()
    detector = AUREXHumanDetector()
    voice_engine = AUREXVoiceEngine()
    fusion = AUREXMultimodalFusion()

    worker = VoiceWorker(speech)

    latest_voice = None
    latest_decision = None

    try:
        camera.open()

        print()
        print("Camera READY.")
        print("AUREX Phase 33 is LIVE.")
        print()

        while True:
            frame = camera.read()

            if frame is None:
                continue

            detections = detector.detect(frame)
            people_count = len(detections)

            if worker.latest_text:
                latest_voice = worker.latest_text
                worker.latest_text = ""

                voice_command = voice_engine.parse(
                    latest_voice
                )

                latest_decision = fusion.combine(
                    voice_command=voice_command
                )

                print()
                print("=" * 70)
                print("AUREX MULTIMODAL RESULT")
                print("=" * 70)
                print("Voice:", latest_voice)
                print("Intent:", voice_command.intent)
                print(
                    "Confidence:",
                    round(voice_command.confidence, 3),
                )

                if latest_decision is not None:
                    print(
                        "Fused intent:",
                        latest_decision.intent,
                    )
                    print(
                        "Fused confidence:",
                        round(
                            latest_decision.confidence,
                            3,
                        ),
                    )
                    print(
                        "Sources:",
                        latest_decision.sources,
                    )

                print("=" * 70)

            display = frame.copy()

            draw_text(
                display,
                "AUREX PHASE 33 - MULTIMODAL INTELLIGENCE",
                20,
                35,
            )

            draw_text(
                display,
                f"People detected: {people_count}",
                20,
                70,
            )

            if worker.busy:
                draw_text(
                    display,
                    "VOICE: LISTENING...",
                    20,
                    105,
                )
            else:
                draw_text(
                    display,
                    "VOICE: READY - PRESS V",
                    20,
                    105,
                )

            if latest_voice:
                draw_text(
                    display,
                    f"Heard: {latest_voice[:55]}",
                    20,
                    145,
                )

            if latest_decision is not None:
                draw_text(
                    display,
                    f"Intent: {latest_decision.intent}",
                    20,
                    185,
                )

                draw_text(
                    display,
                    f"Confidence: {latest_decision.confidence:.2f}",
                    20,
                    220,
                )

            draw_text(
                display,
                "V = Voice   R = Reset   Q = Quit",
                20,
                display.shape[0] - 25,
                0.55,
            )

            cv2.imshow(
                "AUREX Phase 33 - Multimodal Intelligence",
                display,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("v"):
                if worker.busy:
                    print("Voice listener is already active.")
                else:
                    print()
                    print("Starting local voice recognition...")
                    worker.start()

            elif key == ord("r"):
                latest_voice = None
                latest_decision = None
                worker.latest_text = ""

                voice_engine.reset()
                fusion.reset()

                print()
                print("AUREX multimodal state RESET.")

            elif key == ord("q"):
                break

            time.sleep(0.005)

    finally:
        camera.release()
        cv2.destroyAllWindows()

        print()
        print("=" * 70)
        print("AUREX PHASE 33 TEST ENDED")
        print("=" * 70)


if __name__ == "__main__":
    main()