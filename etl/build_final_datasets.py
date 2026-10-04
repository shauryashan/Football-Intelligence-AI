import json
import os
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MATCHES_FILE = (
    PROJECT_ROOT
    / "open-data-master"
    / "data"
    / "matches"
    / "2"
    / "27.json"
)

LINEUPS_FOLDER = (
    PROJECT_ROOT
    / "open-data-master"
    / "data"
    / "lineups"
)

EVENTS_FOLDER = (
    PROJECT_ROOT
    / "open-data-master"
    / "data"
    / "events"
)

DATA_DIR = PROJECT_ROOT / "data"


# ---------------------------------------------------------
# Load Premier League matches
# ---------------------------------------------------------

with open(MATCHES_FILE, "r", encoding="utf-8") as file:
    matches = json.load(file)

match_ids = {
    match["match_id"]
    for match in matches
}


# ---------------------------------------------------------
# Build final matches table
# ---------------------------------------------------------

match_rows = []

for match in matches:

    match_rows.append({
        "match_id": match["match_id"],
        "match_date": match["match_date"],
        "kick_off": match["kick_off"],

        "season_id": match["season"]["season_id"],
        "season_name": match["season"]["season_name"],

        "home_team_id": match["home_team"]["home_team_id"],
        "away_team_id": match["away_team"]["away_team_id"],

        "home_score": match["home_score"],
        "away_score": match["away_score"],

        "match_week": match["match_week"],
        "competition_stage": match["competition_stage"]["name"],
        "stadium": match["stadium"]["name"],
        "referee": match["referee"]["name"]
    })


matches_df = pd.DataFrame(match_rows)


# ---------------------------------------------------------
# Create match result
# ---------------------------------------------------------

def get_match_result(row):

    if row["home_score"] > row["away_score"]:
        return "HOME_WIN"

    elif row["home_score"] < row["away_score"]:
        return "AWAY_WIN"

    else:
        return "DRAW"


matches_df["match_result"] = matches_df.apply(
    get_match_result,
    axis=1
)


# ---------------------------------------------------------
# Validate final matches table
# ---------------------------------------------------------

print("\n--- Final Matches Table ---")

print("Shape:", matches_df.shape)

print("\nColumns:")
print(matches_df.columns.tolist())

print("\nDuplicate match IDs:")
print(matches_df["match_id"].duplicated().sum())

print("\nMissing values:")
print(matches_df.isnull().sum())

print("\nMatch result distribution:")
print(matches_df["match_result"].value_counts())


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

matches_df.to_csv(
    DATA_DIR / "matches_cleaned.csv",
    index=False
)

# ---------------------------------------------------------
# Build final teams table
# ---------------------------------------------------------

team_rows = []

for match in matches:

    home_team = match["home_team"]
    away_team = match["away_team"]

    team_rows.append({
        "team_id": home_team["home_team_id"],
        "team_name": home_team["home_team_name"]
    })

    team_rows.append({
        "team_id": away_team["away_team_id"],
        "team_name": away_team["away_team_name"]
    })


teams_df = (
    pd.DataFrame(team_rows)
    .drop_duplicates(subset=["team_id"])
    .sort_values("team_id")
    .reset_index(drop=True)
)


# ---------------------------------------------------------
# Validate teams table
# ---------------------------------------------------------

print("\n--- Final Teams Table ---")

print("Shape:", teams_df.shape)

print("\nColumns:")
print(teams_df.columns.tolist())

print("\nUnique teams:")
print(teams_df["team_id"].nunique())

print("\nDuplicate team IDs:")
print(teams_df["team_id"].duplicated().sum())

print("\nTeam ID -> Team Name consistency:")

team_name_counts = (
    teams_df
    .groupby("team_id")["team_name"]
    .nunique()
)

print("Team IDs with multiple names:")
print((team_name_counts > 1).sum())


# ---------------------------------------------------------
# Save teams table
# ---------------------------------------------------------

teams_df.to_csv(
    DATA_DIR / "teams.csv",
    index=False
)

print("\nSaved:")
print("teams.csv")


# ---------------------------------------------------------
# Build final players table
# ---------------------------------------------------------

player_rows = []

