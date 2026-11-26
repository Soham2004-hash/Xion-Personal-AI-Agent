"""SQLite task-management operations for XION.

Task names are matched safely: an exact match is preferred; otherwise a
partial match is accepted only when it identifies exactly one task. Ambiguous
matches never update or delete multiple records.
"""

from datetime import datetime
import re

from memory.database import get_connection

VALID_PRIORITIES = {"high", "medium", "low"}


def _clean_task_name(task_name):
    if not isinstance(task_name, str):
        return ""
    return re.sub(r"\s+", " ", task_name).strip()


def _normalize_task_name(task_name):
    """Normalize a task name for case- and punctuation-insensitive comparison."""
    task_name = _clean_task_name(task_name).casefold()
    task_name = re.sub(r"[^\w\s]", " ", task_name)
    return re.sub(r"\s+", " ", task_name).strip()


def _find_unique_task_id(cursor, task_name, pending_only=False):
    """Find one task ID by exact name, or a unique partial name match.

    Returns None when there is no match or when more than one record matches.
    Exact duplicates are also treated as ambiguous rather than modifying all.
    """
    normalized_query = _normalize_task_name(task_name)
    if not normalized_query:
        return None

    query = "SELECT id, task_name FROM tasks"
    if pending_only:
        query += " WHERE status = 'pending'"
    cursor.execute(query)
    rows = cursor.fetchall()

    normalized_rows = [
        (row[0], row[1], _normalize_task_name(row[1]))
        for row in rows
    ]

    exact_matches = [row for row in normalized_rows if row[2] == normalized_query]
    if len(exact_matches) == 1:
        return exact_matches[0][0]
    if len(exact_matches) > 1:
        return None

    partial_matches = [
        row for row in normalized_rows
        if normalized_query in row[2]
    ]
    if len(partial_matches) == 1:
        return partial_matches[0][0]

    return None


def add_task(task_name: str, priority: str = "medium"):
    """Add a pending task.

    A duplicate pending task (same normalized name) is not inserted. In that
    case the existing task ID is returned, preserving the original function's
    integer/None return contract and preventing duplicate database rows.
    Completed tasks do not block a new task with the same name.
    """
    task_name = _clean_task_name(task_name)
    if not task_name:
        return None

    if not isinstance(priority, str):
        priority = "medium"
    priority = priority.lower().strip()
    if priority not in VALID_PRIORITIES:
        priority = "medium"

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, task_name FROM tasks WHERE status = 'pending'"
        )
        for existing_id, existing_name in cursor.fetchall():
            if _normalize_task_name(existing_name) == _normalize_task_name(task_name):
                return existing_id

        cursor.execute(
            """
            INSERT INTO tasks (task_name, status, priority, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (task_name, "pending", priority, datetime.now().isoformat()),
        )
        task_id = cursor.lastrowid
        conn.commit()
        return task_id
    finally:
        conn.close()


def get_tasks(status: str = None):
    """Return tasks ordered by priority and then creation time."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if status:
            cursor.execute(
                """
                SELECT id, task_name, status, priority, created_at
                FROM tasks
                WHERE status = ?
                ORDER BY
                    CASE priority
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                        ELSE 4
                    END,
                    created_at ASC,
                    id ASC
                """,
                (status,),
            )
        else:
            cursor.execute(
                """
                SELECT id, task_name, status, priority, created_at
                FROM tasks
                ORDER BY
                    CASE priority
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                        ELSE 4
                    END,
                    created_at ASC,
                    id ASC
                """
            )
        return cursor.fetchall()
    finally:
        conn.close()


def get_pending_tasks():
    """Return all pending tasks."""
    return get_tasks(status="pending")


def get_next_task():
    """Return the highest-priority pending task, or None."""
    tasks = get_pending_tasks()
    return tasks[0] if tasks else None


def complete_task(task_name: str):
    """Complete one uniquely identified pending task.

    Returns True only when exactly one task is updated. If the name is blank,
    missing, or ambiguous, no database record is changed.
    """
    task_name = _clean_task_name(task_name)
    if not task_name:
        return False

    conn = get_connection()
    try:
        cursor = conn.cursor()
        task_id = _find_unique_task_id(cursor, task_name, pending_only=True)
        if task_id is None:
            return False

        cursor.execute(
            """
            UPDATE tasks
            SET status = 'completed', completed_at = ?
            WHERE id = ? AND status = 'pending'
            """,
            (datetime.now().isoformat(), task_id),
        )
        updated = cursor.rowcount
        if updated == 1:
            conn.commit()
            return True
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_task(task_name: str):
    """Delete one uniquely identified task.

    Returns True only when exactly one task is deleted. Ambiguous partial
    matches are rejected to prevent accidental bulk deletion.
    """
    task_name = _clean_task_name(task_name)
    if not task_name:
        return False

    conn = get_connection()
    try:
        cursor = conn.cursor()
        task_id = _find_unique_task_id(cursor, task_name, pending_only=False)
        if task_id is None:
            return False

        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        deleted = cursor.rowcount
        if deleted == 1:
            conn.commit()
            return True
        conn.rollback()
        return False
    finally:
        conn.close()


def clear_completed_tasks():
    """Delete all completed tasks and return the number of deleted rows."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE status = 'completed'")
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count
    finally:
        conn.close()
