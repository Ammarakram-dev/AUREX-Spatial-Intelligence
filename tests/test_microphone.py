import speech_recognition as sr

print("=" * 60)
print("AUREX MICROPHONE + SPEECH TEST")
print("=" * 60)

recognizer = sr.Recognizer()

print("\nAvailable microphones:")
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{i}: {name}")

print("\nOpening default microphone...")

try:
    with sr.Microphone() as source:
        print("Adjusting for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        print("\n========================================")
        print("SPEAK NOW")
        print("Say: hello AUREX")
        print("========================================")

        audio = recognizer.listen(
            source,
            timeout=10,
            phrase_time_limit=8
        )

    print("\nAudio captured successfully.")
    print("Audio size:", len(audio.frame_data), "bytes")
    print("Sending audio for recognition...")

    text = recognizer.recognize_google(audio)

    print("\nSUCCESS!")
    print("Recognized:", text)

except sr.WaitTimeoutError:
    print("\nERROR: No speech detected within the timeout.")

except sr.UnknownValueError:
    print("\nERROR: Microphone captured audio, but speech was not understood.")

except sr.RequestError as e:
    print("\nERROR: Speech recognition service problem:")
    print(e)

except Exception as e:
    print("\nERROR:", type(e).__name__)
    print(e)