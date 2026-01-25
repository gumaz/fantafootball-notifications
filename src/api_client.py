import requests

class FootballDataAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": api_key}
    
    def get_next_matchday(self, league_id):
        endpoint = f"{self.base_url}/competitions/{league_id}/matches"
        params = {
            "status": "SCHEDULED"
        }
        
        try:
            response = requests.get(
                endpoint, 
                headers=self.headers, 
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            matches = data.get("matches", [])
            print(f"Found {len(matches)} scheduled matches")

            if not matches:
                print(f"No scheduled matches found. League ID: {league_id}")
                return None
            
            matches.sort(key=lambda m: m["utcDate"])
            first = matches[0]
            
            return {
                "date": first["utcDate"],
                "round": first.get("matchday", "Matchday N/A"),
                "home": first["homeTeam"]["name"],
                "away": first["awayTeam"]["name"]
            }
        except Exception as e:
            print(f"Error: {e}")
            return None