from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, validator
from typing import List, Dict
import uvicorn
import random
import httpx
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import os

app = FastAPI()

# Get the directory of the current file
current_dir = os.path.dirname(os.path.realpath(__file__))
# Set the absolute path to the build directory and static directory
build_dir = "/app/build"
static_dir = "/app/static"

# Mount the static files
app.mount("/static", StaticFiles(directory=static_dir), name="static_files")
app.mount("/", StaticFiles(directory=build_dir, html=True), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(build_dir, 'index.html'))

@app.get("/players.csv")
async def get_players_csv():
    return FileResponse(os.path.join(static_dir, "players.csv"))

# Define data models
class Player(BaseModel):
    name: str
    role: str = Field(..., pattern="^(batsman|bowler|all-rounder)$")

class PitchReport(BaseModel):
    description: str
    moisture_level: float = Field(..., ge=0, le=100)
    temperature: float
    last_match_date: datetime

class TeamSelection(BaseModel):
    players: List[Player]
    pitch_report: PitchReport

    @validator('players')
    def validate_player_count(cls, v):
        if len(v) != 22:
            raise ValueError('Must select exactly 22 players')
        return v

# Mock database (replace with actual database in production)
players_db = []

# Global variables for ML models
ml_models = {
    'performance': None,
    'team_suggestion': None
}
scaler = StandardScaler()

@app.post("/select-team")
async def select_team(team_selection: TeamSelection):
    try:
        # Process the pitch report
        pitch_analysis = analyze_pitch(team_selection.pitch_report)

        # Fetch player data
        player_data = await fetch_player_data(team_selection.players)

        # Apply machine learning predictions
        ml_predictions = predict_player_performance(player_data, pitch_analysis)

        # Apply pitch logic and optimize team selection
        optimized_team = optimize_team_selection(player_data, pitch_analysis, ml_predictions)

        return {"optimized_team": optimized_team}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def predict_player_performance(player_data: List[Dict], pitch_analysis: Dict) -> List[Dict]:
    # Use the trained ML models to predict player performance
    X = prepare_features(player_data, pitch_analysis)
    X_scaled = ml_models['scaler'].transform(X)
    performance_predictions = ml_models['performance'].predict(X_scaled)

    # Add predictions to player data
    for player, prediction in zip(player_data, performance_predictions):
        player['predicted_performance'] = float(prediction)

    return player_data

def analyze_pitch(pitch_report: PitchReport) -> Dict:
    pitch_type = "balanced"
    expected_score = 150
    spin_friendly = False
    pace_friendly = False

    if "dry" in pitch_report.description.lower() or pitch_report.moisture_level < 20:
        pitch_type = "dry"
        expected_score += 20
        spin_friendly = True
    elif "green" in pitch_report.description.lower() or pitch_report.moisture_level > 60:
        pitch_type = "green"
        expected_score -= 20
        pace_friendly = True
    elif "dusty" in pitch_report.description.lower():
        pitch_type = "dusty"
        expected_score += 10
        spin_friendly = True

    if pitch_report.temperature > 30:
        expected_score += 10
    elif pitch_report.temperature < 15:
        expected_score -= 10

    days_since_last_match = (datetime.now() - pitch_report.last_match_date).days
    if days_since_last_match < 3:
        expected_score -= 15
    elif days_since_last_match > 10:
        expected_score += 10

    return {
        "pitch_type": pitch_type,
        "expected_score": expected_score,
        "spin_friendly": spin_friendly,
        "pace_friendly": pace_friendly
    }

