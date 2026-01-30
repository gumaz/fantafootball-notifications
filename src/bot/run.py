import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from src.bot import FantasyBot
from src.config import Config

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    config = Config()
    bot = FantasyBot(config.telegram_token)
    bot.run()

if __name__ == '__main__':
    main()
