import json
import logging
import os
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes


class FantasyBot:
    def __init__(self, token, users_file="data/users.json"):
        """
        Initialize the FantasyBot instance.

        Args:
            token (str): Telegram bot token used to authenticate the bot.
            users_file (str): Path to the JSON file used to persist user settings.

        Side effects:
            - Ensures `data` directory exists.
            - Loads existing users from `users_file` into `self.users`.
        """
        self.token = token
        self.users_file = users_file
        # per-instance logger under "src" so we can enable/disable our package centrally
        self.logger = logging.getLogger(f"src.{self.__class__.__name__}")
        Path("data").mkdir(exist_ok=True)
        self.users = self.load_users()

    def load_users(self):
        """
        Load users from the JSON persistence file.

        Returns:
            dict: Mapping of `chat_id` -> user settings. Returns an empty dict
            if the file does not exist, is empty, or cannot be decoded.

        Side effects:
            - Prints a warning if the file is unreadable or invalid JSON.
        """
        if not os.path.exists(self.users_file):
            return {}

        try:
            with open(self.users_file, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.warning(f"Could not load users file: {e}")
            return {}

    def save_users(self):
        """
        Persist current `self.users` to the configured JSON file.

        Side effects:
            - Writes `self.users` to disk. Prints an error message if write fails.
        """
        try:
            with open(self.users_file, "w") as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving users: {e}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle the /start command for new users or re-subscription.

        Registers a new user or reactivates a previously inactive user subscription.
        Blocks bot accounts from registering. Extracts user information (username, first name)
        and initializes notification settings with a default 24-hour notification window.

        Args:
            update (Update): The update object containing user and chat information.
            context (ContextTypes.DEFAULT_TYPE): The context object for the handler.

        Side effects:
            - Prevents bot accounts from subscribing by replying with an error message.
            - Creates a new user entry in self.users with default settings if user is new.
            - Reactivates an existing user's subscription if they were previously inactive.
            - Persists user data to storage via self.save_users().
            - Sends welcome/re-subscription messages to the user.
        """
        chat_id = str(update.effective_chat.id)
        user = update.effective_user

        # Block bot accounts from registering
        if user and getattr(user, "is_bot", False):
            await update.message.reply_text("Bots cannot subscribe to this service.")
            return

        username = user.username if user and getattr(user, "username", None) else ""
        first_name = (
            user.first_name if user and getattr(user, "first_name", None) else ""
        )

        # If user exists, handle re-subscription when previously inactive
        if chat_id in self.users:
            if not self.users[chat_id].get("active", True):
                self.users[chat_id]["username"] = username
                self.users[chat_id]["first_name"] = first_name
                self.users[chat_id]["active"] = True
                self.users[chat_id]["registration_date"] = datetime.now().isoformat()
                self.save_users()
                await update.message.reply_text(
                    "✅ Welcome back! You've been re-subscribed and will receive notifications again."
                )
            else:
                await update.message.reply_text("You're already subscribed!")
            return

        # New user registration
        self.logger.info(f"Registering new user: {chat_id}, first_name: {first_name}")
        self.users[chat_id] = {
            "active": True,
            "hours_before": 24,
            "username": username,
            "first_name": first_name,
            "registration_date": datetime.now().isoformat(),
        }
        self.save_users()
        await update.message.reply_text(
            "✅ Welcome to Serie A Fantasy Reminder!\n\n"
            "You'll receive notifications 24 hours before each matchday.\n\n"
            "Commands:\n"
            "/sethours <hours> - Set notification time (e.g., /sethours 48)\n"
            "/status - Check your settings\n"
            "/stop - Unsubscribe"
        )

    async def set_hours(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle the `/sethours` command to change the user's notification window.

        Expects one integer argument (hours). Valid range is 1-24.

        Side effects:
            - Updates `self.users[chat_id]['hours_before']` and persists changes.
            - Sends a confirmation or usage/error message to the user.
        """
        chat_id = str(update.effective_chat.id)
        if chat_id not in self.users:
            await update.message.reply_text("Please use /start first!")
            return

        try:
            hours = int(context.args[0])
            if hours < 1 or hours > 24:
                await update.message.reply_text("Please choose between 1-24 hours")
                return

            self.users[chat_id]["hours_before"] = hours
            self.save_users()
            await update.message.reply_text(
                f"✅ Notification set to {hours} hours before kickoff"
            )
        except (IndexError, ValueError):
            await update.message.reply_text(
                "Usage: /sethours <number>\nExample: /sethours 48"
            )

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle the `/status` command to display the user's current settings.

        Sends a short summary containing whether the user is active and their
        configured `hours_before` reminder.
        """
        chat_id = str(update.effective_chat.id)
        if chat_id in self.users:
            hours = self.users[chat_id]["hours_before"]
            active = self.users[chat_id]["active"]
            status_text = "Active ✅" if active else "Inactive ❌"
            await update.message.reply_text(
                f"📊 Your Settings:\n"
                f"Status: {status_text}\n"
                f"Reminder: {hours} hours before kickoff"
            )
        else:
            await update.message.reply_text(
                "You're not subscribed. Use /start to begin!"
            )

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle the `/stop` command to unsubscribe a user.

        Side effects:
            - Marks the user as inactive (`active = False`) and persists the change.
            - Sends a confirmation message to the user.
        """
        chat_id = str(update.effective_chat.id)
        if chat_id in self.users:
            self.logger.info(f"Unsubscribing user: {chat_id}")
            self.users[chat_id]["active"] = False
            self.save_users()
            await update.message.reply_text(
                "😔 You've been unsubscribed. Use /start to resubscribe anytime."
            )
        else:
            await update.message.reply_text("You weren't subscribed.")

    async def handle_lineup_confirmed(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handles the confirmation of a lineup.

        This asynchronous method processes the confirmation of a specific lineup when a user interacts with a button.
        It updates the user's confirmed matches list and removes the button from the message.
        """
        query = update.callback_query
        await query.answer()  # dismisses the loading spinner on the button

        chat_id = str(query.message.chat_id)
        match_id = query.data.replace("lineup_set:", "")

        if chat_id in self.users:
            confirmed = self.users[chat_id].setdefault("confirmed_matches", [])
            if match_id not in confirmed:
                confirmed.append(match_id)
                self.save_users()
            await query.edit_message_reply_markup(
                reply_markup=None
            )  # remove the button
            await query.message.reply_text(
                "✅ Got it! No more reminders for this matchday."
            )

    def run(self):
        app = Application.builder().token(self.token).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("sethours", self.set_hours))
        app.add_handler(CommandHandler("status", self.status))
        app.add_handler(CommandHandler("stop", self.stop))
        app.add_handler(
            CallbackQueryHandler(self.handle_lineup_confirmed, pattern=r"^lineup_set:")
        )
        self.logger.info("Bot is running...")
        app.run_polling(stop_signals=None)
