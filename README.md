# Fantafootball Notifications

A lightweight Telegram bot that notifies subscribed users about upcoming Serie A matchdays.

Purpose: send timely reminders so users can set their fantasy football lineups before kickoff.

Features:
- Send per-user reminders ahead of the next matchday.
- Per-user settings (notification hours) persisted in `data/users.json`.
- Simple scheduler that checks the API and notifies active subscribers.

## Running Locally

1. Create a `.env` file in the project root with your credentials:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
API_FOOTBALL_KEY=your_api_key_here
```

2. Copy `config.example.json` to `data/config.json` and adjust settings as needed. Default values are:

```json
{
  "league_id": "SA",
  "default_hours_before": 24
}
```

3. Install dependencies and run:

```bash
pip install -r requirements.txt
python -m src.main
```

## Running with Docker

1. Build the image:

```bash
docker build -t fantabot .
```

2. Run the container, passing credentials as environment variables and mounting a volume for persistent storage:

```bash
docker run -e TELEGRAM_BOT_TOKEN=your_token \
           -e API_FOOTBALL_KEY=your_key \
           -v $(pwd)/data:/app/data \
           fantabot
```

The `/app/data` volume keeps `users.json` and `config.json` persistent across container restarts. Make sure `data/config.json` exists on the host before starting the container.

---

Configuration:
- Sensitive credentials (`TELEGRAM_BOT_TOKEN`, `API_FOOTBALL_KEY`) must be set as environment variables
- Non-sensitive settings are stored in `data/config.json`
- API currently used is [football-data.org](https://www.football-data.org/). Access may be limited on free plans.
