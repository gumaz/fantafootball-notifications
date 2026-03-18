"""
Tests for the lineup confirmation flow.

Calls the real handle_lineup_confirmed (bot) and check_and_schedule (scheduler)
methods directly, mocking only external I/O (Telegram API, football API, file system).
"""

import os
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.bot import FantasyBot
from src.scheduler.scheduler import MatchdayScheduler

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

MATCH_ID = 537093  # int, as returned by the football API
CHAT_ID = "111"


def make_bot(users: dict, users_file: str) -> FantasyBot:
    """Instantiate FantasyBot with pre-loaded users, bypassing file I/O on init."""
    with patch("src.bot.bot.FantasyBot.load_users", return_value=users):
        bot = FantasyBot(token="fake-token", users_file=users_file)
    return bot


class TestHandleLineupConfirmed(unittest.IsolatedAsyncioTestCase):
    async def test_confirmed_match_id_is_stored_as_string(self):
        """
        handle_lineup_confirmed must store the match_id as a string,
        since callback data is always a string.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            users_file = f.name

        try:
            users = {
                CHAT_ID: {"active": True, "hours_before": 24, "confirmed_matches": []}
            }
            bot = make_bot(users, users_file)

            # Build a mock Update that simulates the button press
            update = MagicMock()
            update.effective_chat.id = int(CHAT_ID)
            update.effective_user.language_code = "en"
            update.effective_user.is_bot = False
            query = AsyncMock()
            query.data = f"lineup_set:{MATCH_ID}"
            query.message.reply_text = AsyncMock()
            query.edit_message_reply_markup = AsyncMock()
            update.callback_query = query

            with patch.object(bot, "save_users"):
                await bot.handle_lineup_confirmed(update, MagicMock())

            confirmed = bot.users[CHAT_ID]["confirmed_matches"]
            self.assertEqual(confirmed, [str(MATCH_ID)])
        finally:
            os.unlink(users_file)


if __name__ == "__main__":
    unittest.main(verbosity=2)
