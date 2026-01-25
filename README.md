# Fantafootball Notifications

A lightweight Telegram bot that notifies subscribed users about upcoming Serie A matchdays.

Purpose: send timely reminders so users can set their fantasy football lineups before kickoff.

Features:
- Send per-user reminders ahead of the next matchday.
- Per-user settings (notification hours) persisted in `data/users.json`.
- Simple scheduler that checks the API and notifies active subscribers.

Quick start:
1. Create a `.env` file in the project root with your credentials:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
API_FOOTBALL_KEY=your_api_key_here
```

2. Adjust settings as needed in `data/config.jsopn`:

```bash
"league_id": "SA", # Serie A
"default_hours_before": 24
```

3. Run the service locally to see it in action:

```bash
python -m src.main
```

Configuration:
- Sensitive credentials (`TELEGRAM_BOT_TOKEN`, `API_FOOTBALL_KEY`) must be set as environment variables
- Non-sensitive settings are stored in `data/config.json`
- API currently used is [football-data.org](https://www.football-data.org/). Access may be limited on free plans.

Environment Variables:
- **Local development**: Create `.env` file with your credentials
- **Production**: Set `TELEGRAM_BOT_TOKEN` and `API_FOOTBALL_KEY` in your deployment platform's environment configuration
