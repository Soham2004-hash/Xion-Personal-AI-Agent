# SQLite memory later

import sqlite3
from pathlib import Path
from datetime import datetime


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Database directory
DATA_DIR = BASE_DIR / "data"

# Create data directory if it does not exist
DATA_DIR.mkdir(exist_ok=True)

# Database file
DB_PATH = DATA_DIR / "xion.db"


def get_connection():
    """
    Create and return a SQLite database connection.
    """
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """
    Create required database tables.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------
    # MEMORIES TABLE
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_key TEXT UNIQUE NOT NULL,
            memory_value TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # -------------------------
    # TASKS TABLE
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            priority TEXT NOT NULL DEFAULT 'medium',
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_memory(key: str, value: str):
    """
    Save or update a memory.
    """

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO memories (
            memory_key,
            memory_value,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(memory_key)
        DO UPDATE SET
            memory_value = excluded.memory_value,
            updated_at = excluded.updated_at
    """, (key.lower().strip(), value.strip(), now, now))

    conn.commit()
    conn.close()


def get_memory(key: str):
    """
    Retrieve a memory using its key.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT memory_value
        FROM memories
        WHERE memory_key = ?
    """, (key.lower().strip(),))

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None


def delete_memory(key: str):
    """
    Delete a memory.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM memories
        WHERE memory_key = ?
    """, (key.lower().strip(),))

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted > 0


def get_all_memories():
    """
    Return all saved memories.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT memory_key, memory_value, updated_at
        FROM memories
        ORDER BY updated_at DESC
    """)

    results = cursor.fetchall()

    conn.close()

    return results