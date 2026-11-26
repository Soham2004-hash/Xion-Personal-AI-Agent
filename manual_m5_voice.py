from agent.brain import understand_command
from agent.context import (
    clear_context,
    get_context,
    set_pending_action,
    clear_pending_action,
    update_context,
)
from agent.router import process_intent
from voice.listener import listen
from voice.speaker import speak


print("=" * 60)
print("XION M5.5 — MULTI-TURN VOICE TEST")
print("=" * 60)

clear_context()

speak(
    "Xion voice system ready. "
    "You can test a multi-turn task command."
)


while True:

    # ========================================================
    # LISTEN
    # ========================================================

    query = listen()

    if not query:
        continue

    print("\nUSER:", query)


    # ========================================================
    # GET CURRENT CONTEXT
    # ========================================================

    context = get_context()


    # ========================================================
    # BRAIN
    # ========================================================

    intent_data = understand_command(
        query,
        context
    )

    print(
        "XION BRAIN:",
        intent_data
    )


    intent = intent_data.get(
        "intent",
        "UNKNOWN"
    )

    parameters = intent_data.get(
        "parameters",
        {}
    )


    # ========================================================
    # MULTI-TURN TASK HANDLING
    # ========================================================

    if intent in {
        "ADD_TASK",
        "COMPLETE_TASK",
        "DELETE_TASK"
    }:

        task_name = parameters.get(
            "task_name",
            ""
        )

        if not isinstance(
            task_name,
            str
        ):
            task_name = ""

        task_name = task_name.strip()


        # ----------------------------------------------------
        # ADD TASK
        # ----------------------------------------------------

        if intent == "ADD_TASK":

            priority = parameters.get(
                "priority",
                "medium"
            )

            if not isinstance(
                priority,
                str
            ):
                priority = "medium"

            priority = priority.lower().strip()

            if priority not in {
                "high",
                "medium",
                "low"
            }:
                priority = "medium"


            if not task_name:

                set_pending_action(
                    "ADD_TASK",
                    {
                        "task_name": "",
                        "priority": priority
                    }
                )

                response = "What task should I add?"

                update_context(
                    intent=intent,
                    parameters=parameters,
                    response=response
                )

                speak(response)

                continue


        # ----------------------------------------------------
        # COMPLETE TASK
        # ----------------------------------------------------

        if intent == "COMPLETE_TASK":

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

                speak(response)

                continue


        # ----------------------------------------------------
        # DELETE TASK
        # ----------------------------------------------------

        if intent == "DELETE_TASK":

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

                speak(response)

                continue


    # ========================================================
    # ROUTER
    # ========================================================

    response = process_intent(
        intent_data
    )


    # ========================================================
    # CLEAR PENDING ACTION
    # ========================================================

    if intent in {
        "ADD_TASK",
        "COMPLETE_TASK",
        "DELETE_TASK"
    }:

        clear_pending_action()


    # ========================================================
    # UPDATE CONTEXT
    # ========================================================

    update_context(
        intent=intent,
        parameters=parameters,
        response=response
    )


    # ========================================================
    # EXIT
    # ========================================================

    if response == "EXIT":

        speak(
            "Goodbye. Have a productive day."
        )

        break


    # ========================================================
    # SPEAK RESPONSE
    # ========================================================

    speak(response)


print("\nM5.5 VOICE TEST ENDED.")