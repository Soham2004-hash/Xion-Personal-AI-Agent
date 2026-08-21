# Application entry point

from voice.speaker import speak, setup_voice
from voice.listener import listen
from agent.router import process_command
from memory.database import initialize_database

import datetime


def wish_me():

    hour = datetime.datetime.now().hour

    if 6 <= hour < 12:
        greeting = "Good morning."

    elif 12 <= hour < 18:
        greeting = "Good afternoon."

    elif 18 <= hour < 22:
        greeting = "Good evening."

    else:
        greeting = "Welcome back."

    speak(
        f"{greeting} "
        "This is Xion, your personal AI assistant. "
        "How may I help you?"
    )


def main():

    # Initialize SQLite database
    initialize_database()

    # Setup voice
    setup_voice()

    #greeting
    wish_me()

    while True:

        query = listen()

        response = process_command(query)

        if response == "EXIT":

            speak("Goodbye. Have a productive day.")
            break

        speak(response)


if __name__ == "__main__":
    main()