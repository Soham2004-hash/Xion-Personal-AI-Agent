from agent.brain import understand_command

from agent.context import (
    clear_context,
    get_context,
    set_pending_action,
    clear_pending_action,
)


print("=" * 60)
print("XION M5.3 MULTI-TURN TASK TEST")
print("=" * 60)


# ============================================================
# TEST 1
# ============================================================

clear_context()

print("\nTEST 1")
print("USER:")
print("Add a high priority task.")

result = understand_command(
    "Add a high priority task.",
    get_context()
)

print("\nBRAIN:")
print(result)

assert result["intent"] == "ADD_TASK"
assert result["parameters"]["task_name"] == ""
assert result["parameters"]["priority"] == "high"

print("\nPASS: Incomplete task detected.")


# ============================================================
# TEST 2
# ============================================================

set_pending_action(
    "ADD_TASK",
    {
        "task_name": "",
        "priority": "high"
    }
)

print("\n" + "-" * 60)

print("\nTEST 2")
print("Pending action:")
print(get_context())

print("\nUSER:")
print("Update the protocol loader.")

result = understand_command(
    "Update the protocol loader.",
    get_context()
)

print("\nBRAIN:")
print(result)

assert result["intent"] == "ADD_TASK"
assert (
    result["parameters"]["task_name"]
    == "Update the protocol loader."
)

assert result["parameters"]["priority"] == "high"

print("\nPASS: Missing task name successfully filled.")


# ============================================================
# TEST 3
# ============================================================

clear_pending_action()

print("\n" + "-" * 60)

print("\nTEST 3")
print("USER:")
print("Add a task.")

result = understand_command(
    "Add a task.",
    get_context()
)

print("\nBRAIN:")
print(result)

assert result["intent"] == "ADD_TASK"
assert result["parameters"]["task_name"] == ""

print("\nPASS: Generic incomplete task detected.")


# ============================================================
# TEST 4
# ============================================================

set_pending_action(
    "ADD_TASK",
    {
        "task_name": "",
        "priority": "medium"
    }
)

print("\n" + "-" * 60)

print("\nTEST 4")
print("USER:")
print("Finish the literature review.")

result = understand_command(
    "Finish the literature review.",
    get_context()
)

print("\nBRAIN:")
print(result)

assert result["intent"] == "ADD_TASK"
assert (
    result["parameters"]["task_name"]
    == "Finish the literature review."
)

assert result["parameters"]["priority"] == "medium"

print("\nPASS: Default priority preserved.")


print("\n" + "=" * 60)
print("M5.3 TEST COMPLETE")
print("=" * 60)