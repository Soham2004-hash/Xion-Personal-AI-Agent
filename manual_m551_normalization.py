from agent.brain import understand_command
from agent.context import clear_context, get_context


print("=" * 60)
print("XION M5.5.1 BRAIN NORMALIZATION TEST")
print("=" * 60)


def test_complete_task():

    clear_context()

    result = understand_command(
        "Complete the protocol task",
        get_context()
    )

    print("\nTEST 1 — COMPLETE TASK")
    print(result)

    assert result["intent"] == "COMPLETE_TASK"
    assert result["parameters"]["task_name"] == "the protocol task"

    print("PASS")


def test_complete_generic():

    clear_context()

    result = understand_command(
        "Complete a task",
        get_context()
    )

    print("\nTEST 2 — GENERIC COMPLETE")
    print(result)

    assert result["intent"] == "COMPLETE_TASK"
    assert result["parameters"]["task_name"] == ""

    print("PASS")


def test_recall_current_project():

    clear_context()

    result = understand_command(
        "What is my current project?",
        get_context()
    )

    print("\nTEST 3 — RECALL CURRENT PROJECT")
    print(result)

    assert result["intent"] == "RECALL_MEMORY"
    assert result["parameters"]["key"] == "current_project"

    print("PASS")


def test_recall_project():

    clear_context()

    result = understand_command(
        "What is my project?",
        get_context()
    )

    print("\nTEST 4 — RECALL PROJECT")
    print(result)

    assert result["intent"] == "RECALL_MEMORY"
    assert result["parameters"]["key"] == "current_project"

    print("PASS")


def test_delete_task():

    clear_context()

    result = understand_command(
        "Delete the data task",
        get_context()
    )

    print("\nTEST 5 — DELETE TASK")
    print(result)

    assert result["intent"] == "DELETE_TASK"
    assert result["parameters"]["task_name"] == "the data task"

    print("PASS")


def test_delete_generic():

    clear_context()

    result = understand_command(
        "Delete a task",
        get_context()
    )

    print("\nTEST 6 — GENERIC DELETE")
    print(result)

    assert result["intent"] == "DELETE_TASK"
    assert result["parameters"]["task_name"] == ""

    print("PASS")


print("\nRunning tests...")

test_complete_task()
test_complete_generic()
test_recall_current_project()
test_recall_project()
test_delete_task()
test_delete_generic()

print("\n" + "=" * 60)
print("M5.5.1 NORMALIZATION TEST COMPLETE")
print("=" * 60)
print("ALL TESTS PASSED.")
print("=" * 60)