for filename in os.listdir(
    "open-data-master/data/lineups"
):

    if not filename.endswith(".json"):
        continue

    match_id = int(filename.replace(".json", ""))

    if match_id not in match_ids:
        continue

    filepath = os.path.join(
        "open-data-master/data/lineups",
        filename
    )

    with open(filepath, "r", encoding="utf-8") as file:
        lineup_data = json.load(file)

    for team in lineup_data:

        for player in team["lineup"]:

            player_rows.append({
                "player_id": player["player_id"],
                "player_name": player["player_name"],
                "player_nickname": player["player_nickname"],
                "country": player.get("country", {}).get("name")
            })


players_df = (
    pd.DataFrame(player_rows)
    .drop_duplicates(subset=["player_id"])
    .sort_values("player_id")
    .reset_index(drop=True)
)


# ---------------------------------------------------------
# Validate players table
# ---------------------------------------------------------

print("\n--- Final Players Table ---")

print("Shape:", players_df.shape)

print("\nColumns:")
print(players_df.columns.tolist())

print("\nUnique players:")
print(players_df["player_id"].nunique())

print("\nDuplicate player IDs:")
print(players_df["player_id"].duplicated().sum())

print("\nMissing values:")
print(players_df.isnull().sum())


# ---------------------------------------------------------
# Save players table
# ---------------------------------------------------------

players_df.to_csv(
    DATA_DIR / "players.csv",
    index=False
)

# ---------------------------------------------------------
# Build final player_match table
# ---------------------------------------------------------

LINEUPS_FOLDER = "open-data-master/data/lineups"
EVENTS_FOLDER = "open-data-master/data/events"


# ---------------------------------------------------------
# Find actual end time of every match
# ---------------------------------------------------------

match_end_times = {}

for match_id in match_ids:

    event_file = os.path.join(
        EVENTS_FOLDER,
        f"{match_id}.json"
    )

    with open(event_file, "r", encoding="utf-8") as file:
        events = json.load(file)

    final_whistle = None

    for event in events:

        if (
            event.get("period") == 2
            and event.get("type", {}).get("name") == "Half End"
        ):
            final_whistle = (
                event.get("minute"),
                event.get("second")
            )

    if final_whistle is not None:

        minute, second = final_whistle

        match_end_times[match_id] = (
            minute * 60 + second
        )


print(
    "\nActual match end times found:",
    len(match_end_times)
)


# ---------------------------------------------------------
# Helper function
# ---------------------------------------------------------

def time_to_seconds(time_value):

    if pd.isna(time_value):
        return None

    minutes, seconds = time_value.split(":")

    return int(minutes) * 60 + int(seconds)


# ---------------------------------------------------------
# Extract player-match records
# ---------------------------------------------------------

player_match_rows = []

for filename in os.listdir(LINEUPS_FOLDER):

    if not filename.endswith(".json"):
        continue

    match_id = int(filename.replace(".json", ""))

    if match_id not in match_ids:
        continue

    filepath = os.path.join(
        LINEUPS_FOLDER,
        filename
    )

    with open(filepath, "r", encoding="utf-8") as file:
        lineup_data = json.load(file)

    for team in lineup_data:

        team_id = team["team_id"]

        for player in team["lineup"]:

            position_info = (
                player["positions"][0]
                if player["positions"]
                else {}
            )

            player_match_rows.append({
                "match_id": match_id,
                "player_id": player["player_id"],
                "team_id": team_id,
                "jersey_number": player["jersey_number"],
                "position_id": position_info.get("position_id"),
                "position": position_info.get("position"),
                "start_reason": position_info.get("start_reason"),
                "end_reason": position_info.get("end_reason"),
                "from_time": position_info.get("from"),
                "to_time": position_info.get("to")
            })


player_match_df = pd.DataFrame(player_match_rows)


# ---------------------------------------------------------
# Convert times to seconds
# ---------------------------------------------------------

player_match_df["from_seconds"] = (
    player_match_df["from_time"]
    .apply(time_to_seconds)
)

player_match_df["to_seconds"] = (
    player_match_df["to_time"]
    .apply(time_to_seconds)
)


# ---------------------------------------------------------
# Calculate minutes played
# ---------------------------------------------------------

player_match_df["minutes_played"] = 0.0


# Players who actually appeared
played_mask = (
    player_match_df["from_seconds"].notna()
)


