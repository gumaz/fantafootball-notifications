# Fantafootball Notifications

A lightweight Telegram bot that notifies subscribed users about upcoming Serie A matchdays.

Purpose: send timely reminders so users can set their fantasy football lineups before kickoff.

Features:
- Send per-user reminders ahead of the next matchday.
- Per-user settings (notification hours) persisted in `data/users.json`.
- Simple scheduler that checks the API and notifies active subscribers.

Quick start:
1. Provide your Telegram bot token and API-Football key (football-data.org) via your configuration.
2. Run the service locally to see it in action:

```bash
python -m src.main
```

Notes:
- API currently used is [football-data.org](https://www.football-data.org/). Access may be limited on free plans.
