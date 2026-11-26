import tempfile
from pathlib import Path
import memory.database as database

from agent.brain import understand_command
from agent.context import (
    clear_context,
    get_context,
    set_pending_action,
    clear_pending_action,
)
from agent.router import process_intent
from memory.database import (
    initialize_database,
    get_connection,
)


print("=" * 60)
print("XION M5.4 MULTI-TURN ACTION INTEGRATION TEST")
print("=" * 60)


# ============================================================
# INITIALIZE ISOLATED TEST DATABASE
# ============================================================

_TEST_DB_DIR = tempfile.TemporaryDirectory(
    prefix="xion_m54_test_"
)

database.DB_PATH = (
    Path(_TEST_DB_DIR.name) / "test_xion.db"
)

initialize_database()
clear_context()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_test_task(task_name, priority="medium"):
    """
    Insert a test task directly into SQLite.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (
            task_name,
            status,
            priority,
            created_at
        )
        VALUES (?, ?, ?, datetime('now'))
    """, (
        task_name,
        "pending",
        priority
    ))

    conn.commit()
    conn.close()


def get_task(task_name):
    """
    Retrieve the latest task with the given name.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT task_name, status, priority
        FROM tasks
        WHERE task_name = ?
        ORDER BY id DESC
        LIMIT 1
    """, (task_name,))

    result = cursor.fetchone()

    conn.close()

    return result


def cleanup_test_tasks():
    """
    Remove tasks created by previous runs of this test.
    """

    test_tasks = [
        "XION M5.4 COMPLETE TEST",
        "XION M5.4 DELETE TEST",
        "XION M5.4 AMBIGUOUS A",
        "XION M5.4 AMBIGUOUS B",
    ]

    conn = get_connection()
    cursor = conn.cursor()

    for task_name in test_tasks:

        cursor.execute("""
            DELETE FROM tasks
            WHERE task_name = ?
        """, (task_name,))

    conn.commit()
    conn.close()


# ============================================================
# CLEAN OLD TEST DATA
# ============================================================

print("\nCleaning previous M5.4 test data...")

cleanup_test_tasks()

print("Previous test data cleaned.")


# ============================================================
# TEST 1 — MULTI-TURN COMPLETE
# ============================================================

print("\n" + "-" * 60)
print("\nTEST 1 — MULTI-TURN COMPLETE")


clear_context()


# ------------------------------------------------------------
# First turn
# ------------------------------------------------------------

result = understand_command(
    "Complete a task.",
    get_context()
)

print("\nUSER:")
print("Complete a task.")

print("\nBRAIN:")
print(result)


assert result["intent"] == "COMPLETE_TASK"

assert (
    result["parameters"]["task_name"]
    == ""
)


print("\nPASS: Incomplete COMPLETE_TASK detected.")


# ------------------------------------------------------------
# Store pending action
# ------------------------------------------------------------

set_pending_action(
    "COMPLETE_TASK",
    {
        "task_name": ""
    }
)


print("\nXION:")
print("Which task should I complete?")


# ------------------------------------------------------------
# Create unique test task
# ------------------------------------------------------------

task_name = "XION M5.4 COMPLETE TEST"

add_test_task(
    task_name,
    "high"
)


# ------------------------------------------------------------
# Second turn
# ------------------------------------------------------------

result = understand_command(
    task_name,
    get_context()
)

print("\nUSER:")
print(task_name)

print("\nBRAIN:")
print(result)


assert result["intent"] == "COMPLETE_TASK"

assert (
    result["parameters"]["task_name"]
    == task_name
)


print("\nPASS: COMPLETE_TASK resolved.")


# ------------------------------------------------------------
# Execute through router
# ------------------------------------------------------------

response = process_intent(result)

print("\nXION:")
print(response)


assert "completed" in response.lower()


# ------------------------------------------------------------
# Verify SQLite
# ------------------------------------------------------------

db_task = get_task(task_name)

print("\nDATABASE:")
print(db_task)


assert db_task is not None

assert db_task[0] == task_name

assert db_task[1] == "completed"

