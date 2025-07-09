import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from typing import Dict, List


class MLBScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.last_request = 0

    def _throttle(self):
        elapsed = time.time() - self.last_request
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self.last_request = time.time()

    def _normalize_team_name(self, name: str) -> str:
        name = name.replace("Chi", "Chicago")
        name = name.replace("Chicagocago", "Chicago")
        name = name.replace("NY", "New York")
        name = name.replace("LA", "Los Angeles")
        name = name.replace("SF", "San Francisco")
        name = name.replace("SD", "San Diego")
        name = name.replace("TB", "Tampa Bay")
        name = name.replace("KC", "Kansas City")
        name = name.replace("WSH", "Washington")
        name = name.replace("AZ", "Arizona")
        return name.strip()

    def get_mlb_pitchers(self) -> Dict[str, str]:
        today = datetime.now().strftime('%Y-%m-%d')
        url = f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}&hydrate=probablePitcher'
        try:
            response = self.session.get(url, timeout=5)
            data = response.json()
            pitchers = {}

            if 'dates' in data and data['dates']:
                for game in data['dates'][0]['games']:
                    home_team = game['teams']['home']['team']['name']
                    away_team = game['teams']['away']['team']['name']
                    if 'probablePitcher' in game['teams']['home']:
                        pitchers[home_team] = game['teams']['home']['probablePitcher']['fullName']
                    if 'probablePitcher' in game['teams']['away']:
                        pitchers[away_team] = game['teams']['away']['probablePitcher']['fullName']
            print(f"✅ Found {len(pitchers)} probable pitchers")
            for team, pitcher in pitchers.items():
                print(f"  {team}: {pitcher}")
            return pitchers
        except Exception as e:
            print(f"❌ Error getting MLB pitchers: {e}")
            return {}

    def get_todays_games(self) -> List[Dict]:
        today = datetime.now()
        today_str = today.strftime("%Y%m%d")
        url = f"https://www.espn.com/mlb/schedule/_/date/{today_str}"

        try:
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            pitchers = self.get_mlb_pitchers()

            schedule_blocks = soup.find_all("div", class_="ResponsiveTable")
            games = []
            day_str = str(today.day)
            today_date = today.strftime(f"%A, %B {day_str}, %Y")

            for block in schedule_blocks:
                title = block.find("div", class_="Table__Title")
                if not title or today_date not in title.get_text(strip=True):
                    continue

                team_links = block.select('a.AnchorLink[href^="/mlb/team/"]')
                team_names = [a.get_text(strip=True) for a in team_links if a.get_text(strip=True)]

                for i in range(0, len(team_names), 2):
                    try:
                        away_team = self._normalize_team_name(team_names[i])
                        home_team = self._normalize_team_name(team_names[i + 1])

                        away_pitcher = pitchers.get(away_team, "TBD")
                        home_pitcher = pitchers.get(home_team, "TBD")

                        games.append({
                            'away_team': away_team,
                            'home_team': home_team,
                            'game_time': '7:00 PM ET',
                            'away_pitcher': away_pitcher,
                            'home_pitcher': home_pitcher
                        })
                    except IndexError:
                        continue
                break

            print(f"✅ Found {len(games)} games for today")
            return games

        except Exception as e:
            print(f"❌ Error scraping ESPN: {e}")
            return []

    def get_pitcher_stats(self, pitcher_name: str, team: str) -> Dict:
        # TEMP fallback to avoid hanging
        print(f"⏳ Skipping real scrape. Returning defaults for: {pitcher_name}")
        return self._default_pitcher_stats()

        # UNCOMMENT THIS if you want full scraping once stable:
        """
        self._throttle()
        print(f"🔍 Getting stats for {pitcher_name} ({team})")
        search_url = f'https://www.baseball-reference.com/search/search.fcgi?search={pitcher_name.replace(" ", "+")}'
        try:
            response = self.session.get(search_url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            search_results = soup.find('div', class_='search-results')
            if not search_results:
                return self._default_pitcher_stats()
            pitcher_link = search_results.find('a')
            if not pitcher_link:
                return self._default_pitcher_stats()
            pitcher_url = 'https://www.baseball-reference.com' + pitcher_link['href']
            self._throttle()
            response = self.session.get(pitcher_url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            stats_table = soup.find('table', {'id': 'pitching_standard'})
            if not stats_table:
                return self._default_pitcher_stats()
            current_year = str(datetime.now().year)
            current_row = None
            for row in stats_table.find_all('tr'):
                year_cell = row.find('th')
                if year_cell and current_year in year_cell.text:
                    current_row = row
                    break
            if not current_row:
                return self._default_pitcher_stats()
            cells = current_row.find_all('td')
            era = self._safe_float(cells[3].text if len(cells) > 3 else '4.50')
            whip = self._safe_float(cells[4].text if len(cells) > 4 else '1.30')
            so = self._safe_int(cells[8].text if len(cells) > 8 else '150')
            ip = self._safe_float(cells[5].text if len(cells) > 5 else '150.0')
            k9 = (so / ip) * 9 if ip > 0 else 8.5
            k_percent = min(35.0, k9 * 2.5)
            whiff_rate = min(40.0, k_percent * 1.1)
            swing_strike_rate = min(20.0, whiff_rate * 0.4)
            return {
                'k9': round(k9, 1),
                'k_percent': round(k_percent, 1),
                'whiff_rate': round(whiff_rate, 1),
                'swing_strike_rate': round(swing_strike_rate, 1),
                'era': era,
                'whip': whip,
                'handedness': self._get_pitcher_handedness(soup)
            }
        except Exception as e:
            print(f"Error getting pitcher stats for {pitcher_name}: {e}")
            return self._default_pitcher_stats()
        """

    def _safe_float(self, value: str) -> float:
        try:
            return float(value.replace(',', ''))
        except:
            return 0.0

    def _safe_int(self, value: str) -> int:
        try:
            return int(value.replace(',', ''))
        except:
            return 0

    def _get_pitcher_handedness(self, soup) -> str:
        bio_section = soup.find('div', {'id': 'meta'})
        if bio_section and 'Left' in bio_section.text:
            return 'L'
        return 'R'

    def _default_pitcher_stats(self) -> Dict:
        return {
            'k9': 8.5,
            'k_percent': 22.0,
            'whiff_rate': 25.0,
            'swing_strike_rate': 12.0,
            'era': 4.50,
            'whip': 1.30,
            'handedness': 'R'
        }

    def _default_batters(self) -> List[Dict]:
        return [
            {'name': f'Batter {i+1}', 'k_rate': 22.5, 'handedness': 'R', 'vs_pitcher_history': 1}
            for i in range(8)
        ]

    def _get_probable_pitcher(self, team: str) -> str:
        return "TBD"

    def _get_batters_for_team(self, pitcher_name: str, team: str) -> List[Dict]:
        return [
            {'name': f'{team} Batter {i+1}', 'k_rate': 22.5, 'handedness': 'R', 'vs_pitcher_history': 1}
            for i in range(8)
        ]

    def _get_team_abbr(self, team_name: str) -> str:
        abbr_map = {
            'Arizona': 'ARI', 'Atlanta': 'ATL', 'Baltimore': 'BAL', 'Boston': 'BOS',
            'Chicago Cubs': 'CHC', 'Chicago White Sox': 'CWS', 'Cincinnati': 'CIN',
            'Cleveland': 'CLE', 'Colorado': 'COL', 'Detroit': 'DET', 'Houston': 'HOU',
            'Kansas City': 'KC', 'Los Angeles Angels': 'LAA', 'Los Angeles Dodgers': 'LAD',
            'Miami': 'MIA', 'Milwaukee': 'MIL', 'Minnesota': 'MIN', 'New York Mets': 'NYM',
            'New York Yankees': 'NYY', 'Oakland': 'OAK', 'Philadelphia': 'PHI',
            'Pittsburgh': 'PIT', 'San Diego': 'SD', 'San Francisco': 'SF',
            'Seattle': 'SEA', 'St. Louis': 'STL', 'Tampa Bay': 'TB', 'Texas': 'TEX',
            'Toronto': 'TOR', 'Washington': 'WSH'
        }
        for full_name, abbr in abbr_map.items():
            if full_name.lower() in team_name.lower():
                return abbr
        return team_name[:3].upper()

    def _teams_match(self, mlb_team: str, espn_team: str) -> bool:
        # Normalize both team names
        mlb_lower = mlb_team.lower()
        espn_lower = espn_team.lower()
        
        # Direct match
        if mlb_lower == espn_lower:
            return True
            
        # Check key words match
        mlb_words = set(mlb_lower.split())
        espn_words = set(espn_lower.split())
        
        # Remove common words
        common_words = {'the', 'of', 'and', 'at'}
        mlb_words -= common_words
        espn_words -= common_words
        
        # Must have at least 2 matching words or 1 unique identifier
        unique_identifiers = {'yankees', 'mets', 'dodgers', 'angels', 'giants', 'athletics', 'padres', 'cubs', 'sox'}
        
        intersection = mlb_words & espn_words
        if len(intersection) >= 2 or any(word in unique_identifiers for word in intersection):
            return True
            
        return False
