from agent.brain import understand_command
from agent.context import (
    update_context,
    get_context,
    clear_context,
)


print("=" * 60)
print("XION M5.2 CONTEXT-AWARE BRAIN TEST")
print("=" * 60)


# ============================================================
# TEST 1
# ============================================================

clear_context()

update_context(
    intent="RECALL_MEMORY",
    parameters={
        "key": "current project"
    },
    response="current project is XION."
)

context = get_context()

print("\nTEST 1")
print("Context:")
print(context)

print("\nUSER:")
print("Add a task to finish it.")

result = understand_command(
    "Add a task to finish it.",
    context
)

print("\nBRAIN:")
print(result)


# ============================================================
# TEST 2
# ============================================================

clear_context()

update_context(
    intent="ADD_TASK",
    parameters={
        "task_name": "update protocol loader",
        "priority": "high"
    },
    response="I added the task 'update protocol loader'."
)

context = get_context()

print("\n" + "-" * 60)

print("\nTEST 2")
print("Context:")
print(context)

print("\nUSER:")
print("Complete that.")

result = understand_command(
    "Complete that.",
    context
)

print("\nBRAIN:")
print(result)


print("\n" + "=" * 60)
print("M5.2 TEST COMPLETE")
print("=" * 60)
