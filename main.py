# ============================================================
# XION PERSONAL AI ASSISTANT
# MAIN RUNTIME
# ============================================================

import re

from agent.brain import understand_command, answer_from_history

from agent.context import (
    get_context,
    update_context,
    set_pending_action,
    get_pending_action,
    get_pending_parameters,
    clear_pending_action,
)

from agent.router import process_intent

from memory.database import (
    initialize_database,
    get_memory,
    save_memory,
    normalize_memory_key,
)

from memory.conversation_manager import (
    get_or_create_session,
    get_recent_messages,
    save_message,
)

from voice.listener import listen
from voice.speaker import speak


# Persistent session used for this runtime. get_or_create_session()
# resumes the latest session, creating one only when none exists.
CURRENT_SESSION_ID = None


def save_conversation_message(role, content):
    """Persist a message without allowing a database issue to crash XION."""
    if CURRENT_SESSION_ID is None or not isinstance(content, str) or not content.strip():
        return
    try:
        save_message(CURRENT_SESSION_ID, role, content.strip())
    except Exception as error:
        print(f"CONVERSATION SAVE ERROR ({role}): {error}")


# ============================================================
# COMMAND NORMALIZATION
# ============================================================

def normalize_command(query):
    """Normalize voice commands for deterministic matching."""

    if not isinstance(query, str):
        return ""

    query = query.lower().strip()

    query = query.replace("’", "'")

    query = re.sub(r"[.!?,]+$", "", query)

    query = re.sub(r"\s+", " ", query)

    return query


def is_incomplete_memory_command(query):
    """
    Detect a memory-saving command that visibly ends before its value.

    This runs before the LLM so conversation history cannot fill in a
    missing value from an older memory command.
    """
    normalized = normalize_command(query)

    memory_starters = (
        "remember ",
        "remember that ",
        "save ",
        "save that ",
        "store ",
        "store that ",
        "note ",
        "note that ",
    )

    incomplete_endings = (" is", " as", " to", " =")

    return (
        normalized.startswith(memory_starters)
        and normalized.endswith(incomplete_endings)
    )


def respond_and_continue(response, intent, parameters=None):
    """Update context, persist and speak a response, then let caller continue."""
    update_context(
        intent=intent,
        parameters=parameters or {},
        response=response,
    )
    save_conversation_message("assistant", response)
    speak(response)


def handle_memory_confirmation(query):
    """
    Resolve a pending memory overwrite confirmation.

    Returns:
        response string if confirmation was handled
        None if there is no confirmation to resolve
    """

    if get_pending_action() != "UPDATE_MEMORY":
        return None

    normalized_query = normalize_command(query)

    pending = get_pending_parameters() or {}
    if not isinstance(pending, dict):
        return None

    key = pending.get("key", "")
    value = pending.get("value", "")
    old_value = pending.get("old_value", "")

    # Confirm the proposed update
    if normalized_query in CONFIRM_COMMANDS:

        save_memory(key, value)
        clear_pending_action()

        return (
            f"Done. I updated your memory. "
            f"{key} is now {value}."
        )

    # Reject the proposed update
    if normalized_query in REJECT_COMMANDS:

        clear_pending_action()

        return (
            f"Okay. I kept the existing memory. "
            f"{key} remains {old_value}."
        )

    # Any other command is not treated as confirmation.
    return None




# ============================================================
# DIRECT COMMAND HANDLING
# ============================================================

EXIT_COMMANDS = {
    "goodbye",
    "bye",
    "exit",
    "quit",
    "stop",
    "goodbye xion",
    "bye xion",
    "exit xion",
    "quit xion",
    "stop xion",
}

CANCEL_COMMANDS = {
    "cancel",
    "cancel that",
    "never mind",
    "nevermind",
    "forget it",
    "don't do that",
    "do not do that",
}

CONFIRM_COMMANDS = {
    "yes",
    "yes please",
    "yeah",
    "yep",
    "yup",
    "sure",
    "correct",
    "confirm",
    "confirm it",
    "yes confirm it",
    "update",
    "update it",
    "ok update",
    "okay update",
    "do it",
    "yes do it",
    "save it",
    "go ahead",
    "alright",
    "all right",
    "okay",
    "ok",
}

REJECT_COMMANDS = {
    "no",
    "no thanks",
    "nope",
    "nah",
    "no don't update",
    "do not update",
    "keep existing",
    "keep the old one",
    "keep it",
    "leave it",
    "cancel",
}

# ============================================================
# STARTUP
# ============================================================

def startup():

    global CURRENT_SESSION_ID

    print("=" * 60)
    print("XION PERSONAL AI ASSISTANT")
    print("=" * 60)

    # Initialize SQLite database and persistent conversation tables.
    initialize_database()
    CURRENT_SESSION_ID = get_or_create_session()

    print("\nDatabase initialized successfully.")
    print(f"Conversation session: {CURRENT_SESSION_ID}")
    print("XION is ready.")

    greeting = (
        "Hello. This is Xion, "
        "your personal AI assistant. "
        "How may I help you?"
    )
    save_conversation_message("assistant", greeting)
    speak(greeting)

