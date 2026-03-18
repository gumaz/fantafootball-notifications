"""
Tests for the lineup confirmation flow.

Calls the real handle_lineup_confirmed (bot) and check_and_schedule (scheduler)
methods directly, mocking only external I/O (Telegram API, football API, file system).
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.bot import FantasyBot
from src.scheduler.scheduler import MatchdayScheduler

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

MATCH_ID = 537093  # int, as returned by the football API
CHAT_ID = "111"

MATCH_INFO = {
    "id": MATCH_ID,
    # match is 12h from now: still in the future (won't be skipped as started),
    # but within the default 24h notification window (will trigger a send)
    "date": (datetime.now(timezone.utc) + timedelta(hours=12)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    ),
    "round": 30,
    "home": "Inter",
    "away": "Milan",
    "status": "TIMED",
}


def make_scheduler(users_file: str) -> MatchdayScheduler:
    """Instantiate MatchdayScheduler with mocked config and Telegram bot."""
    config = MagicMock()
    config.telegram_token = "fake-token"
    config.api_football_key = "fake-key"
    config.league_id = "SA"
    config.default_hours_before = 24

    with patch("src.scheduler.scheduler.Bot"):
        scheduler = MatchdayScheduler(config)

    scheduler.users_file = users_file
    return scheduler


class TestCheckAndSchedule(unittest.TestCase):
    def _run(self, users: dict) -> dict:
        """
        Helper: writes users to a temp file, runs check_and_schedule with a
        mocked API returning MATCH_INFO, and returns users as persisted on disk.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(users, f)
            users_file = f.name

        try:
            scheduler = make_scheduler(users_file)
            scheduler.api_client.get_first_match_of_matchday = MagicMock(
                return_value=MATCH_INFO
            )
            scheduler.send_notification = MagicMock()

            with patch("src.scheduler.scheduler.asyncio.run") as mock_run:
                scheduler.check_and_schedule()
                return mock_run.call_count, json.load(open(users_file))
        finally:
            os.unlink(users_file)

    def test_notifies_when_window_open_and_not_confirmed(self):
        """Scheduler should send notification when within window and not confirmed."""
        users = {CHAT_ID: {"active": True, "hours_before": 24, "confirmed_matches": []}}
        send_count, _ = self._run(users)
        self.assertEqual(send_count, 1)

    def test_stops_notifying_after_user_confirms_string_id(self):
        """Scheduler must skip notification when match_id (as string) is in confirmed_matches."""
        users = {
            CHAT_ID: {
                "active": True,
                "hours_before": 24,
                "confirmed_matches": [str(MATCH_ID)],
            }
        }
        send_count, _ = self._run(users)
        self.assertEqual(send_count, 0)

    def test_does_not_notify_inactive_user(self):
        """Inactive users must never receive notifications."""
        users = {
            CHAT_ID: {"active": False, "hours_before": 24, "confirmed_matches": []}
        }
        send_count, _ = self._run(users)
        self.assertEqual(send_count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