# Players with a recorded exit time
has_to_time = (
    played_mask
    & player_match_df["to_seconds"].notna()
)

player_match_df.loc[has_to_time, "minutes_played"] = (
    player_match_df.loc[has_to_time, "to_seconds"]
    - player_match_df.loc[has_to_time, "from_seconds"]
) / 60


# Players without a recorded exit time
no_to_time = (
    played_mask
    & player_match_df["to_seconds"].isna()
)

player_match_df.loc[no_to_time, "minutes_played"] = (
    player_match_df.loc[no_to_time, "match_id"].map(
        match_end_times
    )
    - player_match_df.loc[no_to_time, "from_seconds"]
) / 60


# ---------------------------------------------------------
# Remove ETL helper columns
# ---------------------------------------------------------

player_match_df = player_match_df.drop(
    columns=[
        "from_seconds",
        "to_seconds"
    ]
)


# ---------------------------------------------------------
# Validate player-match table
# ---------------------------------------------------------

print("\n--- Final Player-Match Table ---")

print("Shape:", player_match_df.shape)

print("\nColumns:")
print(player_match_df.columns.tolist())

print("\nUnique players:")
print(player_match_df["player_id"].nunique())

print("\nUnique matches:")
print(player_match_df["match_id"].nunique())

print("\nDuplicate (match_id, player_id) records:")
print(
    player_match_df.duplicated(
        subset=["match_id", "player_id"]
    ).sum()
)

print("\nNegative minutes:")
print(
    (player_match_df["minutes_played"] < 0).sum()
)

print("\nZero-minute records:")
print(
    (player_match_df["minutes_played"] == 0).sum()
)

print("\nMinutes statistics:")
print(
    player_match_df["minutes_played"].describe()
)


# ---------------------------------------------------------
# Save player-match table
# ---------------------------------------------------------

player_match_df.to_csv(
    DATA_DIR / "player_match_cleaned.csv",
    index=False
)

# ---------------------------------------------------------
# Relational Integrity Validation
# ---------------------------------------------------------

print("\n--- Relational Integrity Validation ---")


# ---------------------------------------------------------
# 1. player_match → matches
# ---------------------------------------------------------

invalid_player_match_matches = (
    ~player_match_df["match_id"].isin(
        matches_df["match_id"]
    )
).sum()

print(
    "\nplayer_match → matches:",
    invalid_player_match_matches,
    "invalid references"
)


# ---------------------------------------------------------
# 2. player_match → players
# ---------------------------------------------------------

invalid_player_match_players = (
    ~player_match_df["player_id"].isin(
        players_df["player_id"]
    )
).sum()

print(
    "player_match → players:",
    invalid_player_match_players,
    "invalid references"
)


# ---------------------------------------------------------
# 3. player_match → teams
# ---------------------------------------------------------

invalid_player_match_teams = (
    ~player_match_df["team_id"].isin(
        teams_df["team_id"]
    )
).sum()

print(
    "player_match → teams:",
    invalid_player_match_teams,
    "invalid references"
)


# ---------------------------------------------------------
# 4. matches.home_team_id → teams
# ---------------------------------------------------------

invalid_home_teams = (
    ~matches_df["home_team_id"].isin(
        teams_df["team_id"]
    )
).sum()

print(
    "matches.home_team_id → teams:",
    invalid_home_teams,
    "invalid references"
)


# ---------------------------------------------------------
# 5. matches.away_team_id → teams
# ---------------------------------------------------------

invalid_away_teams = (
    ~matches_df["away_team_id"].isin(
        teams_df["team_id"]
    )
).sum()

print(
    "matches.away_team_id → teams:",
    invalid_away_teams,
    "invalid references"
)


# ---------------------------------------------------------
# Overall result
# ---------------------------------------------------------

total_invalid_references = (
    invalid_player_match_matches
    + invalid_player_match_players
    + invalid_player_match_teams
    + invalid_home_teams
    + invalid_away_teams
)

print("\nTotal invalid foreign-key references:")
print(total_invalid_references)

print(
    "\nRelational integrity valid:",
    total_invalid_references == 0
)

print("\nSaved:")
print("player_match_cleaned.csv")

print("\nSaved:")
print("players.csv")

