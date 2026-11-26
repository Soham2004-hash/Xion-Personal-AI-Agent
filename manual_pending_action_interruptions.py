
from unittest.mock import patch

from agent.brain import understand_command
from agent.context import clear_context, get_context, set_pending_action


def run_test(name, pending_action, user_query, expected_intent, expected_task_name=None):
    clear_context()

    set_pending_action(
        pending_action,
        {"task_name": "", "priority": "high"},
    )

    # Deterministic commands should not require an Ollama call.
    with patch("agent.brain.ollama.chat") as mock_chat:
        result = understand_command(user_query, get_context())

        if expected_intent == "UNKNOWN":
            mock_chat.assert_called_once()
        else:
            mock_chat.assert_not_called()

    assert result["intent"] == expected_intent, (
        f"{name}: expected {expected_intent}, got {result}"
    )

    if expected_task_name is not None:
        assert result["parameters"]["task_name"] == expected_task_name, (
            f"{name}: incorrect task name: {result}"
        )

    print(f"PASS: {name}")


print("\nXION PENDING ACTION INTERRUPTION TESTS\n")

run_test(
    "ADD_TASK interrupted by time query",
    "ADD_TASK",
    "What time is it?",
    "GET_TIME",
)

run_test(
    "COMPLETE_TASK interrupted by YouTube command",
    "COMPLETE_TASK",
    "Open YouTube",
    "OPEN_YOUTUBE",
)

run_test(
    "DELETE_TASK interrupted by memory recall",
    "DELETE_TASK",
    "What is my current project?",
    "RECALL_MEMORY",
)

run_test(
    "ADD_TASK accepts ordinary follow-up",
    "ADD_TASK",
    "Finish the research paper",
    "ADD_TASK",
    "Finish the research paper",
)

run_test(
    "COMPLETE_TASK accepts ordinary follow-up",
    "COMPLETE_TASK",
    "Update the protocol loader",
    "COMPLETE_TASK",
    "Update the protocol loader",
)

run_test(
    "DELETE_TASK accepts ordinary follow-up",
    "DELETE_TASK",
    "Organise the data",
    "DELETE_TASK",
    "Organise the data",
)

run_test(
    "CANCEL overrides pending action",
    "ADD_TASK",
    "Cancel",
    "CANCEL",
)

run_test(
    "EXIT overrides pending action",
    "COMPLETE_TASK",
    "Goodbye",
    "EXIT",
)

clear_context()

print("\nALL PENDING ACTION TESTS PASSED")