assert db_task[2] == "high"


clear_pending_action()


print(
    "\nPASS: Multi-turn completion "
    "successfully updated SQLite."
)


# ============================================================
# TEST 2 — MULTI-TURN DELETE
# ============================================================

print("\n" + "-" * 60)
print("\nTEST 2 — MULTI-TURN DELETE")


clear_context()


# ------------------------------------------------------------
# First turn
# ------------------------------------------------------------

result = understand_command(
    "Delete a task.",
    get_context()
)

print("\nUSER:")
print("Delete a task.")

print("\nBRAIN:")
print(result)


assert result["intent"] == "DELETE_TASK"

assert (
    result["parameters"]["task_name"]
    == ""
)


print("\nPASS: Incomplete DELETE_TASK detected.")


# ------------------------------------------------------------
# Store pending action
# ------------------------------------------------------------

set_pending_action(
    "DELETE_TASK",
    {
        "task_name": ""
    }
)


print("\nXION:")
print("Which task should I delete?")


# ------------------------------------------------------------
# Create unique test task
# ------------------------------------------------------------

task_name = "XION M5.4 DELETE TEST"

add_test_task(
    task_name,
    "medium"
)


# ------------------------------------------------------------
# Second turn
# ------------------------------------------------------------

result = understand_command(
    task_name,
    get_context()
)

print("\nUSER:")
print(task_name)

print("\nBRAIN:")
print(result)


assert result["intent"] == "DELETE_TASK"

assert (
    result["parameters"]["task_name"]
    == task_name
)


print("\nPASS: DELETE_TASK resolved.")


# ------------------------------------------------------------
# Execute through router
# ------------------------------------------------------------

response = process_intent(result)

print("\nXION:")
print(response)


assert "deleted" in response.lower()


# ------------------------------------------------------------
# Verify SQLite
# ------------------------------------------------------------

db_task = get_task(task_name)

print("\nDATABASE:")
print(db_task)


assert db_task is None


clear_pending_action()


print(
    "\nPASS: Multi-turn deletion "
    "successfully updated SQLite."
)


# ============================================================
# TEST 3 — AMBIGUOUS TASK PROTECTION
# ============================================================

print("\n" + "-" * 60)
print("\nTEST 3 — AMBIGUOUS TASK PROTECTION")


clear_context()


# ------------------------------------------------------------
# Create two similar tasks
# ------------------------------------------------------------

add_test_task(
    "XION M5.4 AMBIGUOUS A",
    "medium"
)

add_test_task(
    "XION M5.4 AMBIGUOUS B",
    "medium"
)


# ------------------------------------------------------------
# Try to complete using an ambiguous name
# ------------------------------------------------------------

result = process_intent({
    "intent": "COMPLETE_TASK",
    "parameters": {
        "task_name": "XION M5.4 AMBIGUOUS"
    }
})


print("\nREQUEST:")
print("Complete XION M5.4 AMBIGUOUS")


print("\nXION:")
print(result)


assert "multiple" in result.lower()

assert "full task name" in result.lower()


print(
    "\nPASS: Ambiguous completion "
    "was safely rejected."
)


# ------------------------------------------------------------
# Verify neither task was completed
# ------------------------------------------------------------

task_a = get_task(
    "XION M5.4 AMBIGUOUS A"
)

task_b = get_task(
    "XION M5.4 AMBIGUOUS B"
)


print("\nDATABASE CHECK:")

print(
    "Task A:",
    task_a
)

print(
    "Task B:",
    task_b
)


assert task_a is not None
assert task_b is not None

assert task_a[1] == "pending"
assert task_b[1] == "pending"


print(
    "\nPASS: Ambiguous request "
    "did not modify either task."
)


# ============================================================
# FINAL CLEANUP
# ============================================================

print("\n" + "-" * 60)
print("\nCleaning M5.4 test data...")

cleanup_test_tasks()

print("Test data cleaned.")


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 60)
print("M5.4 INTEGRATION TEST COMPLETE")
print("=" * 60)
print("\nALL TESTS PASSED.")
print("=" * 60)