print("\nSaved:")
print("matches_cleaned.csv")

# ---------------------------------------------------------
# Build final events table
# ---------------------------------------------------------

EVENTS_FILE = DATA_DIR / "events_cleaned.csv"


# ---------------------------------------------------------
# Load validated event dataset
# ---------------------------------------------------------

events_df = pd.read_csv(EVENTS_FILE)


# ---------------------------------------------------------
# Select final relational columns
# ---------------------------------------------------------

final_event_columns = [
    "match_id",
    "event_id",
    "event_index",
    "period",
    "timestamp",
    "minute",
    "second",
    "event_type",

    "possession",
    "possession_team_id",
    "play_pattern",

    "team_id",
    "player_id",
    "position_id",
    "position",

    "location_x",
    "location_y",
    "duration",
    "under_pressure",
    "counterpress",

    "pass_recipient_id",
    "pass_length",
    "pass_angle",
    "pass_height",
    "pass_end_x",
    "pass_end_y",
    "pass_body_part",
    "pass_type",
    "pass_outcome",

    "shot_xg",
    "shot_end_x",
    "shot_end_y",
    "shot_body_part",
    "shot_type",
    "shot_outcome",
    "shot_first_time",
    "shot_technique",
    "shot_key_pass_id",

    "carry_end_x",
    "carry_end_y",

    "duel_type",
    "dribble_outcome",
    "interception_outcome",
    "clearance_body_part"
]


events_df = events_df[final_event_columns]


# ---------------------------------------------------------
# Validate final events table
# ---------------------------------------------------------

print("\n--- Final Events Table ---")

print("Shape:", events_df.shape)

print("\nColumns:")
print(events_df.columns.tolist())

print("\nDuplicate event IDs:")
print(events_df["event_id"].duplicated().sum())


# ---------------------------------------------------------
# Event Foreign-Key Validation
# ---------------------------------------------------------

print("\n--- Event Foreign-Key Validation ---")


# 1. events.match_id → matches.match_id

invalid_event_matches = (
    ~events_df["match_id"].isin(
        matches_df["match_id"]
    )
).sum()

print(
    "events.match_id → matches.match_id:",
    invalid_event_matches,
    "invalid references"
)


# 2. events.team_id → teams.team_id

event_team_ids = (
    events_df["team_id"]
    .dropna()
)

invalid_event_teams = (
    ~event_team_ids.isin(
        teams_df["team_id"]
    )
).sum()

print(
    "events.team_id → teams.team_id:",
    invalid_event_teams,
    "invalid references"
)


# 3. events.possession_team_id → teams.team_id

possession_team_ids = (
    events_df["possession_team_id"]
    .dropna()
)

invalid_possession_teams = (
    ~possession_team_ids.isin(
        teams_df["team_id"]
    )
).sum()

print(
    "events.possession_team_id → teams.team_id:",
    invalid_possession_teams,
    "invalid references"
)


# 4. events.player_id → players.player_id

event_player_ids = (
    events_df["player_id"]
    .dropna()
)

invalid_event_players = (
    ~event_player_ids.isin(
        players_df["player_id"]
    )
).sum()

print(
    "events.player_id → players.player_id:",
    invalid_event_players,
    "invalid references"
)


# 5. events.pass_recipient_id → players.player_id

pass_recipient_ids = (
    events_df["pass_recipient_id"]
    .dropna()
)

invalid_pass_recipients = (
    ~pass_recipient_ids.isin(
        players_df["player_id"]
    )
).sum()

print(
    "events.pass_recipient_id → players.player_id:",
    invalid_pass_recipients,
    "invalid references"
)


# ---------------------------------------------------------
# Overall event relational integrity
# ---------------------------------------------------------

total_invalid_event_references = (
    invalid_event_matches
    + invalid_event_teams
    + invalid_possession_teams
    + invalid_event_players
    + invalid_pass_recipients
)

print("\nTotal invalid event foreign-key references:")
print(total_invalid_event_references)

print(
    "\nEvent relational integrity valid:",
    total_invalid_event_references == 0
)


# ---------------------------------------------------------
# Save final events table
# ---------------------------------------------------------

events_df.to_csv(
    DATA_DIR / "events_final.csv",
    index=False
)

print("\nSaved:")
print("events_final.csv")