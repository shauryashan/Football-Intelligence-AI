import json
import os
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LINEUPS_FOLDER = PROJECT_ROOT / "open-data-master" / "data" / "lineups"
EVENTS_FOLDER = PROJECT_ROOT / "open-data-master" / "data" / "events"
MATCHES_FILE = PROJECT_ROOT / "open-data-master" / "data" / "matches" / "2" / "27.json"

with open(MATCHES_FILE, "r", encoding="utf-8") as file:
    matches = json.load(file)

premier_league_match_ids = {
    match["match_id"]
    for match in matches
}

print("Premier League matches:", len(premier_league_match_ids))

player_rows = []

for filename in os.listdir(LINEUPS_FOLDER):

    if not filename.endswith(".json"):
        continue

    match_id = int(filename.replace(".json", ""))
    if match_id not in premier_league_match_ids:
        continue

    print("Processing lineup:", filename)

    filepath = os.path.join(LINEUPS_FOLDER, filename)

    with open(filepath, "r", encoding="utf-8") as file:
        teams = json.load(file)

    for team in teams:

        team_id = team["team_id"]
        team_name = team["team_name"]

        for player in team["lineup"]:

            position_info = player["positions"][0] if player["positions"] else {}

            player_rows.append({
                "match_id": match_id,
                "team_id": team_id,
                "team_name": team_name,
                "player_id": player["player_id"],
                "player_name": player["player_name"],
                "player_nickname": player["player_nickname"],
                "jersey_number": player["jersey_number"],
                "country": player.get("country", {}).get("name"),
                "position_id": position_info.get("position_id"),
                "position": position_info.get("position"),
                "start_reason": position_info.get("start_reason"),
                "end_reason": position_info.get("end_reason"),
                "from_time": position_info.get("from"),
                "to_time": position_info.get("to")
            })

players_df = pd.DataFrame(player_rows)


# ---------------------------------------------------------
# Find the actual end time of every Premier League match
# ---------------------------------------------------------

match_end_times = {}

for match_id in premier_league_match_ids:

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


def time_to_seconds(time_value):

    if pd.isna(time_value):
        return None

    minutes, seconds = time_value.split(":")

    return int(minutes) * 60 + int(seconds)


players_df["from_seconds"] = players_df["from_time"].apply(time_to_seconds)
players_df["to_seconds"] = players_df["to_time"].apply(time_to_seconds)


# ---------------------------------------------------------
# Calculate minutes played
# ---------------------------------------------------------

# A player with no from_time did not appear in the match.
players_df["minutes_played"] = 0.0

# Players who actually entered the match.
played_mask = players_df["from_seconds"].notna()

# For players with a recorded to_time,
# calculate minutes using their actual exit time.
has_to_time = (
    played_mask
    & players_df["to_seconds"].notna()
)

players_df.loc[has_to_time, "minutes_played"] = (
    players_df.loc[has_to_time, "to_seconds"]
    - players_df.loc[has_to_time, "from_seconds"]
) / 60


# For players who have no to_time,
# use the actual final whistle of their match.
no_to_time = (
    played_mask
    & players_df["to_seconds"].isna()
)

players_df.loc[no_to_time, "minutes_played"] = (
    players_df.loc[no_to_time, "match_id"].map(match_end_times)
    - players_df.loc[no_to_time, "from_seconds"]
) / 60

print("\nMinutes Played:")
print(
    players_df[
        [
            "player_name",
            "team_name",
            "position",
            "start_reason",
            "from_time",
            "to_time",
            "minutes_played"
        ]
    ].head(20)
)

print("Shape:", players_df.shape)

print("\nColumns:")
print(players_df.columns.tolist())

print("\nFirst 10 rows:")
print(players_df.head(10))

print("\n--- Player Dataset Validation ---")

# 1. Number of unique players
print("\nUnique players:")
print(players_df["player_id"].nunique())

# 2. Number of unique player appearances
print("\nPlayer-match records:")
print(len(players_df))

# 3. Starting XI vs substitutes
print("\nStart reason distribution:")
print(players_df["start_reason"].value_counts(dropna=False))

