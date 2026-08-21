# VS Code, Spotify, Brave

import subprocess


def open_vscode():

    try:
        subprocess.run(
            ["open", "-a", "Visual Studio Code"]
        )

        return "Opening Visual Studio Code."

    except Exception:
        return "I could not open Visual Studio Code."


def open_spotify():

    try:
        subprocess.run(
            ["open", "-a", "Spotify"]
        )

        return "Opening Spotify."

    except Exception:
        return "I could not open Spotify."


def open_brave():

    try:
        subprocess.run(
            ["open", "-a", "Brave Browser"]
        )

        return "Opening Brave Browser."

    except Exception:
        return "I could not open Brave Browser."