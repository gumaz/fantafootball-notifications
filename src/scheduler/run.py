import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scheduler import MatchdayScheduler
from src.config import Config

def main():
    config = Config()
    scheduler = MatchdayScheduler(config)
    scheduler.run()

if __name__ == '__main__':
    main()
