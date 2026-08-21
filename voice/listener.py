# Speech-to-text

import speech_recognition as sr


def listen() -> str:
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")

        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source)

        audio = recognizer.listen(source)

    try:
        print("Recognizing...")

        query = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        print(f"YOU: {query}")

        return query.lower()

    except sr.UnknownValueError:
        return ""

    except sr.RequestError:
        print("Speech recognition service unavailable.")
        return ""