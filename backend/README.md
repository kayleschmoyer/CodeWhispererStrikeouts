# MLB Strikeout Predictions Backend

FastAPI backend that scrapes real MLB data and provides strikeout predictions.

## Features

- Scrapes today's games from ESPN
- Gets pitcher stats from Baseball Reference
- Calculates team strikeout rates vs handedness
- Provides expected batting lineups with K rates
- Generates strikeout projections with confidence scores

## Setup

```bash
cd backend
pip install -r requirements.txt
python run.py
```

## API Endpoints

- `GET /api/games/today` - Get today's games with predictions
- `GET /api/pitcher/{name}` - Get specific pitcher stats
- `GET /` - API info

## Data Sources

- **ESPN**: Game schedules and team rosters
- **Baseball Reference**: Pitcher statistics and advanced metrics
- **Smart scraping**: Rate limiting, realistic headers, caching

## Usage

```python
import requests

# Get today's predictions
response = requests.get('http://localhost:8000/api/games/today')
games = response.json()

for game in games:
    print(f"{game['away_team']['name']} @ {game['home_team']['name']}")
    print(f"Home: {game['home_pitcher']['name']} - {game['home_pitcher']['projection']['projected_strikeouts']} K")
    print(f"Away: {game['away_pitcher']['name']} - {game['away_pitcher']['projection']['projected_strikeouts']} K")
```