async def fetch_player_data(players: List[Player]) -> List[Dict]:
    # In a real scenario, this would make API calls to fetch actual player data
    async with httpx.AsyncClient() as client:
        player_data = []
        for player in players:
            # Simulating API call
            response = await client.get(f"https://api.cricketdata.com/players/{player.name}")
            if response.status_code == 200:
                data = response.json()
                player_data.append({
                    "name": player.name,
                    "role": player.role,
                    "batting_avg": data.get("batting_avg", round(random.uniform(20.0, 55.0), 2)),
                    "bowling_avg": data.get("bowling_avg", round(random.uniform(20.0, 40.0), 2)),
                    "recent_form": data.get("recent_form", round(random.uniform(0.5, 1.5), 2)),
                    "matches_played": data.get("matches_played", random.randint(10, 100))
                })
            else:
                # Fallback to random data if API call fails
                player_data.append({
                    "name": player.name,
                    "role": player.role,
                    "batting_avg": round(random.uniform(20.0, 55.0), 2),
                    "bowling_avg": round(random.uniform(20.0, 40.0), 2),
                    "recent_form": round(random.uniform(0.5, 1.5), 2),
                    "matches_played": random.randint(10, 100)
                })
    return player_data

def prepare_features(player_data: List[Dict], pitch_analysis: Dict) -> np.ndarray:
    features = []
    for player in player_data:
        player_features = [
            player['batting_avg'],
            player['bowling_avg'],
            player['recent_form'],
            player['matches_played'],
            1 if player['role'] == 'batsman' else 0,
            1 if player['role'] == 'bowler' else 0,
            1 if player['role'] == 'all-rounder' else 0,
            pitch_analysis['expected_score'],
            1 if pitch_analysis['spin_friendly'] else 0,
            1 if pitch_analysis['pace_friendly'] else 0
        ]
        features.append(player_features)
    return np.array(features)

def optimize_team_selection(player_data: List[Dict], pitch_analysis: Dict, ml_predictions: List[Dict]) -> List[Dict]:
    # Advanced optimization logic
    batsmen = [p for p in player_data if p['role'] == 'batsman']
    bowlers = [p for p in player_data if p['role'] == 'bowler']
    all_rounders = [p for p in player_data if p['role'] == 'all-rounder']

    # Adjust player ratings based on pitch conditions
    for player in player_data:
        if pitch_analysis['spin_friendly'] and player['role'] in ['bowler', 'all-rounder']:
            player['bowling_avg'] *= 0.9
        if pitch_analysis['pace_friendly'] and player['role'] in ['bowler', 'all-rounder']:
            player['bowling_avg'] *= 0.9
        player['overall_rating'] = (
            player['batting_avg'] * player['recent_form'] +
            (100 - player['bowling_avg']) * player['recent_form'] +
            player['matches_played'] * 0.1
        )

    # Sort players by overall rating
    sorted_players = sorted(player_data, key=lambda x: x['overall_rating'], reverse=True)

    optimized_team = []
    optimized_team.extend(sorted_players[:6])  # Top 6 players
    optimized_team.extend([p for p in sorted_players[6:] if p['role'] == 'bowler'][:4])  # 4 bowlers
    optimized_team.append(max([p for p in sorted_players if p['role'] == 'all-rounder'], key=lambda x: x['overall_rating']))  # 1 all-rounder

    # Ensure team composition
    if len(optimized_team) < 11:
        remaining = [p for p in sorted_players if p not in optimized_team]
        optimized_team.extend(remaining[:11-len(optimized_team)])

    # Select captain and vice-captain
    captain = max(optimized_team, key=lambda x: x['overall_rating'])
    vice_captain = sorted([p for p in optimized_team if p != captain], key=lambda x: x['overall_rating'])[-1]

    return {
        "team": optimized_team,
        "captain": captain['name'],
        "vice_captain": vice_captain['name']
    }

@app.get("/players")
async def get_players():
    return players_db

@app.post("/players")
async def add_player(player: Player):
    players_db.append(player)
    return {"message": "Player added successfully"}

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse(os.path.join(build_dir, 'index.html'))

if __name__ == "__main__":
    # Initialize and train machine learning models on startup
    ml_models = {}
    ml_models['scaler'] = StandardScaler()
    ml_models['performance'] = RandomForestRegressor(n_estimators=100, random_state=42)
    ml_models['team_suggestion'] = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(10,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    # Train models (in a real scenario, this would use historical data)
    # For now, we'll just compile the TensorFlow model
    ml_models['team_suggestion'].compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    uvicorn.run(app, host="0.0.0.0", port=8000)
