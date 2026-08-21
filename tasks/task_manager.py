 # Today's tasks later

from datetime import datetime

from memory.database import get_connection


VALID_PRIORITIES = {"high", "medium", "low"}


def add_task(task_name: str, priority: str = "medium"):
    """
    Add a new task.
    """

    priority = priority.lower().strip()

    if priority not in VALID_PRIORITIES:
        priority = "medium"

    task_name = task_name.strip()

    if not task_name:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (
            task_name,
            status,
            priority,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        task_name,
        "pending",
        priority,
        datetime.now().isoformat()
    ))

    task_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return task_id


def get_tasks(status: str = None):
    """
    Get tasks from database.
    """

    conn = get_connection()
    cursor = conn.cursor()

    if status:
        cursor.execute("""
            SELECT id, task_name, status, priority, created_at
            FROM tasks
            WHERE status = ?
            ORDER BY
                CASE priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                created_at ASC
        """, (status,))

    else:
        cursor.execute("""
            SELECT id, task_name, status, priority, created_at
            FROM tasks
            ORDER BY
                CASE priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                created_at ASC
        """)

    tasks = cursor.fetchall()

    conn.close()

    return tasks


def get_pending_tasks():
    """
    Get all pending tasks.
    """

    return get_tasks(status="pending")


def get_next_task():
    """
    Get the highest-priority pending task.
    """

    tasks = get_pending_tasks()

    if tasks:
        return tasks[0]

    return None


def complete_task(task_name: str):
    """
    Complete a task using partial name matching.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET
            status = 'completed',
            completed_at = ?
        WHERE LOWER(task_name)
        LIKE LOWER(?)
        AND status = 'pending'
    """, (
        datetime.now().isoformat(),
        f"%{task_name.strip()}%"
    ))

    updated = cursor.rowcount

    conn.commit()
    conn.close()

    return updated > 0


def delete_task(task_name: str):
    """
    Delete a task using partial name matching.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM tasks
        WHERE LOWER(task_name)
        LIKE LOWER(?)
    """, (
        f"%{task_name.strip()}%",
    ))

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted > 0

def clear_completed_tasks():
    """
    Delete all completed tasks.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM tasks
        WHERE status = 'completed'
    """)

    deleted_count = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted_count