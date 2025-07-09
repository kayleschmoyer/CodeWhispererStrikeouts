from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from scraper import MLBScraper

app = FastAPI(title="MLB Strikeout Predictions API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Batter(BaseModel):
    name: str
    k_rate: float
    handedness: str
    vs_pitcher_history: int

class PitcherStats(BaseModel):
    k9: float
    k_percent: float
    whiff_rate: float
    swing_strike_rate: float
    era: float
    whip: float

class Projection(BaseModel):
    projected_strikeouts: float
    confidence: int
    betting_line: str

class Pitcher(BaseModel):
    name: str
    team: str
    handedness: str
    stats: PitcherStats
    projection: Projection

class Game(BaseModel):
    id: int
    home_team: Dict[str, str]
    away_team: Dict[str, str]
    game_time: str
    home_pitcher: Pitcher
    away_pitcher: Pitcher
    team_stats: Dict[str, Dict[str, float]]
    expected_batters: List[Batter]

scraper = MLBScraper()

@app.get("/")
async def root():
    return {"message": "MLB Strikeout Predictions API", "version": "1.0.0"}

@app.get("/api/games/today", response_model=List[Game])
async def get_todays_games():
    """Get today's MLB games with strikeout predictions"""
    try:
        # Get today's games
        games_data = scraper.get_todays_games()
        
        if not games_data:
            # Return mock data if scraping fails
            return get_mock_games()
        
        games = []
        
        for idx, game_data in enumerate(games_data[:5]):  # Limit to 5 games to avoid rate limits
            try:
                # Get pitcher names (would need more sophisticated scraping for real pitcher names)
                home_pitcher_name = get_probable_pitcher(game_data['home_team'])
                away_pitcher_name = get_probable_pitcher(game_data['away_team'])
                
                # Get pitcher stats
                home_pitcher_stats = scraper.get_pitcher_stats(home_pitcher_name, game_data['home_team'])
                away_pitcher_stats = scraper.get_pitcher_stats(away_pitcher_name, game_data['away_team'])
                
                # Get team strikeout rates
                home_vs_rhp = scraper.get_team_vs_handedness_stats(game_data['home_team'], 'R')
                home_vs_lhp = scraper.get_team_vs_handedness_stats(game_data['home_team'], 'L')
                away_vs_rhp = scraper.get_team_vs_handedness_stats(game_data['away_team'], 'R')
                away_vs_lhp = scraper.get_team_vs_handedness_stats(game_data['away_team'], 'L')
                
                # Get expected batters
                home_batters = scraper.get_expected_batters(game_data['home_team'])
                away_batters = scraper.get_expected_batters(game_data['away_team'])
                
                # Calculate projections
                home_team_k_rate = away_vs_rhp if home_pitcher_stats['handedness'] == 'R' else away_vs_lhp
                away_team_k_rate = home_vs_rhp if away_pitcher_stats['handedness'] == 'R' else home_vs_lhp
                
                home_projection = scraper.calculate_strikeout_projection(
                    home_pitcher_stats, home_team_k_rate, away_batters
                )
                away_projection = scraper.calculate_strikeout_projection(
                    away_pitcher_stats, away_team_k_rate, home_batters
                )
                
                game = Game(
                    id=idx + 1,
                    home_team={
                        "name": game_data['home_team'],
                        "abbr": scraper._get_team_abbr(game_data['home_team']).upper(),
                        "logo": "⚾"
                    },
                    away_team={
                        "name": game_data['away_team'],
                        "abbr": scraper._get_team_abbr(game_data['away_team']).upper(),
                        "logo": "⚾"
                    },
                    game_time=game_data['game_time'],
                    home_pitcher=Pitcher(
                        name=home_pitcher_name,
                        team=game_data['home_team'],
                        handedness=home_pitcher_stats['handedness'],
                        stats=PitcherStats(**{k: v for k, v in home_pitcher_stats.items() if k != 'handedness'}),
                        projection=Projection(**home_projection)
                    ),
                    away_pitcher=Pitcher(
                        name=away_pitcher_name,
                        team=game_data['away_team'],
                        handedness=away_pitcher_stats['handedness'],
                        stats=PitcherStats(**{k: v for k, v in away_pitcher_stats.items() if k != 'handedness'}),
                        projection=Projection(**away_projection)
                    ),
                    team_stats={
                        "home": {"vsRHP": home_vs_rhp, "vsLHP": home_vs_lhp},
                        "away": {"vsRHP": away_vs_rhp, "vsLHP": away_vs_lhp}
                    },
                    expected_batters=[Batter(**batter) for batter in (home_batters + away_batters)[:8]]
                )
                
                games.append(game)
                
            except Exception as e:
                print(f"Error processing game {idx}: {e}")
                continue
        
        return games if games else get_mock_games()
        
    except Exception as e:
        print(f"Error in get_todays_games: {e}")
        return get_mock_games()

def get_probable_pitcher(team: str) -> str:
    """Get probable starting pitcher - would need more sophisticated scraping"""
    # Mock pitcher names for demonstration
    pitcher_map = {
        'Yankees': 'Gerrit Cole',
        'Red Sox': 'Chris Sale',
        'Dodgers': 'Walker Buehler',
        'Padres': 'Yu Darvish',
        'Astros': 'Framber Valdez',
        'Angels': 'Shohei Ohtani',
        'Giants': 'Logan Webb',
        'Athletics': 'Paul Blackburn',
        'Mariners': 'Logan Gilbert',
        'Rangers': 'Nathan Eovaldi'
    }
    return pitcher_map.get(team, f"{team} Starter")

def get_mock_games() -> List[Game]:
    """Return mock games if scraping fails"""
    return [
        Game(
            id=1,
            home_team={"name": "Yankees", "abbr": "NYY", "logo": "⚾"},
            away_team={"name": "Red Sox", "abbr": "BOS", "logo": "⚾"},
            game_time="7:05 PM ET",
            home_pitcher=Pitcher(
                name="Gerrit Cole",
                team="Yankees",
                handedness="R",
                stats=PitcherStats(k9=11.2, k_percent=28.5, whiff_rate=32.1, swing_strike_rate=14.8, era=3.20, whip=1.15),
                projection=Projection(projected_strikeouts=8.5, confidence=78, betting_line="Over 7.5")
            ),
            away_pitcher=Pitcher(
                name="Chris Sale",
                team="Red Sox",
                handedness="L",
                stats=PitcherStats(k9=12.1, k_percent=31.2, whiff_rate=35.4, swing_strike_rate=16.2, era=2.90, whip=1.05),
                projection=Projection(projected_strikeouts=9.2, confidence=82, betting_line="Over 8.5")
            ),
            team_stats={
                "home": {"vsRHP": 22.1, "vsLHP": 24.8},
                "away": {"vsRHP": 23.4, "vsLHP": 21.9}
            },
            expected_batters=[
                Batter(name="Rafael Devers", k_rate=18.5, handedness="L", vs_pitcher_history=3),
                Batter(name="Xander Bogaerts", k_rate=15.2, handedness="R", vs_pitcher_history=1),
                Batter(name="J.D. Martinez", k_rate=24.1, handedness="R", vs_pitcher_history=5),
                Batter(name="Alex Verdugo", k_rate=19.8, handedness="L", vs_pitcher_history=2),
                Batter(name="Aaron Judge", k_rate=28.2, handedness="R", vs_pitcher_history=4),
                Batter(name="Anthony Rizzo", k_rate=22.1, handedness="L", vs_pitcher_history=2),
                Batter(name="Gleyber Torres", k_rate=20.5, handedness="R", vs_pitcher_history=3),
                Batter(name="Giancarlo Stanton", k_rate=31.8, handedness="R", vs_pitcher_history=6)
            ]
        )
    ]

@app.get("/api/pitcher/{pitcher_name}")
async def get_pitcher_stats(pitcher_name: str):
    """Get detailed stats for a specific pitcher"""
    try:
        stats = scraper.get_pitcher_stats(pitcher_name, "")
        return {"pitcher": pitcher_name, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Pitcher not found: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)