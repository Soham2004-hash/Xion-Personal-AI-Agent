
# ============================================================
# XION — M5.7.2 CONVERSATION MANAGER TEST
# Uses a temporary SQLite database.
# Does NOT modify data/xion.db
# ============================================================

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import memory.database as database
import memory.conversation_manager as manager


class TestConversationManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.test_db = Path(self.temp_dir.name) / "test_xion.db"

        self.db_patcher = patch.object(
            database,
            "DB_PATH",
            self.test_db
        )

        self.db_patcher.start()

        database.initialize_database()

    def tearDown(self):
        self.db_patcher.stop()
        self.temp_dir.cleanup()

    def test_create_session(self):
        session_id = manager.create_session("Test Conversation")

        session = manager.get_latest_session()

        self.assertIsNotNone(session)
        self.assertEqual(session["id"], session_id)
        self.assertEqual(
            session["session_title"],
            "Test Conversation"
        )

    def test_get_or_create_session(self):
        first_id = manager.get_or_create_session()
        second_id = manager.get_or_create_session()

        self.assertEqual(first_id, second_id)

    def test_save_and_retrieve_messages(self):
        session_id = manager.create_session()

        manager.save_message(
            session_id,
            "user",
            "My project is XION."
        )

        manager.save_message(
            session_id,
            "assistant",
            "Understood. Your project is XION."
        )

        messages = manager.get_session_messages(session_id)

        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[1]["role"], "assistant")

    def test_recent_messages_limit(self):
        session_id = manager.create_session()

        for i in range(5):
            manager.save_message(
                session_id,
                "user",
                f"Message {i + 1}"
            )

        messages = manager.get_recent_messages(
            session_id,
            limit=2
        )

        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["content"], "Message 4")
        self.assertEqual(messages[1]["content"], "Message 5")

    def test_invalid_role(self):
        session_id = manager.create_session()

        with self.assertRaises(ValueError):
            manager.save_message(
                session_id,
                "invalid",
                "Test message"
            )

    def test_empty_message(self):
        session_id = manager.create_session()

        with self.assertRaises(ValueError):
            manager.save_message(
                session_id,
                "user",
                "   "
            )

    def test_update_session_title(self):
        session_id = manager.create_session("Old Title")

        result = manager.update_session_title(
            session_id,
            "Updated Title"
        )

        session = manager.get_latest_session()

        self.assertTrue(result)
        self.assertEqual(
            session["session_title"],
            "Updated Title"
        )

    def test_list_sessions(self):
        session_id = manager.create_session("Conversation A")

        manager.save_message(
            session_id,
            "user",
            "Hello XION"
        )

        sessions = manager.list_sessions()

        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["message_count"], 1)

    def test_delete_session(self):
        session_id = manager.create_session()

        manager.save_message(
            session_id,
            "user",
            "This conversation will be deleted."
        )

        result = manager.delete_session(session_id)

        self.assertTrue(result)
        self.assertIsNone(manager.get_latest_session())

        messages = manager.get_session_messages(session_id)

        self.assertEqual(len(messages), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
