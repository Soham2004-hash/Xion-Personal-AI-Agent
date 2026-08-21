# Text-to-speech

import pyttsx3


VOICE_NAME = "Daniel"


def speak(text: str):
    """
    Speak one response using a fresh pyttsx3 engine.
    This is more reliable on some macOS systems.
    """

    print(f"XION: {text}")

    engine = None

    try:
        # Create a fresh engine
        engine = pyttsx3.init()

        engine.setProperty("rate", 180)
        engine.setProperty("volume", 1.0)

        # Select Daniel voice if available
        voices = engine.getProperty("voices")

        for voice in voices:
            if VOICE_NAME.lower() in voice.name.lower():
                engine.setProperty("voice", voice.id)
                break

        engine.say(str(text))
        engine.runAndWait()

    except Exception as e:
        print(f"TTS ERROR: {e}")

    finally:
        if engine is not None:
            try:
                engine.stop()
            except Exception:
                pass


def setup_voice():
    """
    Kept for compatibility with main.py.
    """
    print("XION voice system ready.")