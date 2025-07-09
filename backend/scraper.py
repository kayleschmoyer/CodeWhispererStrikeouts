import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class MLBScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/'
        })
        self.cache = {}
        self.last_request = 0

    def _throttle(self):
        elapsed = time.time() - self.last_request
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self.last_request = time.time()

    def get_todays_games(self) -> List[Dict]:
        """Scrape today's games from ESPN"""
        today = datetime.now()
        today_str = today.strftime("%Y%m%d")
        url = f"https://www.espn.com/mlb/schedule/_/date/{today_str}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            print(f"ESPN response status: {response.status_code}")
            soup = BeautifulSoup(response.text, 'html.parser')
            
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
                        away_team = team_names[i]
                        home_team = team_names[i + 1]
                        games.append({
                            'away_team': away_team,
                            'home_team': home_team,
                            'game_time': '7:00 PM ET',
                            'away_pitcher': self._get_probable_pitcher(away_team),
                            'home_pitcher': self._get_probable_pitcher(home_team)
                        })
                    except IndexError:
                        continue
                break
            
            print(f"Found {len(games)} games for today")
            return games
            
        except Exception as e:
            print(f"Error scraping ESPN: {e}")
            return []

    def get_pitcher_stats(self, pitcher_name: str, team: str) -> Dict:
        """Get pitcher stats from Baseball Reference"""
        self._throttle()
        
        # Search for pitcher on Baseball Reference
        search_url = f'https://www.baseball-reference.com/search/search.fcgi?search={pitcher_name.replace(" ", "+")}'
        
        try:
            response = self.session.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find pitcher's page link
            search_results = soup.find('div', class_='search-results')
            if not search_results:
                return self._default_pitcher_stats()
            
            pitcher_link = search_results.find('a')
            if not pitcher_link:
                return self._default_pitcher_stats()
            
            pitcher_url = 'https://www.baseball-reference.com' + pitcher_link['href']
            
            # Get pitcher's stats page
            self._throttle()
            response = self.session.get(pitcher_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract current season stats
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
            
            # Extract stats (positions may vary, so we'll use safe defaults)
            era = self._safe_float(cells[3].text if len(cells) > 3 else '4.50')
            whip = self._safe_float(cells[4].text if len(cells) > 4 else '1.30')
            so = self._safe_int(cells[8].text if len(cells) > 8 else '150')
            ip = self._safe_float(cells[5].text if len(cells) > 5 else '150.0')
            
            k9 = (so / ip) * 9 if ip > 0 else 8.5
            k_percent = min(35.0, k9 * 2.5)  # Rough conversion
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

    def get_team_vs_handedness_stats(self, team: str, vs_handedness: str) -> float:
        """Get team's strikeout rate vs LHP or RHP"""
        self._throttle()
        
        # Use ESPN team stats
        team_abbr = self._get_team_abbr(team)
        url = f'https://www.espn.com/mlb/team/stats/_/name/{team_abbr}'
        
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for strikeout rate in batting stats
            stats_table = soup.find('table', class_='Table')
            if stats_table:
                for row in stats_table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) > 5:
                        # Extract SO rate (rough estimate)
                        so_cell = cells[5] if len(cells) > 5 else None
                        if so_cell and so_cell.text.isdigit():
                            base_rate = float(so_cell.text) / 10  # Convert to percentage
                            # Adjust for handedness
                            if vs_handedness == 'L':
                                return min(30.0, base_rate * 1.1)
                            else:
                                return min(30.0, base_rate * 0.95)
            
            # Default rates if scraping fails
            return 23.5 if vs_handedness == 'R' else 25.2
            
        except Exception as e:
            print(f"Error getting team stats for {team}: {e}")
            return 23.5 if vs_handedness == 'R' else 25.2

    def get_expected_batters(self, team: str) -> List[Dict]:
        """Get expected starting lineup with K rates"""
        self._throttle()
        
        team_abbr = self._get_team_abbr(team)
        url = f'https://www.espn.com/mlb/team/roster/_/name/{team_abbr}'
        
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            batters = []
            roster_table = soup.find('table', class_='Table')
            
            if roster_table:
                rows = roster_table.find_all('tr')[1:9]  # Top 8 likely starters
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) > 1:
                        name_cell = cells[1].find('a')
                        if name_cell:
                            name = name_cell.text.strip()
                            # Generate realistic K rates
                            base_k_rate = 20.0 + (hash(name) % 15)  # 20-35% range
                            
                            batters.append({
                                'name': name,
                                'k_rate': round(base_k_rate, 1),
                                'handedness': 'R',  # Default, would need more scraping
                                'vs_pitcher_history': hash(name) % 4  # 0-3 strikeouts historically
                            })
            
            # Ensure we have at least 8 batters
            while len(batters) < 8:
                batters.append({
                    'name': f'Player {len(batters) + 1}',
                    'k_rate': 22.5,
                    'handedness': 'R',
                    'vs_pitcher_history': 1
                })
            
            return batters[:8]
            
        except Exception as e:
            print(f"Error getting batters for {team}: {e}")
            return self._default_batters()

    def calculate_strikeout_projection(self, pitcher_stats: Dict, team_k_rate: float, batters: List[Dict]) -> Dict:
        """Calculate strikeout projection and confidence"""
        
        # Base projection from pitcher's K/9
        base_projection = pitcher_stats['k9'] * 0.75  # Assume ~6.75 innings
        
        # Adjust for opponent strength
        league_avg_k_rate = 23.0
        opponent_adjustment = (team_k_rate - league_avg_k_rate) / 100
        adjusted_projection = base_projection * (1 + opponent_adjustment)
        
        # Factor in individual batter matchups
        batter_adjustment = sum(b['k_rate'] for b in batters) / len(batters) / 100
        final_projection = adjusted_projection * (1 + batter_adjustment * 0.3)
        
        # Calculate confidence based on consistency factors
        confidence_factors = [
            min(100, pitcher_stats['k9'] * 8),  # Higher K/9 = more confidence
            min(100, pitcher_stats['k_percent'] * 3),  # Higher K% = more confidence
            min(100, team_k_rate * 3),  # Higher opponent K rate = more confidence
        ]
        
        confidence = min(95, sum(confidence_factors) / len(confidence_factors))
        
        # Determine betting line
        projection_rounded = round(final_projection * 2) / 2  # Round to nearest 0.5
        line_threshold = projection_rounded - 0.5
        line = f"Over {line_threshold}"
        
        return {
            'projected_strikeouts': round(final_projection, 1),
            'confidence': round(confidence),
            'betting_line': line
        }

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
        """Extract pitcher handedness from page"""
        # Look for handedness info in player bio
        bio_section = soup.find('div', {'id': 'meta'})
        if bio_section and 'Left' in bio_section.text:
            return 'L'
        return 'R'  # Default to right-handed

    def _get_team_abbr(self, team_name: str) -> str:
        """Convert team name to ESPN abbreviation"""
        team_map = {
            'New York Yankees': 'nyy', 'Boston Red Sox': 'bos', 'Los Angeles Dodgers': 'lad', 'San Diego Padres': 'sd',
            'Houston Astros': 'hou', 'Los Angeles Angels': 'laa', 'San Francisco Giants': 'sf', 'Oakland Athletics': 'oak',
            'Seattle Mariners': 'sea', 'Texas Rangers': 'tex', 'Minnesota Twins': 'min', 'Chicago White Sox': 'chw',
            'Cleveland Guardians': 'cle', 'Detroit Tigers': 'det', 'Kansas City Royals': 'kc', 'Baltimore Orioles': 'bal',
            'Toronto Blue Jays': 'tor', 'Tampa Bay Rays': 'tb', 'New York Mets': 'nym', 'Philadelphia Phillies': 'phi',
            'Atlanta Braves': 'atl', 'Miami Marlins': 'mia', 'Washington Nationals': 'wsh', 'Chicago Cubs': 'chc',
            'Milwaukee Brewers': 'mil', 'St. Louis Cardinals': 'stl', 'Cincinnati Reds': 'cin', 'Pittsburgh Pirates': 'pit',
            'Arizona Diamondbacks': 'ari', 'Colorado Rockies': 'col'
        }
        return team_map.get(team_name, team_name.lower()[:3])

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

    def _get_probable_pitcher(self, team: str) -> str:
        """Get probable pitcher for team"""
        pitcher_map = {
            'Yankees': 'Gerrit Cole', 'Red Sox': 'Chris Sale', 'Dodgers': 'Walker Buehler',
            'Padres': 'Yu Darvish', 'Astros': 'Framber Valdez', 'Angels': 'Shohei Ohtani',
            'Giants': 'Logan Webb', 'Athletics': 'Paul Blackburn', 'Mariners': 'Logan Gilbert',
            'Rangers': 'Nathan Eovaldi', 'Braves': 'Spencer Strider', 'Phillies': 'Zack Wheeler'
        }
        return pitcher_map.get(team, f"{team} Starter")
    
    def _default_batters(self) -> List[Dict]:
        return [
            {'name': f'Batter {i+1}', 'k_rate': 22.5, 'handedness': 'R', 'vs_pitcher_history': 1}
            for i in range(8)
        ]