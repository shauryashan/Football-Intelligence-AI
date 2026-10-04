import json
import os
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

file_path = PROJECT_ROOT / "open-data-master" / "data" / "matches" / "2" / "27.json"

with open(file_path, "r", encoding="utf-8") as file:
    matches = json.load(file)

match_data = []

for match in matches:
    match_data.append({
        "match_id": match["match_id"],
        "match_date": match["match_date"],
        "kick_off": match["kick_off"],
        "season_id": match["season"]["season_id"],
        "season_name": match["season"]["season_name"],
        "home_team_id": match["home_team"]["home_team_id"],
        "home_team": match["home_team"]["home_team_name"],
        "away_team_id": match["away_team"]["away_team_id"],
        "away_team": match["away_team"]["away_team_name"],
        "home_score": match["home_score"],
        "away_score": match["away_score"],
        "match_week": match["match_week"],
        "competition_stage": match["competition_stage"]["name"],
        "stadium": match["stadium"]["name"],
        "referee": match["referee"]["name"]
    })

df = pd.DataFrame(match_data)

def get_match_result(row):
    if row["home_score"] > row["away_score"]:
        return "HOME_WIN"
    elif row["home_score"] < row["away_score"]:
        return "AWAY_WIN"
    else:
        return "DRAW"


df["match_result"] = df.apply(get_match_result, axis=1)

print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 matches:")
print(df.head())

print("\nMatch Results:")
print(df[["home_team", "away_team", "home_score", "away_score", "match_result"]].head(10))

print("\nResult Distribution:")
print(df["match_result"].value_counts())

print("\n--- Data Validation ---")

# 1. Missing values
print("\nMissing values:")
print(df.isnull().sum())

# 2. Duplicate match IDs
print("\nDuplicate match IDs:")
print(df["match_id"].duplicated().sum())

# 3. Unique teams
teams = pd.concat([df["home_team"], df["away_team"]]).unique()

print("\nNumber of unique teams:")
print(len(teams))

print("\nTeams:")
print(sorted(teams))

# 4. Date range
print("\nDate range:")
print(df["match_date"].min(), "to", df["match_date"].max())

# 5. Score statistics
print("\nScore statistics:")
print("Average home goals:", df["home_score"].mean())
print("Average away goals:", df["away_score"].mean())
print("Highest home score:", df["home_score"].max())
print("Highest away score:", df["away_score"].max())

# 6. Check for impossible negative scores
print("\nNegative scores:")
print((df["home_score"] < 0).sum() + (df["away_score"] < 0).sum())

print("\n--- Available Competition/Season Data ---")

matches_path = PROJECT_ROOT / "open-data-master" / "data" / "matches"

dataset_summary = []

for competition_id in os.listdir(matches_path):

    competition_folder = os.path.join(matches_path, competition_id)

    if not os.path.isdir(competition_folder):
        continue

    for season_file in os.listdir(competition_folder):

        if not season_file.endswith(".json"):
            continue

        file_path = os.path.join(competition_folder, season_file)

        with open(file_path, "r", encoding="utf-8") as file:
            matches = json.load(file)

        if len(matches) == 0:
            continue

        first_match = matches[0]

        dataset_summary.append({
            "competition_id": first_match["competition"]["competition_id"],
            "competition_name": first_match["competition"]["competition_name"],
            "season_id": first_match["season"]["season_id"],
            "season_name": first_match["season"]["season_name"],
            "matches": len(matches)
        })

dataset_df = pd.DataFrame(dataset_summary)

dataset_df = dataset_df.sort_values(
    "matches",
    ascending=False
)

print("\nTotal competition-season datasets:", len(dataset_df))

print("\nLargest datasets:")
print(dataset_df.head(20).to_string(index=False))

# Inspect one match's lineup data

lineup_path = PROJECT_ROOT / "open-data-master" / "data" / "lineups" / "3754217.json"

with open(lineup_path, "r", encoding="utf-8") as file:
    lineups = json.load(file)

print("\n--- Lineup Data ---")

print("Number of teams:", len(lineups))

for team in lineups:
    print("\nTeam:", team["team_name"])
    print("Team ID:", team["team_id"])
    print("Number of players:", len(team["lineup"]))

    print("\nFirst player:")
    print(team["lineup"][0])