# ============================================================
# MAIN ASSISTANT LOOP
# ============================================================

def run_assistant():

    while True:

        try:

            # ------------------------------------------------
            # 1. LISTEN
            # ------------------------------------------------

            query = listen()

            if not query:
                continue

            print("\nUSER:", query)

            normalized_query = normalize_command(query)

            # Load earlier messages BEFORE storing this utterance so a
            # HISTORY_QUERY does not accidentally include its own question.
            conversation_history = get_recent_messages(
                CURRENT_SESSION_ID,
                limit=30,
            )
            save_conversation_message("user", query)

            # ------------------------------------------------
            # 2. HANDLE EXIT BEFORE BRAIN
            # ------------------------------------------------
            # This prevents pending task actions from treating
            # "goodbye" or "exit" as a task name.

            if normalized_query in EXIT_COMMANDS:

                clear_pending_action()

                farewell = "Goodbye. Have a productive day."
                save_conversation_message("assistant", farewell)
                speak(farewell)

                break

            # ------------------------------------------------
            # 3. HANDLE MEMORY UPDATE CONFIRMATION
            # ------------------------------------------------
            # Do this before generic cancellation so "cancel" during a
            # memory overwrite receives the correct memory-specific reply.

            memory_confirmation = handle_memory_confirmation(query)

            if memory_confirmation is not None:
                respond_and_continue(
                    memory_confirmation,
                    intent="MEMORY_CONFIRMATION",
                )
                continue

            # ------------------------------------------------
            # 3.5 HANDLE INCOMPLETE MEMORY COMMANDS
            # ------------------------------------------------
            # Do not let the LLM reuse an older value from conversation
            # history when the user has not finished the current command.

            if is_incomplete_memory_command(query):
                response = (
                    "I didn't hear the value you want to save. "
                    "Please repeat the complete command, for example: "
                    "Remember that my current project is TGSR."
                )
                respond_and_continue(
                    response,
                    intent="REMEMBER_INCOMPLETE",
                )
                continue

            # ------------------------------------------------
            # 3.6 HANDLE STANDALONE CONFIRMATION WITH NO PENDING ACTION
            # ------------------------------------------------
            # A confirmation phrase must never reach the Brain as a new
            # command when there is nothing waiting to be confirmed. This
            # prevents phrases such as "yes do it" from becoming tasks.

            if (
                normalized_query in CONFIRM_COMMANDS
                and get_pending_action() is None
            ):
                response = (
                    "There is no pending action waiting for confirmation. "
                    "Please tell me what you would like Xion to do."
                )
                respond_and_continue(
                    response,
                    intent="NO_PENDING_CONFIRMATION",
                )
                continue

            # ------------------------------------------------
            # 4. HANDLE GENERIC CANCEL BEFORE BRAIN
            # ------------------------------------------------

            if normalized_query in CANCEL_COMMANDS:
                clear_pending_action()

                response = "Okay. I cancelled the pending action."
                respond_and_continue(
                    response,
                    intent="CANCEL",
                )
                continue

            # ------------------------------------------------
            # 5. GET CURRENT CONVERSATION CONTEXT
            # ------------------------------------------------

            context = get_context()
            context["conversation_history"] = conversation_history

            # ------------------------------------------------
            # 5. XION BRAIN
            # ------------------------------------------------

            intent_data = understand_command(
                query,
                context
            )

            print(
                "XION BRAIN:",
                intent_data
            )

            # ------------------------------------------------
            # 6. EXTRACT INTENT AND PARAMETERS
            # ------------------------------------------------

            if not isinstance(intent_data, dict):
                intent_data = {
                    "intent": "UNKNOWN",
                    "parameters": {}
                }

            intent = intent_data.get(
                "intent",
                "UNKNOWN"
            )

            parameters = intent_data.get(
                "parameters",
                {}
            )

            if not isinstance(intent, str):
                intent = "UNKNOWN"

            intent = intent.upper().strip()

            if not isinstance(parameters, dict):
                parameters = {}
            # =================================================
            # 6.5 MEMORY SAVE VALIDATION + OVERWRITE CONFIRMATION
            # =================================================

            if intent == "REMEMBER":

                key = parameters.get("key", "")
                value = parameters.get("value", "")

                if not isinstance(key, str):
                    key = ""
                if not isinstance(value, str):
                    value = ""

                key = key.strip()
                value = value.strip()

                # Never save partial data or reuse a value from history.
                if not key or not value:
                    response = (
                        "I need both the memory name and its value. "
                        "Please say the complete command, for example: "
                        "Remember that my current project is TGSR."
                    )
                    respond_and_continue(
                        response,
                        intent="REMEMBER_INCOMPLETE",
                        parameters=parameters,
                    )
                    continue

                canonical_key = normalize_memory_key(key)
                existing_value = get_memory(canonical_key)

                if (
                    existing_value is not None
                    and str(existing_value).strip() != value
                ):
                    set_pending_action(
                        "UPDATE_MEMORY",
                        {
                            "key": canonical_key,
                            "value": value,
                            "old_value": existing_value,
                        },
                    )

                    response = (
                        f"I already have {canonical_key} saved as "
                        f"{existing_value}. "
                        f"Would you like me to replace it with {value}?"
                    )

                    respond_and_continue(
                        response,
                        intent="REMEMBER_CONFIRMATION_REQUIRED",
                        parameters=parameters,
                    )
                    continue

            # =================================================
            # 7. MULTI-TURN TASK HANDLING
            # =================================================

            if intent in {
                "ADD_TASK",
                "COMPLETE_TASK",
                "DELETE_TASK"
            }:

                task_name = parameters.get(
                    "task_name",
                    ""
                )

                if not isinstance(task_name, str):
                    task_name = ""

                task_name = task_name.strip()

                # ------------------------------------------------
                # ADD TASK
                # ------------------------------------------------

                if intent == "ADD_TASK":

                    priority = parameters.get(
                        "priority",
                        "medium"
                    )

                    if not isinstance(priority, str):
                        priority = "medium"

                    priority = priority.lower().strip()

                    if priority not in {
                        "high",
                        "medium",
                        "low"
                    }:
                        priority = "medium"

                    # Missing task name
                    if not task_name:

                        set_pending_action(
                            "ADD_TASK",
                            {
                                "task_name": "",
                                "priority": priority
                            }
                        )

                        response = (
                            "What task should I add?"
                        )

                        update_context(
                            intent=intent,
                            parameters=parameters,
                            response=response
                        )

                        save_conversation_message("assistant", response)
                        speak(response)

                        continue

                # ------------------------------------------------
                # COMPLETE TASK
                # ------------------------------------------------

                if intent == "COMPLETE_TASK":

                    # Missing task name
                    if not task_name:

                        set_pending_action(
                            "COMPLETE_TASK",
                            {
                                "task_name": ""
                            }
                        )

                        response = (
                            "Which task should I complete?"
                        )

                        update_context(
                            intent=intent,
                            parameters=parameters,
                            response=response
                        )

                        save_conversation_message("assistant", response)
                        speak(response)

                        continue

                # ------------------------------------------------
                # DELETE TASK
                # ------------------------------------------------

                if intent == "DELETE_TASK":

                    # Missing task name
                    if not task_name:

                        set_pending_action(
                            "DELETE_TASK",
                            {
                                "task_name": ""
                            }
                        )

                        response = (
                            "Which task should I delete?"
                        )

                        update_context(
                            intent=intent,
                            parameters=parameters,
                            response=response
                        )

                        save_conversation_message("assistant", response)
                        speak(response)

                        continue

            # =================================================
            # 8. HISTORY ANSWER OR NORMAL ROUTER
            # =================================================

            if intent == "HISTORY_QUERY":
                response = answer_from_history(
                    query,
                    conversation_history,
                )
            else:
                response = process_intent(intent_data)

            # =================================================
            # 9. CLEAR PENDING ACTION
            # =================================================

            if intent in {
                "ADD_TASK",
                "COMPLETE_TASK",
                "DELETE_TASK"
            }:

                clear_pending_action()

            # =================================================
            # 10. UPDATE CONVERSATION CONTEXT
            # =================================================

            update_context(
                intent=intent,
                parameters=parameters,
                response=response
            )

            # =================================================
            # 11. EXIT CHECK
            # =================================================

            if response == "EXIT":

                farewell = "Goodbye. Have a productive day."
                save_conversation_message("assistant", farewell)
                speak(farewell)

                break

            # =================================================
            # 12. SPEAK RESPONSE
            # =================================================

            if response:

                response_text = str(response)
                save_conversation_message("assistant", response_text)
                speak(response_text)

        except KeyboardInterrupt:

            print("\n\nKeyboard interruption detected.")

            clear_pending_action()

            farewell = "Shutting down. Goodbye."
            save_conversation_message("assistant", farewell)
            speak(farewell)

            break

        except Exception as error:

            print(
                f"\nXION RUNTIME ERROR: {error}"
            )

            error_response = (
                "Something went wrong. "
                "Please try that command again."
            )
            save_conversation_message("assistant", error_response)
            speak(error_response)

            continue


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

def main():

    try:

        startup()

        run_assistant()

    except KeyboardInterrupt:

        print("\nXION interrupted by user.")

        clear_pending_action()

    except Exception as error:

        print(
            f"\nXION STARTUP ERROR: {error}"
        )

    finally:

        print("\nXION has been stopped.")

        print("=" * 60)


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    main()
