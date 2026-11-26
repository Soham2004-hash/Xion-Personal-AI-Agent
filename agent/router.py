# ============================================================
# XION ROUTER
# ============================================================
#
# The Router receives a validated intent from the XION Brain
# and executes the corresponding Python tool.
#
# M4.8:
# Intelligent task matching
#
# Matching order:
#   1. Exact match
#   2. Substring match
#   3. Token overlap
#   4. Ambiguous -> ask user
#
# ============================================================

import re

from tools.browser_tools import (
    open_youtube,
    open_github,
    open_kaggle,
)

from tools.system_tools import (
    open_vscode,
    open_spotify,
    open_brave,
)

from tools.time_tools import get_time

from tools.wikipedia_tool import search_wikipedia

from memory.database import (
    save_memory,
    get_memory,
)

from tasks.task_manager import (
    add_task,
    get_tasks,
    get_next_task,
    complete_task,
    delete_task,
)


# ============================================================
# TASK MATCHING
# ============================================================

def _normalize_text(text):
    """
    Normalize text for task matching.
    """

    if not isinstance(text, str):
        return ""

    text = text.lower().strip()

    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _tokenize(text):
    """
    Convert text into useful word tokens.
    """

    text = _normalize_text(text)

    if not text:
        return set()

    stop_words = {
        "the",
        "a",
        "an",
        "my",
        "to",
        "task",
        "please",
        "for",
        "of",
        "and",
    }

    tokens = set(text.split())

    return {
        token
        for token in tokens
        if token not in stop_words
    }


def _find_matching_task(task_name, pending_only=False):
    """
    Find the safest task match.

    Returns:
        task tuple
        None
        "AMBIGUOUS"
    """

    if not isinstance(task_name, str):
        return None

    query = _normalize_text(task_name)

    if not query:
        return None

    if pending_only:
        tasks = get_tasks(status="pending")
    else:
        tasks = get_tasks()

    if not tasks:
        return None

    # --------------------------------------------------------
    # 1. EXACT MATCH
    # --------------------------------------------------------

    exact_matches = []

    for task in tasks:
        stored_name = _normalize_text(task[1])

        if stored_name == query:
            exact_matches.append(task)

    if len(exact_matches) == 1:
        return exact_matches[0]

    if len(exact_matches) > 1:
        return "AMBIGUOUS"

    # --------------------------------------------------------
    # 2. SUBSTRING MATCH
    # --------------------------------------------------------

    substring_matches = []

    for task in tasks:

        stored_name = _normalize_text(task[1])

        if query in stored_name or stored_name in query:
            substring_matches.append(task)

    if len(substring_matches) == 1:
        return substring_matches[0]

    # If several tasks contain the phrase, do not guess.
    if len(substring_matches) > 1:

        # Try token matching before declaring ambiguity.
        query_tokens = _tokenize(query)

        token_candidates = []

        for task in substring_matches:

            task_tokens = _tokenize(task[1])

            if query_tokens and query_tokens.issubset(task_tokens):
                token_candidates.append(task)

        if len(token_candidates) == 1:
            return token_candidates[0]

        if len(token_candidates) > 1:
            return "AMBIGUOUS"

    # --------------------------------------------------------
    # 3. TOKEN OVERLAP
    # --------------------------------------------------------

    query_tokens = _tokenize(query)

    if not query_tokens:
        return None

    scored_tasks = []

    for task in tasks:

        task_tokens = _tokenize(task[1])

        overlap = query_tokens.intersection(task_tokens)

        if not overlap:
            continue

        # Number of matching meaningful words
        score = len(overlap)

        # Prefer tasks where most of the query words match
        coverage = score / len(query_tokens)

        scored_tasks.append(
            (
                score,
                coverage,
                task
            )
        )

    if not scored_tasks:
        return None

    # Sort by:
    #   1. number of matching words
    #   2. query coverage
    scored_tasks.sort(
        key=lambda item: (
            item[0],
            item[1]
        ),
        reverse=True
    )

    best_score = scored_tasks[0][0]
    best_coverage = scored_tasks[0][1]

    best_matches = [
        item
        for item in scored_tasks
        if item[0] == best_score
        and item[1] == best_coverage
    ]

    # Require at least 50% of the query words to match.
    if best_coverage < 0.5:
        return None

    if len(best_matches) == 1:
        return best_matches[0][2]

    return "AMBIGUOUS"


