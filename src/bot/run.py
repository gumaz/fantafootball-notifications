import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from src.bot import FantasyBot
from src.config import Config

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# Enable our package logs at INFO; keep all third-party libs at WARNING by default
logging.getLogger('src').setLevel(logging.INFO)

def main():
    config = Config()
    bot = FantasyBot(config.telegram_token)
    bot.run()

if __name__ == '__main__':
    main()
