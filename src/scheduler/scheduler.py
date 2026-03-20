import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import schedule
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from src.api import FootballDataAPIClient

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = [5, 10, 15]  # wait time before each retry attempt


class MatchdayScheduler:
    def __init__(self, config):
        self.config = config
        # per-instance logger under "src" so we can enable/disable our package centrally
        self.logger = logging.getLogger(f"src.{self.__class__.__name__}")
        self.api_client = FootballDataAPIClient(config.api_football_key)
        self.bot = Bot(token=config.telegram_token)
        self.users_file = "data/users.json"

    def load_users(self):
        try:
            with open(self.users_file, "r") as f:
                return json.load(f)
        except:
            return {}

    async def send_notification(self, chat_id, match_info):
        """
        Send a match reminder notification with retry on failure.

        Attempts up to MAX_RETRIES times with exponential backoff between attempts.
        Logs a warning on each failed attempt and an error if all retries are exhausted.
        """
        match_date = datetime.fromisoformat(
            match_info["date"].replace("Z", "+00:00")
        ).astimezone(ZoneInfo("Europe/Rome"))

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ Lineup set — stop reminders",
                        callback_data=f"lineup_set:{match_info['id']}",
                    )
                ]
            ]
        )

        message = (
            f"⚽ Serie A Reminder!\n\n"
            f"🏆 {match_info['round']}\n"
            f"🆚 {match_info['home']} vs {match_info['away']}\n"
            f"🕐 Kickoff: {match_date}\n\n"
            f"Don't forget to set your lineup!"
        )

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                await self.bot.send_message(
                    chat_id=chat_id, text=message, reply_markup=keyboard
                )
                self.logger.info(
                    f"Notification sent to {chat_id}"
                    + (f" (attempt {attempt + 1})" if attempt > 0 else "")
                )
                return
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BACKOFF_SECONDS[attempt]
                    self.logger.warning(
                        f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {chat_id}: {e}. "
                        f"Retrying in {wait}s..."
                    )
                    await asyncio.sleep(wait)

        self.logger.error(
            f"All {MAX_RETRIES} attempts failed for {chat_id}: {last_error}"
        )

    async def check_and_schedule(self):
        self.logger.info(f"Checking... {datetime.now()}")

        match_info = self.api_client.get_first_match_of_matchday(self.config.league_id)

        if not match_info:
            self.logger.info("No matches found")
            return

        match_id = match_info["id"]

        self.logger.info(f"First match of matchday: {match_info}")

        # Check if match has actually started or finished
        # Valid statuses for upcoming matches: SCHEDULED, TIMED
        if match_info["status"] not in ["SCHEDULED", "TIMED"]:
            self.logger.info(
                "Match already started or finished, skipping notifications"
            )
            return

        match_time = datetime.fromisoformat(match_info["date"].replace("Z", "+00:00"))

        # Don't notify if the match has already kicked off
        now = datetime.now(match_time.tzinfo)
        if now >= match_time:
            self.logger.info(
                f"Match has already started at {match_time}, skipping notifications"
            )
            return

        users = self.load_users()
        notifications = []

        for chat_id, settings in users.items():
            if not settings.get("active", True):
                continue

            # Skip if user already confirmed lineup for this match
            if str(match_id) in settings.get("confirmed_matches", []):
                self.logger.info(
                    f"Skipping {chat_id}: lineup already confirmed for match {match_id}"
                )
                continue

            hours_before = settings.get(
                "hours_before", self.config.default_hours_before
            )
            notification_time = match_time - timedelta(hours=hours_before)

            if now >= notification_time:
                self.logger.info(f"Queuing notification for {chat_id}")
                notifications.append(self.send_notification(chat_id, match_info))
            else:
                self.logger.info(
                    f"Not time yet for {chat_id}: {now} < {notification_time}"
                )

        if notifications:
            await asyncio.gather(*notifications)

    def run(self):
        asyncio.run(self.check_and_schedule())
        # Run the check every hour
        schedule.every().hour.do(lambda: asyncio.run(self.check_and_schedule()))

        self.logger.info("Scheduler started: checking every hour")
        while True:
            schedule.run_pending()
            time.sleep(60)
