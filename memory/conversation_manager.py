# ============================================================
# XION — PERSISTENT CONVERSATION MANAGER
# M5.7.2
# ============================================================

from datetime import datetime

from memory.database import get_connection


VALID_ROLES = {"user", "assistant", "system"}


def create_session(session_title="New Conversation"):
    """Create a new conversation session and return its ID."""

    title = str(session_title).strip() or "New Conversation"
    now = datetime.now().isoformat()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO conversation_sessions (
                session_title,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?)
        """, (title, now, now))

        session_id = cursor.lastrowid
        conn.commit()

        return session_id

    finally:
        conn.close()


def get_latest_session():
    """Return the most recently updated session."""

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, session_title, created_at, updated_at
            FROM conversation_sessions
            ORDER BY updated_at DESC, id DESC
            LIMIT 1
        """)

        result = cursor.fetchone()

        if result is None:
            return None

        return {
            "id": result[0],
            "session_title": result[1],
            "created_at": result[2],
            "updated_at": result[3]
        }

    finally:
        conn.close()


def get_or_create_session():
    """
    Resume the latest conversation.
    If no conversation exists, create one.
    """

    session = get_latest_session()

    if session:
        return session["id"]

    return create_session()


def save_message(session_id, role, content):
    """Save a message to a conversation session."""

    role = str(role).strip().lower()
    content = str(content).strip()

    if role not in VALID_ROLES:
        raise ValueError(
            f"Invalid message role: {role}. "
            f"Allowed roles: {VALID_ROLES}"
        )

    if not content:
        raise ValueError("Message content cannot be empty.")

    now = datetime.now().isoformat()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO conversation_messages (
                session_id,
                role,
                content,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (session_id, role, content, now))

        message_id = cursor.lastrowid

        cursor.execute("""
            UPDATE conversation_sessions
            SET updated_at = ?
            WHERE id = ?
        """, (now, session_id))

        if cursor.rowcount == 0:
            raise ValueError(
                f"Conversation session {session_id} does not exist."
            )

        conn.commit()

        return message_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_recent_messages(session_id, limit=20):
    """
    Retrieve the most recent messages in chronological order.
    """

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, role, content, created_at
            FROM conversation_messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (session_id, limit))

        results = cursor.fetchall()

        results.reverse()

        return [
            {
                "id": row[0],
                "role": row[1],
                "content": row[2],
                "created_at": row[3]
            }
            for row in results
        ]

    finally:
        conn.close()


def get_session_messages(session_id, limit=None):
    """Retrieve messages from a session."""

    conn = get_connection()

    try:
        cursor = conn.cursor()

        if limit is None:
            cursor.execute("""
                SELECT id, role, content, created_at
                FROM conversation_messages
                WHERE session_id = ?
                ORDER BY id ASC
            """, (session_id,))
        else:
            if limit < 1:
                raise ValueError("Limit must be at least 1.")

            cursor.execute("""
                SELECT id, role, content, created_at
                FROM conversation_messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (session_id, limit))

        results = cursor.fetchall()

        if limit is not None:
            results.reverse()

        return [
            {
                "id": row[0],
                "role": row[1],
                "content": row[2],
                "created_at": row[3]
            }
            for row in results
        ]

    finally:
        conn.close()


def update_session_title(session_id, new_title):
    """Update the title of an existing session."""

    new_title = str(new_title).strip()

    if not new_title:
        raise ValueError("Session title cannot be empty.")

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE conversation_sessions
            SET session_title = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            new_title,
            datetime.now().isoformat(),
            session_id
        ))

        updated = cursor.rowcount > 0
        conn.commit()

        return updated

    finally:
        conn.close()


def list_sessions(limit=20):
    """List the most recently updated conversation sessions."""

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                s.id,
                s.session_title,
                s.created_at,
                s.updated_at,
                COUNT(m.id) AS message_count
            FROM conversation_sessions s
            LEFT JOIN conversation_messages m
                ON s.id = m.session_id
            GROUP BY s.id
            ORDER BY s.updated_at DESC, s.id DESC
            LIMIT ?
        """, (limit,))

        results = cursor.fetchall()

        return [
            {
                "id": row[0],
                "session_title": row[1],
                "created_at": row[2],
                "updated_at": row[3],
                "message_count": row[4]
            }
            for row in results
        ]

    finally:
        conn.close()


def delete_session(session_id):
    """Delete a session and its messages."""

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM conversation_sessions
            WHERE id = ?
        """, (session_id,))

        deleted = cursor.rowcount > 0
        conn.commit()

        return deleted

    finally:
        conn.close()
