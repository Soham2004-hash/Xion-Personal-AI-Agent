from agent.brain import understand_command
from agent.context import (
    clear_context,
    get_context,
    set_pending_action,
)


print("=" * 60)
print("XION M5.4 MULTI-TURN ACTION TEST")
print("=" * 60)


# ============================================================
# TEST 1 — COMPLETE TASK
# ============================================================

clear_context()

print("\nTEST 1 — COMPLETE TASK")

result = understand_command(
    "Complete a task.",
    get_context()
)

print("\nUSER:")
print("Complete a task.")

print("\nBRAIN:")
print(result)

assert result["intent"] == "COMPLETE_TASK"
assert result["parameters"]["task_name"] == ""

print("\nPASS: Incomplete COMPLETE_TASK detected.")


set_pending_action(
    "COMPLETE_TASK",
    {
        "task_name": ""
    }
)


result = understand_command(
    "Update the protocol loader.",
    get_context()
)

print("\nUSER:")
print("Update the protocol loader.")

print("\nBRAIN:")
print(result)

assert result["intent"] == "COMPLETE_TASK"
assert (
    result["parameters"]["task_name"]
    == "Update the protocol loader."
)

print("\nPASS: COMPLETE_TASK resolved.")


# ============================================================
# TEST 2 — DELETE TASK
# ============================================================

clear_context()

print("\n" + "-" * 60)

print("\nTEST 2 — DELETE TASK")

result = understand_command(
    "Delete a task.",
    get_context()
)

print("\nUSER:")
print("Delete a task.")

print("\nBRAIN:")
print(result)

assert result["intent"] == "DELETE_TASK"
assert result["parameters"]["task_name"] == ""

print("\nPASS: Incomplete DELETE_TASK detected.")


set_pending_action(
    "DELETE_TASK",
    {
        "task_name": ""
    }
)


result = understand_command(
    "Organise the data.",
    get_context()
)

print("\nUSER:")
print("Organise the data.")

print("\nBRAIN:")
print(result)

assert result["intent"] == "DELETE_TASK"
assert (
    result["parameters"]["task_name"]
    == "Organise the data."
)

print("\nPASS: DELETE_TASK resolved.")


# ============================================================
# TEST 3 — EXISTING COMPLETE COMMAND
# ============================================================

clear_context()

print("\n" + "-" * 60)

print("\nTEST 3 — DIRECT COMPLETE COMMAND")

result = understand_command(
    "Complete Update the protocol loader.",
    get_context()
)

print("\nBRAIN:")
print(result)

assert result["intent"] == "COMPLETE_TASK"
assert result["parameters"]["task_name"]

print("\nPASS: Existing direct COMPLETE_TASK preserved.")


# ============================================================
# TEST 4 — EXISTING DELETE COMMAND
# ============================================================

clear_context()

print("\n" + "-" * 60)

print("\nTEST 4 — DIRECT DELETE COMMAND")

result = understand_command(
    "Delete Organise the data.",
    get_context()
)

print("\nBRAIN:")
print(result)

assert result["intent"] == "DELETE_TASK"
assert result["parameters"]["task_name"]

print("\nPASS: Existing direct DELETE_TASK preserved.")


print("\n" + "=" * 60)
print("M5.4 TEST COMPLETE")
print("=" * 60)