# 4. Missing values
print("\nMissing values:")
print(players_df.isnull().sum())

# 5. Minutes statistics
print("\nMinutes played statistics:")
print(players_df["minutes_played"].describe())

# 6. Players with zero minutes
print("\nRecords with 0 minutes:")
print((players_df["minutes_played"] == 0).sum())

# 7. Records above 90 minutes
print("\nRecords above 90 minutes:")
print((players_df["minutes_played"] > 90).sum())

# 8. Missing positions
print("\nMissing positions:")
print(players_df["position"].isnull().sum())

# 9. Missing from_time
print("\nMissing from_time:")
print(players_df["from_time"].isnull().sum())

# 10. Duplicate player-match records
print("\nDuplicate player-match records:")
print(
    players_df.duplicated(
        subset=["match_id", "player_id"]
    ).sum()
)

print("\n--- Negative Minutes Records ---")

negative_minutes = players_df[
    players_df["minutes_played"] < 0
]

print(
    negative_minutes[
        [
            "match_id",
            "player_id",
            "player_name",
            "team_name",
            "position",
            "start_reason",
            "end_reason",
            "from_time",
            "to_time",
            "from_seconds",
            "to_seconds",
            "minutes_played"
        ]
    ].to_string(index=False)
)

print(
    "\nActual match end times found:",
    len(match_end_times)
)

# ---------------------------------------------------------
# Validate match end times
# ---------------------------------------------------------

match_end_minutes = pd.Series(
    match_end_times
).div(60)

print("\nMatch end-time statistics:")
print(match_end_minutes.describe())

print("\nShortest match:")
shortest_match_id = min(
    match_end_times,
    key=match_end_times.get
)
print(
    shortest_match_id,
    f"{match_end_times[shortest_match_id] // 60}:"
    f"{match_end_times[shortest_match_id] % 60:02d}"
)

print("\nLongest match:")
longest_match_id = max(
    match_end_times,
    key=match_end_times.get
)
print(
    longest_match_id,
    f"{match_end_times[longest_match_id] // 60}:"
    f"{match_end_times[longest_match_id] % 60:02d}"
)

# ---------------------------------------------------------
# Create Player Master Table
# ---------------------------------------------------------

players_master_df = (
    players_df[
        [
            "player_id",
            "player_name",
            "player_nickname",
            "country"
        ]
    ]
    .drop_duplicates(subset=["player_id"])
    .sort_values("player_id")
    .reset_index(drop=True)
)

print("\n--- Player Master Table ---")

print("Unique players:", len(players_master_df))

print("\nColumns:")
print(players_master_df.columns.tolist())

print("\nFirst 20 players:")
print(players_master_df.head(20).to_string(index=False))

print("\nDuplicate player IDs:")
print(
    players_master_df["player_id"]
    .duplicated()
    .sum()
)

# ---------------------------------------------------------
# Create Team Master Table
# ---------------------------------------------------------

teams_master_df = (
    players_df[
        [
            "team_id",
            "team_name"
        ]
    ]
    .drop_duplicates(subset=["team_id"])
    .sort_values("team_id")
    .reset_index(drop=True)
)

print("\n--- Team Master Table ---")

print("Unique teams:", len(teams_master_df))

print("\nColumns:")
print(teams_master_df.columns.tolist())

print("\nAll teams:")
print(teams_master_df.to_string(index=False))

print("\nDuplicate team IDs:")
print(
    teams_master_df["team_id"]
    .duplicated()
    .sum()
)

# ---------------------------------------------------------
# Validate Team ID -> Team Name Mapping
# ---------------------------------------------------------

team_name_counts = (
    players_df
    .groupby("team_id")["team_name"]
    .nunique()
)

print("\n--- Team ID -> Team Name Validation ---")

print(
    "Team IDs with multiple names:",
    (team_name_counts > 1).sum()
)

if (team_name_counts > 1).any():
    print("\nTeams with inconsistent names:")
    print(team_name_counts[team_name_counts > 1])
else:
    print("Every team ID maps to exactly one team name.")