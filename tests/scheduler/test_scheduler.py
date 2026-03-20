"""
Tests for scheduler
Calls check_and_schedule (scheduler)
methods directly, mocking only external I/O (Telegram API, football API, file system).
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from src.scheduler.scheduler import MatchdayScheduler

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------
MATCH_ID = 537093  # int, as returned by the football API
CHAT_ID = "111"

MATCH_INFO = {
    "id": MATCH_ID,
    "date": (datetime.now(timezone.utc) + timedelta(hours=12)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    ),
    "round": 30,
    "home": "Juventus",
    "away": "Manchester United",
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


class TestCheckAndSchedule(unittest.IsolatedAsyncioTestCase):
    async def _run(self, users: dict) -> int:
        """
        Helper: writes users to a temp file, runs check_and_schedule with a
        mocked API returning MATCH_INFO, returns (send_count, persisted_users).
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(users, f)
            users_file = f.name

        try:
            scheduler = make_scheduler(users_file)
            scheduler.api_client.get_first_match_of_matchday = MagicMock(
                return_value=MATCH_INFO
            )
            scheduler.send_notification = AsyncMock()

            await scheduler.check_and_schedule()

            return scheduler.send_notification.call_count
        finally:
            os.unlink(users_file)

    async def test_notifies_when_window_open_and_not_confirmed(self):
        """Scheduler should send notification when within window and not confirmed."""
        users = {CHAT_ID: {"active": True, "hours_before": 24, "confirmed_matches": []}}
        send_count = await self._run(users)
        self.assertEqual(send_count, 1)

    async def test_stops_notifying_after_user_confirms_string_id(self):
        """Scheduler must skip notification when match_id (as string) is in confirmed_matches."""
        users = {
            CHAT_ID: {
                "active": True,
                "hours_before": 24,
                "confirmed_matches": [str(MATCH_ID)],
            }
        }
        send_count = await self._run(users)
        self.assertEqual(send_count, 0)

    async def test_does_not_notify_inactive_user(self):
        """Inactive users must never receive notifications."""
        users = {
            CHAT_ID: {"active": False, "hours_before": 24, "confirmed_matches": []}
        }
        send_count = await self._run(users)
        self.assertEqual(send_count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
