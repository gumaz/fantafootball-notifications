class Translations:
    def __init__(self):
        self.translations = {
            "en": {
                "bot_cannot_subscribe": "Bots cannot subscribe to this service.",
                "welcome_back": "✅ Welcome back! You've been re-subscribed and will receive notifications again.",
                "already_subscribed": "You're already subscribed!",
                "welcome_new_user": (
                    "✅ Welcome to Serie A Fantasy Reminder!\n\n"
                    "You'll receive notifications 24 hours before each matchday.\n\n"
                    "Commands:\n"
                    "/sethours <hours> - Set notification time (e.g., /sethours 48)\n"
                    "/status - Check your settings\n"
                    "/stop - Unsubscribe"
                ),
                "notification_set": "✅ Notification set to {hours} hours before kickoff.",
                "use_start_first": "Please use /start first!",
                "invalid_hours_range": "Please choose between 1-24 hours.",
                "invalid_hours_format": "Usage: /sethours <number>\nExample: /sethours 48",
                "status": "📊 Your Settings:\nStatus: {status}\nReminder: {hours} hours before kickoff",
                "status_active": "Active ✅",
                "status_inactive": "Inactive ❌",
                "unsubscribed": "😔 You've been unsubscribed. Use /start to resubscribe anytime.",
                "not_subscribed": "You're not subscribed. Use /start to begin!",
                "no_more_reminders": "✅ Got it! No more reminders for this matchday.",
            },
            "it": {
                "bot_cannot_subscribe": "I bot non possono iscriversi a questo servizio.",
                "welcome_back": "✅ Bentornato! Ti sei reiscritto e riceverai nuovamente le notifiche.",
                "already_subscribed": "Sei già iscritto!",
                "welcome_new_user": (
                    "✅ Benvenuto dal Bot delle notifiche per il tuo Fantacalcio!\n\n"
                    "Riceverai notifiche 24 ore prima di ogni giornata per ricordarti di inserire la tua formazione.\n\n"
                    "Comandi:\n"
                    "/sethours <ore> - Scegli quante ore prima ricevere la notifica (es. /sethours 48)\n"
                    "/status - Controlla le tue impostazioni\n"
                    "/stop - Disiscriviti"
                ),
                "notification_set": "✅ Notifica impostata per {hours} ore prima dell'incontro.",
                "use_start_first": "Usa /start per iniziare!",
                "invalid_hours_range": "Seleziona un numero compreso tra 1 e 24 ore.",
                "invalid_hours_format": "Uso: /sethours <numero>\nEsempio: /sethours 48",
                "status": "📊 Le Tue Impostazioni:\nStato: {status}\nPromemoria: {hours} ore prima dello scontro",
                "status_active": "Attivo ✅",
                "status_inactive": "Inattivo ❌",
                "unsubscribed": "😔 Ti sei disiscritto. Usa /start per iscriverti nuovamente.",
                "not_subscribed": "Non sei iscritto. Usa /start per iniziare!",
                "no_more_reminders": "✅ Ok! Non riceverai più promemoria per questa giornata.",
            },
        }

    def get(self, lang_code, key):
        return self.translations.get(lang_code, self.translations["en"])[key]


# Singleton instance
translations = Translations()
