import requests
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class FootballDataAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": api_key}
    
    def get_first_match_of_matchday(self, league_id):
        """
        Get the first match of the next upcoming matchday.
        
        Finds the next matchday with future matches and returns the first match
        of that matchday (even if it has already been played). The scheduler will
        handle notifications based on current time.

        Args:
            league_id (int): The ID of the league to fetch matches for.
        """
        endpoint = f"{self.base_url}/competitions/{league_id}/matches"
        
        try:
            response = requests.get(
                endpoint, 
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            matches = data.get("matches", [])
            logger.info(f"Found {len(matches)} scheduled matches")

            if not matches:
                logger.warning(f"No scheduled matches found. League ID: {league_id}")
                return None
            
            now = datetime.now(timezone.utc)
            future_matches = [
                m for m in matches 
                if datetime.fromisoformat(m["utcDate"].replace('Z', '+00:00')) > now
            ]
            
            if not future_matches:
                logger.warning("No future matches found")
                return None
            
            future_matches.sort(key=lambda m: m["utcDate"])
            next_matchday = future_matches[0].get("matchday")
            
            all_matchday_matches = [
                m for m in matches 
                if m.get("matchday") == next_matchday
            ]
            all_matchday_matches.sort(key=lambda m: m["utcDate"])
            
            match = all_matchday_matches[0]
            
            return {
                "date": match["utcDate"],
                "round": match.get("matchday", "Matchday N/A"),
                "home": match["homeTeam"]["shortName"],
                "away": match["awayTeam"]["shortName"],
                "status": match["status"]
            }
        except Exception as e:
            logger.error(f"Error fetching matches: {e}")
            return None
