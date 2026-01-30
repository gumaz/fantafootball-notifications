
import json
import logging
from zoneinfo import ZoneInfo
import schedule
import time
from datetime import datetime, timedelta
from telegram import Bot
import asyncio
from src.api import FootballDataAPIClient


class MatchdayScheduler:
    def __init__(self, config):
        self.config = config
        # per-instance logger under "src" so we can enable/disable our package centrally
        self.logger = logging.getLogger(f"src.{self.__class__.__name__}")
        self.api_client = FootballDataAPIClient(config.api_football_key)
        self.bot = Bot(token=config.telegram_token)
        self.users_file = 'data/users.json'
    
    def load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    async def send_notification(self, chat_id, match_info):
        try:
            match_date = datetime.fromisoformat(
                match_info['date'].replace('Z', '+00:00')
            ).astimezone(ZoneInfo("Europe/Rome"))

            message = (
                f"⚽ Serie A Reminder!\n\n"
                f"🏆 {match_info['round']}\n"
                f"🆚 {match_info['home']} vs {match_info['away']}\n"
                f"🕐 Kickoff: {match_date}\n\n"
                f"Don't forget to set your lineup!"
            )
            await self.bot.send_message(chat_id=chat_id, text=message)
            self.logger.info(f"Notification sent to {chat_id}")
        except Exception as e:
            self.logger.error(f"Error sending notification to {chat_id}: {e}")
    
    def check_and_schedule(self):
        self.logger.info(f"Checking... {datetime.now()}")
        
        match_info = self.api_client.get_first_match_of_matchday(
            self.config.league_id
        )
        
        if not match_info:
            self.logger.info("No matches found")
            return
        
        self.logger.info(f"First match of matchday: {match_info}")

        # Check if match has actually started or finished
        # Valid statuses for upcoming matches: SCHEDULED, TIMED
        if match_info["status"] not in ['SCHEDULED', 'TIMED']:
            self.logger.info(f"Match already started or finished, skipping notifications")
            return
        
        match_time = datetime.fromisoformat(
            match_info['date'].replace('Z', '+00:00')
        )

        users = self.load_users()
        
        for chat_id, settings in users.items():
            if not settings.get('active', True):
                continue
            
            hours_before = settings.get(
                'hours_before', 
                self.config.default_hours_before
            )
            notification_time = match_time - timedelta(hours=hours_before)

            now = datetime.now(notification_time.tzinfo)

            if now >= notification_time:
                self.logger.info(f"Sending to {chat_id}")
                asyncio.run(self.send_notification(chat_id, match_info))
            else:
                self.logger.info(f"Not time yet for {chat_id}: {now} < {notification_time}")
    
    def run(self):
        self.check_and_schedule()
        # Run the check every hour instead of once per day
        schedule.every().hour.do(self.check_and_schedule)

        self.logger.info("Scheduler started: checking every hour")
        while True:
            schedule.run_pending()
            time.sleep(60)
