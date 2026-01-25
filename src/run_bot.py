import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bot import FantasyBot
from src.config import Config

def main():
    config = Config()
    bot = FantasyBot(config.telegram_token)
    bot.run()

if __name__ == '__main__':
    main()