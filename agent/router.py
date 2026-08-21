# Decides which tool handles a command
from memory.database import (
    save_memory,
    get_memory,
    delete_memory
)

from tools.browser_tools import (
    open_youtube,
    open_github,
    open_kaggle
)

from tools.system_tools import (
    open_vscode,
    open_spotify,
    open_brave
)

from tools.time_tools import get_time


def process_command(query: str):

    if not query:
        return "I didn't hear that clearly."

    # =====================================
    # MEMORY COMMANDS
    # =====================================

    if query.startswith("remember "):

        content = query.replace("remember ", "", 1).strip()

        if " is " in content:

            key, value = content.split(" is ", 1)

            save_memory(key, value)

            return f"I'll remember that {key} is {value}."

        return (
            "Please say something like: "
            "remember my current project is Xion."
        )


    elif query.startswith("what is "):

        key = query.replace("what is ", "", 1).strip()

        memory = get_memory(key)

        if memory:
            return f"{key} is {memory}."

        return f"I don't have a memory for {key}."


    elif query.startswith("forget "):

        key = query.replace("forget ", "", 1).strip()

        deleted = delete_memory(key)

        if deleted:
            return f"I forgot {key}."

        return f"I couldn't find a memory called {key}."

    # =====================================
    # BROWSER COMMANDS
    # =====================================

    elif "open youtube" in query:
        return open_youtube()

    elif "open github" in query:
        return open_github()

    elif "open kaggle" in query or "open database" in query:
        return open_kaggle()

    # =====================================
    # SYSTEM COMMANDS
    # =====================================

    elif "open code" in query or "open vs code" in query:
        return open_vscode()

    elif "open spotify" in query or "play music" in query:
        return open_spotify()

    elif "open brave" in query or "open browser" in query:
        return open_brave()
    # =====================================
    # TIME
    # =====================================

    elif "time" in query:
        return get_time()

   # =====================================
    # EXIT
    # =====================================

    elif (
        "stop" in query
        or "exit" in query
        or "goodbye" in query
    ):
        return "EXIT"


    # =====================================
    # UNKNOWN COMMAND
    # =====================================

    else:
        return "I don't know how to do that yet."