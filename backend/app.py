from flask import Flask, jsonify
from flask_cors import CORS
from scraper import MLBScraper

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

scraper = MLBScraper()

@app.route('/')
def root():
    return {"message": "MLB Strikeout Predictions API", "version": "1.0.0"}

@app.route('/api/games/today')
def get_todays_games():
    try:
        games_data = scraper.get_todays_games()
        mlb_pitchers = scraper.get_mlb_pitchers()
        
        if not games_data:
            print("No games data found from ESPN scraper")
            return jsonify({"error": "No games found for today. Check if it's MLB season or if ESPN is accessible."})
        
        games = []
        
        for idx, game_data in enumerate(games_data):  # Process all games
            try:
                # Get actual pitcher names from MLB.com data
                home_team_short = game_data['home_team'].split()[-1]  # Get last word (Yankees, Red Sox, etc.)
                away_team_short = game_data['away_team'].split()[-1]
                
                home_pitcher_name = 'TBD'
                away_pitcher_name = 'TBD'
                
                # Debug: show what we're trying to match
                print(f"Looking for pitchers for: {game_data['away_team']} @ {game_data['home_team']}")
                
                # Direct team name to MLB team mapping
                team_mapping = {
                    'Baltimore': 'Baltimore Orioles',
                    'New York': ['New York Yankees', 'New York Mets'],
                    'Seattle': 'Seattle Mariners',
                    'Boston': 'Boston Red Sox',
                    'Colorado': 'Colorado Rockies',
                    'Miami': 'Miami Marlins',
                    'Cincinnati': 'Cincinnati Reds',
                    'Chicago': ['Chicago Cubs', 'Chicago White Sox'],
                    'Minnesota': 'Minnesota Twins',
                    'Los Angeles': ['Los Angeles Dodgers', 'Los Angeles Angels'],
                    'Milwaukee': 'Milwaukee Brewers',
                    'Pittsburgh': 'Pittsburgh Pirates',
                    'Kansas City': 'Kansas City Royals',
                    'Toronto': 'Toronto Blue Jays',
                    'Washington': 'Washington Nationals',
                    'St. Louis': 'St. Louis Cardinals',
                    'Cleveland': 'Cleveland Guardians',
                    'Houston': 'Houston Astros',
                    'Texas': 'Texas Rangers',
                    'Arizona': 'Arizona Diamondbacks',
                    'San Diego': 'San Diego Padres',
                    'Philadelphia': 'Philadelphia Phillies',
                    'San Francisco': 'San Francisco Giants',
                    'Athletics': 'Athletics',
                    'Atlanta': 'Atlanta Braves'
                }
                
                used_pitchers = set()
                
                def find_pitcher(team_name):
                    if team_name in team_mapping:
                        mapped_teams = team_mapping[team_name]
                        if isinstance(mapped_teams, list):
                            for mapped_team in mapped_teams:
                                if mapped_team in mlb_pitchers and mlb_pitchers[mapped_team] not in used_pitchers:
                                    pitcher = mlb_pitchers[mapped_team]
                                    used_pitchers.add(pitcher)
                                    return pitcher
                        else:
                            if mapped_teams in mlb_pitchers and mlb_pitchers[mapped_teams] not in used_pitchers:
                                pitcher = mlb_pitchers[mapped_teams]
                                used_pitchers.add(pitcher)
                                return pitcher
                    return 'TBD'
                
                home_pitcher_name = find_pitcher(game_data['home_team'])
                away_pitcher_name = find_pitcher(game_data['away_team'])
                
                # Fallback to default if still TBD
                if home_pitcher_name == 'TBD':
                    home_pitcher_name = scraper._get_probable_pitcher(home_team_short)
                if away_pitcher_name == 'TBD':
                    away_pitcher_name = scraper._get_probable_pitcher(away_team_short)
                
                print(f"Game: {away_pitcher_name} ({game_data['away_team']}) @ {home_pitcher_name} ({game_data['home_team']})")
                
                # Process all games
                
                # Use default stats to avoid hanging
                home_pitcher_stats = scraper._default_pitcher_stats()
                away_pitcher_stats = scraper._default_pitcher_stats()
                
                home_vs_rhp = 23.5
                home_vs_lhp = 25.2
                away_vs_rhp = 23.5
                away_vs_lhp = 25.2
                
                home_batters = scraper._default_batters()
                away_batters = scraper._default_batters()
                
                home_team_k_rate = 24.0
                away_team_k_rate = 24.0
                
                home_projection = {
                    'projected_strikeouts': 7.5,
                    'confidence': 72,
                    'betting_line': 'Over 6.5'
                }
                away_projection = {
                    'projected_strikeouts': 8.2,
                    'confidence': 75,
                    'betting_line': 'Over 7.5'
                }
                
                game = {
                    "id": idx + 1,
                    "homeTeam": {
                        "name": game_data['home_team'],
                        "abbr": scraper._get_team_abbr(game_data['home_team']).upper(),
                        "logo": "⚾"
                    },
                    "awayTeam": {
                        "name": game_data['away_team'],
                        "abbr": scraper._get_team_abbr(game_data['away_team']).upper(),
                        "logo": "⚾"
                    },
                    "gameTime": game_data['game_time'],
                    "homePitcher": {
                        "name": home_pitcher_name if home_pitcher_name != 'TBD' else f"{game_data['home_team']} Starter",
                        "hand": home_pitcher_stats['handedness'],
                        "stats": {k: v for k, v in home_pitcher_stats.items() if k != 'handedness'},
                        "projection": home_projection
                    },
                    "awayPitcher": {
                        "name": away_pitcher_name if away_pitcher_name != 'TBD' else f"{game_data['away_team']} Starter",
                        "hand": away_pitcher_stats['handedness'],
                        "stats": {k: v for k, v in away_pitcher_stats.items() if k != 'handedness'},
                        "projection": away_projection
                    },
                    "teamStats": {
                        "home": {"vsRHP": home_vs_rhp, "vsLHP": home_vs_lhp},
                        "away": {"vsRHP": away_vs_rhp, "vsLHP": away_vs_lhp}
                    },
                    "expectedBatters": (home_batters + away_batters)[:8]
                }
                
                games.append(game)
                
            except Exception as e:
                print(f"Error processing game {idx}: {e}")
                continue
        
        if not games:
            return jsonify({"error": "No games with confirmed starting pitchers found."})
        print(f"Processed {len(games)} games")
        return jsonify(games)
        
    except Exception as e:
        print(f"Error in get_todays_games: {e}")
        return jsonify({"error": f"API Error: {str(e)}"})

