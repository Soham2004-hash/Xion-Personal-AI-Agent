# Decides which tool handles a command
from tasks.task_manager import (
    add_task,
    get_pending_tasks,
    get_next_task,
    complete_task,
    delete_task
)

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
    # TASK COMMANDS
    # =====================================

    elif query.startswith("add a task to "):

        task_name = query.replace(
            "add a task to ",
            "",
            1
        ).strip()

        task_id = add_task(task_name)

        if task_id:
            return f"Task added: {task_name}."

        return "I could not add that task."


    elif query.startswith("add task "):

        task_name = query.replace(
            "add task ",
            "",
            1
        ).strip()

        task_id = add_task(task_name)

        if task_id:
            return f"Task added: {task_name}."

        return "I could not add that task."


    elif (
        "show my tasks" in query
        or "show tasks" in query
        or "what are my tasks" in query
    ):

        tasks = get_pending_tasks()

        if not tasks:
            return "You have no pending tasks."

        response = f"You have {len(tasks)} pending tasks. "

        for index, task in enumerate(tasks, start=1):

            task_name = task[1]
            priority = task[3]

            response += (
                f"Task {index}: "
                f"{task_name}, "
                f"priority {priority}. "
            )

        return response


    elif (
        "what should i work on next" in query
        or "what should i do next" in query
        or "next task" in query
    ):

        task = get_next_task()

        if task:
            return (
                f"Your next task is "
                f"{task[1]}. "
                f"It has {task[3]} priority."
            )

        return "You have no pending tasks."


    elif query.startswith("complete task "):

        task_name = query.replace(
            "complete task ",
            "",
            1
        ).strip()

        completed = complete_task(task_name)

        if completed:
            return f"Task completed: {task_name}."

        return f"I could not find a pending task called {task_name}."


    elif query.startswith("delete task "):

        task_name = query.replace(
            "delete task ",
            "",
            1
        ).strip()

        deleted = delete_task(task_name)

        if deleted:
            return f"Task deleted: {task_name}."

        return f"I could not find a task called {task_name}."

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