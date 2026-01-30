import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv()

class Config:
    def __init__(self, config_path='data/config.json'):
        self.config_path = config_path
        self._ensure_data_dir()
        self.data = self._load_config()
    
    def _ensure_data_dir(self):
        Path('data').mkdir(exist_ok=True)
    
    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Config not found in {self.config_path}."
            )
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    @property
    def telegram_token(self):
        return os.getenv('TELEGRAM_BOT_TOKEN')
    
    @property
    def api_football_key(self):
        return os.getenv('API_FOOTBALL_KEY')
    
    @property
    def league_id(self):
        return self.data['league_id']
    
    @property
    def default_hours_before(self):
        return self.data.get('default_hours_before', 24)
    