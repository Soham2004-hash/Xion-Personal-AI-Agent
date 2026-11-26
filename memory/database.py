# ============================================================
# XION SQLITE DATABASE
# Existing memory + tasks + M5.7 conversation persistence
# ============================================================

import sqlite3
from pathlib import Path
from datetime import datetime


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "xion.db"
# ============================================================
# MEMORY KEY NORMALIZATION
# ============================================================

def normalize_memory_key(key: str) -> str:
    """
    Convert different expressions of the same memory key
    into one canonical key.
    """

    if not isinstance(key, str):
        raise TypeError("Memory key must be a string.")

    cleaned = key.lower().strip()
    cleaned = " ".join(cleaned.replace("_", " ").split())

    aliases = {
        "project": "current_project",
        "my project": "current_project",
        "current project": "current_project",
        "my current project": "current_project",

        "first project": "first_project",
        "my first project": "first_project",

        "my college": "college",
        "current college": "college",
        "my current college": "college",

        "my name": "name",
        "my course": "course",
    }

    return aliases.get(
        cleaned,
        cleaned.replace(" ", "_")
    )

def get_connection():
    """Create and return a SQLite database connection."""

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def initialize_database():
    """
    Initialize all XION database tables.

    Existing tables are preserved.
    New conversation tables are created only if missing.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ----------------------------------------------------
        # 1. EXISTING MEMORIES TABLE
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_key TEXT UNIQUE NOT NULL,
                memory_value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # ----------------------------------------------------
        # 2. EXISTING TASKS TABLE
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # 3. M5.7 — CONVERSATION SESSIONS
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_title TEXT NOT NULL DEFAULT 'New Conversation',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # ----------------------------------------------------
        # 4. M5.7 — CONVERSATION MESSAGES
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL
                    CHECK(role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,

                FOREIGN KEY(session_id)
                    REFERENCES conversation_sessions(id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # 5. INDEXES FOR FASTER HISTORY RETRIEVAL
        # ----------------------------------------------------

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_conversation_messages_session
            ON conversation_messages(session_id, id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_conversation_sessions_updated
            ON conversation_sessions(updated_at)
        """)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ============================================================
# EXISTING MEMORY FUNCTIONS
# ============================================================

def save_memory(key: str, value: str):
    """Save or update a memory."""

    conn = get_connection()

    try:
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
        """, (
            normalize_memory_key(key),
            value.strip(),
            now,
            now
        ))

        conn.commit()

    finally:
        conn.close()


def get_memory(key: str):
    """Retrieve a memory using its key."""

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT memory_value
            FROM memories
            WHERE memory_key = ?
        """, (normalize_memory_key(key),))

        result = cursor.fetchone()

        return result[0] if result else None

    finally:
        conn.close()


def delete_memory(key: str):
    """Delete a memory."""

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM memories
            WHERE memory_key = ?
        """, (key.lower().strip(),))

        deleted = cursor.rowcount
        conn.commit()

        return deleted > 0

    finally:
        conn.close()


def get_all_memories():
    """Return all saved memories."""

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT memory_key, memory_value, updated_at
            FROM memories
            ORDER BY updated_at DESC
        """)

        return cursor.fetchall()

    finally:
        conn.close()
