import tempfile
from pathlib import Path
import memory.database as database

from agent.brain import understand_command
from agent.context import (
    clear_context,
    get_context,
    set_pending_action,
    clear_pending_action,
    update_context,
)
from agent.router import process_intent
from memory.database import (
    initialize_database,
    get_connection,
)


print("=" * 60)
print("XION M5.3 MULTI-TURN INTEGRATION TEST")
print("=" * 60)


# ============================================================
# INITIALIZE ISOLATED TEST DATABASE
# ============================================================

_TEST_DB_DIR = tempfile.TemporaryDirectory(
    prefix="xion_m53_test_"
)

database.DB_PATH = (
    Path(_TEST_DB_DIR.name) / "test_xion.db"
)

initialize_database()
clear_context()


# ============================================================
# TURN 1
# ============================================================

print("\nTEST 1 — INCOMPLETE TASK")

user_input = "Add a high priority task."

context = get_context()

intent_data = understand_command(
    user_input,
    context
)

print("\nUSER:")
print(user_input)

print("\nBRAIN:")
print(intent_data)


assert intent_data["intent"] == "ADD_TASK"
assert intent_data["parameters"]["task_name"] == ""
assert intent_data["parameters"]["priority"] == "high"


# ============================================================
# STORE PENDING ACTION
# ============================================================

set_pending_action(
    "ADD_TASK",
    {
        "task_name": "",
        "priority": "high"
    }
)

response = "What task should I add?"

update_context(
    intent=intent_data["intent"],
    parameters=intent_data["parameters"],
    response=response
)

print("\nXION:")
print(response)


# ============================================================
# TURN 2
# ============================================================

print("\n" + "-" * 60)

print("\nTEST 2 — COMPLETE PENDING TASK")

user_input = "Update the protocol loader."

context = get_context()

intent_data = understand_command(
    user_input,
    context
)

print("\nUSER:")
print(user_input)

print("\nBRAIN:")
print(intent_data)


assert intent_data["intent"] == "ADD_TASK"
assert (
    intent_data["parameters"]["task_name"]
    == "Update the protocol loader."
)

assert (
    intent_data["parameters"]["priority"]
    == "high"
)


# ============================================================
# ROUTER
# ============================================================

response = process_intent(intent_data)

print("\nXION:")
print(response)


assert "Update the protocol loader." in response
assert "high" in response


# ============================================================
# CLEAR PENDING ACTION
# ============================================================

clear_pending_action()


# ============================================================
# VERIFY SQLITE
# ============================================================

print("\n" + "-" * 60)

print("\nTEST 3 — DATABASE VERIFICATION")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT task_name, status, priority
    FROM tasks
    WHERE task_name = ?
    ORDER BY id DESC
    LIMIT 1
""", ("Update the protocol loader.",))

task = cursor.fetchone()

conn.close()


print("\nDATABASE RESULT:")
print(task)


assert task is not None
assert task[0] == "Update the protocol loader."
assert task[1] == "pending"
assert task[2] == "high"


print("\nPASS: Task successfully stored in SQLite.")


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 60)
print("M5.3 INTEGRATION TEST COMPLETE")
print("=" * 60)