# ============================================================
# PROCESS INTENT
# ============================================================

def process_intent(intent_data):
    """
    Execute a validated intent produced by the XION Brain.

    Expected input:

    {
        "intent": "INTENT_NAME",
        "parameters": {}
    }
    """

    if not isinstance(intent_data, dict):
        return "I couldn't understand that command."

    intent = intent_data.get(
        "intent",
        "UNKNOWN"
    )

    parameters = intent_data.get(
        "parameters",
        {}
    )

    if not isinstance(intent, str):
        return "I couldn't understand that command."

    if not isinstance(parameters, dict):
        parameters = {}

    intent = intent.upper().strip()

    # ========================================================
    # GREETING
    # ========================================================

    if intent == "GREETING":
        return "Hello. I am Xion. How can I help you?"

    # ========================================================
    # APPLICATIONS
    # ========================================================

    if intent == "OPEN_YOUTUBE":
        return open_youtube()

    if intent == "OPEN_GITHUB":
        return open_github()

    if intent == "OPEN_KAGGLE":
        return open_kaggle()

    if intent == "OPEN_VSCODE":
        return open_vscode()

    if intent == "OPEN_SPOTIFY":
        return open_spotify()

    if intent == "OPEN_BRAVE":
        return open_brave()

    # ========================================================
    # TIME
    # ========================================================

    if intent == "GET_TIME":
        return get_time()

    # ========================================================
    # WIKIPEDIA
    # ========================================================

    if intent == "SEARCH_WIKIPEDIA":

        query = parameters.get(
            "query",
            ""
        )

        if not isinstance(query, str):
            return "Please tell me what you want me to search for."

        query = query.strip()

        if not query:
            return "Please tell me what you want me to search for."

        return search_wikipedia(query)

    # ========================================================
    # MEMORY - SAVE
    # ========================================================

    if intent == "REMEMBER":

        key = parameters.get(
            "key",
            ""
        )

        value = parameters.get(
            "value",
            ""
        )

        if not isinstance(key, str):
            return "I need a valid memory key."

        if not isinstance(value, str):
            return "I need a valid memory value."

        key = key.strip()
        value = value.strip()

        if not key or not value:
            return "I need both the memory key and the value."

        save_memory(
            key,
            value
        )

        return (
            f"I'll remember that "
            f"{key} is {value}."
        )

    # ========================================================
    # MEMORY - RECALL
    # ========================================================

    if intent == "RECALL_MEMORY":

        key = parameters.get(
            "key",
            ""
        )

        if not isinstance(key, str):
            return "Please tell me what you want me to remember."

        key = key.strip()

        if not key:
            return "Please tell me what you want me to remember."

        value = get_memory(key)

        if value is None:
            return f"I don't have a memory for {key}."

        return f"{key} is {value}."

    # ========================================================
    # ADD TASK
    # ========================================================

    if intent == "ADD_TASK":

        task_name = parameters.get(
            "task_name",
            ""
        )

        priority = parameters.get(
            "priority",
            "medium"
        )

        if not isinstance(task_name, str):
            return "Please tell me what task you want me to add."

        if not isinstance(priority, str):
            priority = "medium"

        task_name = task_name.strip()
        priority = priority.lower().strip()

        if not task_name:
            return "Please tell me what task you want me to add."

        if priority not in {
            "high",
            "medium",
            "low"
        }:
            priority = "medium"

        task_id = add_task(
            task_name,
            priority
        )

        if task_id is None:
            return "I couldn't add that task."

        return (
            f"I added the task "
            f"'{task_name}' "
            f"with {priority} priority."
        )

    # ========================================================
    # SHOW TASKS
    # ========================================================

    if intent == "SHOW_TASKS":

        tasks = get_tasks()

        if not tasks:
            return "You currently have no tasks."

        response = "Here are your tasks:"

        for task in tasks:

            task_id, task_name, status, priority, created_at = task

            response += (
                f"\n- {task_name} "
                f"({status}, "
                f"{priority} priority)"
            )

        return response

    # ========================================================
    # NEXT TASK
    # ========================================================

    if intent == "GET_NEXT_TASK":

        task = get_next_task()

        if not task:
            return "You currently have no pending tasks."

        (
            task_id,
            task_name,
            status,
            priority,
            created_at
        ) = task

        return (
            f"Your next task is "
            f"'{task_name}' "
            f"with {priority} priority."
        )

    # ========================================================
    # COMPLETE TASK
    # ========================================================

    if intent == "COMPLETE_TASK":

        task_name = parameters.get(
            "task_name",
            ""
        )

        if not isinstance(task_name, str):
            return "Please tell me which task you completed."

        task_name = task_name.strip()

        if not task_name:
            return "Please tell me which task you completed."

        # Find a pending task intelligently.
        matched_task = _find_matching_task(
            task_name,
            pending_only=True
        )

        if matched_task is None:
            return (
                f"I couldn't find a pending task "
                f"matching '{task_name}'."
            )

        if matched_task == "AMBIGUOUS":
            return (
                f"I found multiple pending tasks "
                f"matching '{task_name}'. "
                f"Please give me the full task name."
            )

        actual_task_name = matched_task[1]

        success = complete_task(
            actual_task_name
        )

        if success:
            return (
                f"I completed the task "
                f"'{actual_task_name}'."
            )

        return (
            f"I couldn't complete the task "
            f"'{actual_task_name}'."
        )

    # ========================================================
    # DELETE TASK
    # ========================================================

    if intent == "DELETE_TASK":

        task_name = parameters.get(
            "task_name",
            ""
        )

        if not isinstance(task_name, str):
            return "Please tell me which task you want to delete."

        task_name = task_name.strip()

        if not task_name:
            return "Please tell me which task you want to delete."

        # Find the task intelligently.
        matched_task = _find_matching_task(
            task_name,
            pending_only=False
        )

        if matched_task is None:
            return (
                f"I couldn't find a task "
                f"matching '{task_name}'."
            )

        if matched_task == "AMBIGUOUS":
            return (
                f"I found multiple tasks "
                f"matching '{task_name}'. "
                f"Please give me the full task name."
            )

        actual_task_name = matched_task[1]

        success = delete_task(
            actual_task_name
        )

        if success:
            return (
                f"I deleted the task "
                f"'{actual_task_name}'."
            )

        return (
            f"I couldn't delete the task "
            f"'{actual_task_name}'."
        )

    # ========================================================
    # EXIT
    # ========================================================

    if intent == "EXIT":
        return "EXIT"

    return "I don't understand that command yet."


# ============================================================
# LEGACY FALLBACK
# ============================================================

def process_command(query):
    """
    Legacy fallback for commands classified as UNKNOWN.
    """

    if not isinstance(query, str):
        return "I don't understand that command."

    query = query.lower().strip()

    if query in {
        "hello",
        "hi",
        "hey",
        "hello xion",
        "hi xion",
        "hey xion",
        "good morning",
        "good morning xion",
        "good afternoon",
        "good afternoon xion",
        "good evening",
        "good evening xion",
    }:
        return "Hello. I am Xion. How can I help you?"

    if query in {
        "goodbye",
        "bye",
        "exit",
        "quit",
        "stop",
        "goodbye xion",
        "bye xion",
        "exit xion",
        "quit xion",
    }:
        return "EXIT"

    return "I don't understand that command yet."