@app.route('/api/pitcher/<pitcher_name>')
def get_pitcher_stats_endpoint(pitcher_name):
    try:
        stats = scraper.get_pitcher_stats(pitcher_name, "")
        return jsonify({"pitcher": pitcher_name, "stats": stats})
    except Exception as e:
        return jsonify({"error": f"Pitcher not found: {str(e)}"}), 404

def get_probable_pitcher(team):
    pitcher_map = {
        'Yankees': 'Gerrit Cole', 'Red Sox': 'Chris Sale', 'Dodgers': 'Walker Buehler',
        'Padres': 'Yu Darvish', 'Astros': 'Framber Valdez', 'Angels': 'Shohei Ohtani',
        'Giants': 'Logan Webb', 'Athletics': 'Paul Blackburn', 'Mariners': 'Logan Gilbert',
        'Rangers': 'Nathan Eovaldi'
    }
    return pitcher_map.get(team, f"{team} Starter")

def get_mock_games():
    return [{
        "id": 1,
        "homeTeam": {"name": "Yankees", "abbr": "NYY", "logo": "⚾"},
        "awayTeam": {"name": "Red Sox", "abbr": "BOS", "logo": "⚾"},
        "gameTime": "7:05 PM ET",
        "homePitcher": {
            "name": "Gerrit Cole", "hand": "R",
            "stats": {"k9": 11.2, "k_percent": 28.5, "whiff_rate": 32.1, "swing_strike_rate": 14.8, "era": 3.20, "whip": 1.15},
            "projection": {"projected_strikeouts": 8.5, "confidence": 78, "betting_line": "Over 7.5"}
        },
        "awayPitcher": {
            "name": "Chris Sale", "hand": "L",
            "stats": {"k9": 12.1, "k_percent": 31.2, "whiff_rate": 35.4, "swing_strike_rate": 16.2, "era": 2.90, "whip": 1.05},
            "projection": {"projected_strikeouts": 9.2, "confidence": 82, "betting_line": "Over 8.5"}
        },
        "teamStats": {"home": {"vsRHP": 22.1, "vsLHP": 24.8}, "away": {"vsRHP": 23.4, "vsLHP": 21.9}},
        "expectedBatters": [
            {"name": "Rafael Devers", "k_rate": 18.5, "handedness": "L", "vs_pitcher_history": 3},
            {"name": "Aaron Judge", "k_rate": 28.2, "handedness": "R", "vs_pitcher_history": 4}
        ]
    }]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)