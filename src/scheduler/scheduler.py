import json
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
            print(f"✅ Notification sent to {chat_id}")
        except Exception as e:
            print(f"❌ Error sending notification to {chat_id}: {e}")
    
    def check_and_schedule(self):
        print(f"Checking... {datetime.now()}")
        
        match_info = self.api_client.get_first_match_of_matchday(
            self.config.league_id
        )
        
        if not match_info:
            print("No matches found")
            return
        
        print(f"First match of matchday: {match_info}")

        # Check if match has actually started or finished
        # Valid statuses for upcoming matches: SCHEDULED, TIMED, LIVE
        if match_info["status"] not in ['SCHEDULED', 'TIMED']:
            print(f"Match already started or finished, skipping notifications")
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
                print(f"Sending to {chat_id}")
                asyncio.run(self.send_notification(chat_id, match_info))
            else:
                print(f"Not time yet for {chat_id}: {now} < {notification_time}")
    
    def run(self):
        self.check_and_schedule()
        schedule.every().day.at(self.config.check_time).do(
            self.check_and_schedule
        )
        
        print(f"Scheduler started at {self.config.check_time}")
        while True:
            schedule.run_pending()
            time.sleep(60)
