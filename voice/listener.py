# ============================================================
# XION VOICE LISTENER — IMPROVED VERSION
# ============================================================

import speech_recognition as sr


# ============================================================
# CONFIGURATION
# ============================================================

LANGUAGE = "en-IN"

LISTEN_TIMEOUT = 7
PHRASE_TIME_LIMIT = 20
PAUSE_THRESHOLD = 1.5

PHRASE_THRESHOLD = 0.15
NON_SPEAKING_DURATION = 0.5
AMBIENT_CALIBRATION_DURATION = 0.7


# ============================================================
# CREATE RECOGNIZER
# ============================================================

recognizer = sr.Recognizer()

recognizer.pause_threshold = PAUSE_THRESHOLD
recognizer.phrase_threshold = PHRASE_THRESHOLD
recognizer.non_speaking_duration = NON_SPEAKING_DURATION

recognizer.dynamic_energy_threshold = True


# ============================================================
# LISTEN
# ============================================================

def listen() -> str:
    """
    Listen to microphone input and return recognized speech.

    Returns:
        Lowercase text when recognized.
        Empty string when speech is unavailable.
    """

    try:

        with sr.Microphone() as source:

            print("\nListening...")

            # Calibrate for surrounding noise.
            recognizer.adjust_for_ambient_noise(
                source,
                duration=AMBIENT_CALIBRATION_DURATION
            )

            print(
                f"Microphone energy threshold: "
                f"{recognizer.energy_threshold:.2f}"
            )

            try:

                audio = recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT
                )

            except sr.WaitTimeoutError:

                print("No speech detected.")
                return ""

    except OSError as e:

        print(f"MICROPHONE ERROR: {e}")
        return ""

    except Exception as e:

        print(f"LISTENER ERROR: {e}")
        return ""

    # ========================================================
    # GOOGLE SPEECH RECOGNITION
    # ========================================================

    try:

        print("Recognizing...")

        # Try Indian English first.
        # Try multiple English recognition models on the SAME audio.
        query = None

        languages = ["en-IN", "en-US", "en-GB"]

        for language in languages:
            try:
                print(f"Trying recognition language: {language}")

                query = recognizer.recognize_google(
                    audio,
                    language=language
                )

                if query:
                    print(f"Recognized using {language}")
                    break

            except sr.UnknownValueError:
                print(f"Could not understand using {language}")

        if not query:
            return ""

        query = query.strip().lower()

        if not query:
            return ""

        print(f"YOU: {query}")

        return query

    except sr.UnknownValueError:

        print("Speech detected, but could not be understood.")
        return ""

    except sr.RequestError as e:

        print(f"Speech recognition service unavailable: {e}")
        return ""

    except Exception as e:

        print(f"RECOGNITION ERROR: {e}")
        return ""
