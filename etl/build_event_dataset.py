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

EVENTS_FOLDER = (
    PROJECT_ROOT
    / "open-data-master"
    / "data"
    / "events"
)


# ---------------------------------------------------------
# Load Premier League matches
# ---------------------------------------------------------

with open(MATCHES_FILE, "r", encoding="utf-8") as f:
    matches = json.load(f)


match_ids = {
    match["match_id"]
    for match in matches
}

print("Premier League matches:", len(match_ids))


# ---------------------------------------------------------
# Helper function
# ---------------------------------------------------------

def get_name(value):
    """
    Safely extract the 'name' field from a StatsBomb object.
    """
    if isinstance(value, dict):
        return value.get("name")
    return None


# ---------------------------------------------------------
# Extract events
# ---------------------------------------------------------

event_rows = []

for match_id in sorted(match_ids):

    event_file = os.path.join(
        EVENTS_FOLDER,
        f"{match_id}.json"
    )

    with open(event_file, "r", encoding="utf-8") as f:
        events = json.load(f)

    for event in events:

        event_type = get_name(
            event.get("type")
        )

        team = event.get("team") or {}
        player = event.get("player") or {}
        position = event.get("position") or {}
        possession_team = event.get("possession_team") or {}
        play_pattern = event.get("play_pattern") or {}

        location = event.get("location") or [None, None]

        # -------------------------------------------------
        # Base event fields
        # -------------------------------------------------

        row = {
            "match_id": match_id,

            "event_id": event.get("id"),
            "event_index": event.get("index"),

            "period": event.get("period"),
            "timestamp": event.get("timestamp"),
            "minute": event.get("minute"),
            "second": event.get("second"),

            "event_type": event_type,

            "possession": event.get("possession"),

            "possession_team_id": possession_team.get("id"),
            "possession_team": possession_team.get("name"),

            "play_pattern": play_pattern.get("name"),

            "team_id": team.get("id"),
            "team_name": team.get("name"),

            "player_id": player.get("id"),
            "player_name": player.get("name"),

            "position_id": position.get("id"),
            "position": position.get("name"),

            "location_x": location[0],
            "location_y": location[1],

            "duration": event.get("duration"),

            "under_pressure": event.get("under_pressure", False),
            "counterpress": event.get("counterpress", False),
        }


        # -------------------------------------------------
        # Pass fields
        # -------------------------------------------------

        pass_data = event.get("pass") or {}

        pass_recipient = pass_data.get("recipient") or {}
        pass_height = pass_data.get("height") or {}
        pass_body_part = pass_data.get("body_part") or {}
        pass_type = pass_data.get("type") or {}
        pass_outcome = pass_data.get("outcome") or {}

        pass_end_location = (
            pass_data.get("end_location")
            or [None, None]
        )

        row.update({

            "pass_recipient_id":
                pass_recipient.get("id"),

            "pass_recipient":
                pass_recipient.get("name"),

            "pass_length":
                pass_data.get("length"),

            "pass_angle":
                pass_data.get("angle"),

            "pass_height":
                pass_height.get("name"),

            "pass_end_x":
                pass_end_location[0],

            "pass_end_y":
                pass_end_location[1],

            "pass_body_part":
                pass_body_part.get("name"),

            "pass_type":
                pass_type.get("name"),

            "pass_outcome":
                pass_outcome.get("name"),
        })


        # -------------------------------------------------
        # Shot fields
        # -------------------------------------------------

        shot_data = event.get("shot") or {}

        shot_body_part = shot_data.get("body_part") or {}
        shot_type = shot_data.get("type") or {}
        shot_outcome = shot_data.get("outcome") or {}
        shot_technique = shot_data.get("technique") or {}

        shot_end_location = (
            shot_data.get("end_location")
            or [None, None, None]
        )

        row.update({

            "shot_xg":
                shot_data.get("statsbomb_xg"),

            "shot_end_x":
                shot_end_location[0],

            "shot_end_y":
                shot_end_location[1],

            "shot_body_part":
                shot_body_part.get("name"),

            "shot_type":
                shot_type.get("name"),

            "shot_outcome":
                shot_outcome.get("name"),

            "shot_first_time":
                shot_data.get("first_time"),

            "shot_technique":
                shot_technique.get("name"),

            "shot_key_pass_id":
                shot_data.get("key_pass_id"),
        })


        # -------------------------------------------------
        # Carry fields
        # -------------------------------------------------

        carry_data = event.get("carry") or {}

        carry_end_location = (
            carry_data.get("end_location")
            or [None, None]
        )

        row.update({

            "carry_end_x":
                carry_end_location[0],

            "carry_end_y":
                carry_end_location[1],
        })


        # -------------------------------------------------
        # Duel fields
        # -------------------------------------------------

        duel_data = event.get("duel") or {}
        duel_type = duel_data.get("type") or {}

        row["duel_type"] = duel_type.get("name")


        # -------------------------------------------------
        # Dribble fields
        # -------------------------------------------------

        dribble_data = event.get("dribble") or {}
        dribble_outcome = dribble_data.get("outcome") or {}

        row["dribble_outcome"] = (
            dribble_outcome.get("name")
        )


        # -------------------------------------------------
        # Interception fields
        # -------------------------------------------------

        interception_data = (
            event.get("interception") or {}
        )

        interception_outcome = (
            interception_data.get("outcome") or {}
        )

        row["interception_outcome"] = (
            interception_outcome.get("name")
        )


        # -------------------------------------------------
        # Clearance fields
        # -------------------------------------------------

        clearance_data = (
            event.get("clearance") or {}
        )

        clearance_body_part = (
            clearance_data.get("body_part") or {}
        )

        row["clearance_body_part"] = (
            clearance_body_part.get("name")
        )


        # -------------------------------------------------
        # Add row
        # -------------------------------------------------

        event_rows.append(row)


# ---------------------------------------------------------
# Create DataFrame
# ---------------------------------------------------------

events_df = pd.DataFrame(event_rows)


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

print("\n--- Event Dataset ---")

print("Shape:", events_df.shape)

print("\nColumns:")
print(events_df.columns.tolist())

print("\nEvent types:")
print(
    events_df["event_type"]
    .value_counts()
)


print("\nDuplicate event IDs:")
print(
    events_df["event_id"]
    .duplicated()
    .sum()
)


print("\nMissing values in key fields:")

key_columns = [
    "match_id",
    "event_id",
    "event_index",
    "period",
    "event_type",
    "team_id",
    "team_name",
]

print(
    events_df[key_columns]
    .isna()
    .sum()
)

# ---------------------------------------------------------
# Raw event count validation
# ---------------------------------------------------------

print("\n--- Raw Event Count Validation ---")

raw_event_count = 0
raw_event_type_counts = {}

for match_id in sorted(match_ids):

    event_file = os.path.join(
        EVENTS_FOLDER,
        f"{match_id}.json"
    )

    with open(event_file, "r", encoding="utf-8") as f:
        raw_events = json.load(f)

    raw_event_count += len(raw_events)

    for event in raw_events:

        event_type = get_name(
            event.get("type")
        )

        if event_type:
            raw_event_type_counts[event_type] = (
                raw_event_type_counts.get(event_type, 0) + 1
            )


clean_event_count = len(events_df)


print("Raw event count:", raw_event_count)
print("Clean event count:", clean_event_count)

print(
    "Event count matches:",
    raw_event_count == clean_event_count
)


# ---------------------------------------------------------
# Event type validation
# ---------------------------------------------------------

raw_event_types = pd.Series(
    raw_event_type_counts,
    name="raw_count"
)

clean_event_types = (
    events_df["event_type"]
    .value_counts()
    .rename("clean_count")
)

event_type_validation = pd.concat(
    [
        raw_event_types,
        clean_event_types
    ],
    axis=1
).fillna(0)


event_type_validation["raw_count"] = (
    event_type_validation["raw_count"]
    .astype(int)
)

event_type_validation["clean_count"] = (
    event_type_validation["clean_count"]
    .astype(int)
)

event_type_validation["difference"] = (
    event_type_validation["clean_count"]
    - event_type_validation["raw_count"]
)


print("\n--- Event Type Validation ---")

print(
    event_type_validation
    .sort_values("raw_count", ascending=False)
    .to_string()
)


print("\nEvent types with count differences:")

print(
    event_type_validation[
        event_type_validation["difference"] != 0
    ]
)

# ---------------------------------------------------------
# Analytical Quality Checks
# ---------------------------------------------------------

print("\n--- Analytical Quality Checks ---")


# ---------------------------------------------------------
# 1. Match coverage
# ---------------------------------------------------------

event_match_count = events_df["match_id"].nunique()

print("\nMatch coverage:")
print("Expected matches:", len(match_ids))
print("Event dataset matches:", event_match_count)
print(
    "Match coverage valid:",
    event_match_count == len(match_ids)
)


# ---------------------------------------------------------
# 2. Event ID uniqueness
# ---------------------------------------------------------

duplicate_event_ids = (
    events_df["event_id"]
    .duplicated()
    .sum()
)

print("\nEvent ID uniqueness:")
print("Duplicate event IDs:", duplicate_event_ids)


# ---------------------------------------------------------
# 3. Team coverage
# ---------------------------------------------------------

event_team_count = events_df["team_id"].nunique()

print("\nTeam coverage:")
print("Unique teams in events:", event_team_count)


# ---------------------------------------------------------
# 4. Player coverage
# ---------------------------------------------------------

event_player_count = (
    events_df["player_id"]
    .dropna()
    .nunique()
)

print("\nPlayer coverage:")
print("Unique players with event records:", event_player_count)


# ---------------------------------------------------------
# 5. Coordinate validation
# ---------------------------------------------------------

coordinate_columns = [
    "location_x",
    "location_y"
]

coordinate_check = events_df[
    coordinate_columns
].dropna()

invalid_x = (
    (coordinate_check["location_x"] < 0)
    | (coordinate_check["location_x"] > 120)
).sum()

invalid_y = (
    (coordinate_check["location_y"] < 0)
    | (coordinate_check["location_y"] > 80)
).sum()

print("\nCoordinate validation:")
print("Coordinates checked:", len(coordinate_check))
print("Invalid X coordinates:", invalid_x)
print("Invalid Y coordinates:", invalid_y)


# ---------------------------------------------------------
# 6. Event time validation
# ---------------------------------------------------------

invalid_minutes = (
    (events_df["minute"] < 0)
).sum()

invalid_seconds = (
    (events_df["second"] < 0)
    | (events_df["second"] >= 60)
).sum()

print("\nEvent time validation:")
print("Invalid minutes:", invalid_minutes)
print("Invalid seconds:", invalid_seconds)


# ---------------------------------------------------------
# 7. Shot xG validation
# ---------------------------------------------------------

shot_events = events_df[
    events_df["event_type"] == "Shot"
]

invalid_xg = (
    shot_events["shot_xg"].notna()
    & (
        (shot_events["shot_xg"] < 0)
        | (shot_events["shot_xg"] > 1)
    )
).sum()

missing_xg = (
    shot_events["shot_xg"]
    .isna()
    .sum()
)

print("\nShot xG validation:")
print("Total shots:", len(shot_events))
print("Shots with missing xG:", missing_xg)
print("Shots with invalid xG:", invalid_xg)


# ---------------------------------------------------------
# 8. Pass validation
# ---------------------------------------------------------

pass_events = events_df[
    events_df["event_type"] == "Pass"
]

invalid_pass_length = (
    pass_events["pass_length"].notna()
    & (pass_events["pass_length"] < 0)
).sum()

missing_pass_end = (
    pass_events[
        ["pass_end_x", "pass_end_y"]
    ]
    .isna()
    .any(axis=1)
    .sum()
)

print("\nPass validation:")
print("Total passes:", len(pass_events))
print(
    "Negative pass lengths:",
    invalid_pass_length
)
print(
    "Passes missing end location:",
    missing_pass_end
)


# ---------------------------------------------------------
# 9. Carry validation
# ---------------------------------------------------------

carry_events = events_df[
    events_df["event_type"] == "Carry"
]

missing_carry_end = (
    carry_events[
        ["carry_end_x", "carry_end_y"]
    ]
    .isna()
    .any(axis=1)
    .sum()
)

print("\nCarry validation:")
print("Total carries:", len(carry_events))
print(
    "Carries missing end location:",
    missing_carry_end
)


# ---------------------------------------------------------
# 10. Event-specific field coverage
# ---------------------------------------------------------

print("\nEvent-specific field coverage:")

print(
    "Passes with recipient:",
    pass_events["pass_recipient_id"]
    .notna()
    .sum()
)

print(
    "Shots with outcome:",
    shot_events["shot_outcome"]
    .notna()
    .sum()
)

print(
    "Shots resulting in goals:",
    (
        shot_events["shot_outcome"] == "Goal"
    ).sum()
)

print(
    "Carries with end location:",
    (
        carry_events[
            ["carry_end_x", "carry_end_y"]
        ]
        .notna()
        .all(axis=1)
    ).sum()
)

# ---------------------------------------------------------
# Detailed Analytical Investigations
# ---------------------------------------------------------

print("\n--- Detailed Analytical Investigations ---")


# ---------------------------------------------------------
# 1. Investigate invalid X coordinates
# ---------------------------------------------------------

invalid_x_events = events_df[
    events_df["location_x"].notna()
    & (
        (events_df["location_x"] < 0)
        | (events_df["location_x"] > 120)
    )
]

print("\nInvalid X coordinate events:")
print(
    invalid_x_events[
        [
            "match_id",
            "event_id",
            "event_index",
            "event_type",
            "player_name",
            "team_name",
            "location_x",
            "location_y"
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# 2. Passes without recipients
# ---------------------------------------------------------

passes_without_recipient = pass_events[
    pass_events["pass_recipient_id"].isna()
]

print("\nPasses without recipient:")
print(
    "Total:",
    len(passes_without_recipient)
)

print("\nPass outcome distribution for passes without recipient:")

print(
    passes_without_recipient[
        "pass_outcome"
    ]
    .fillna("SUCCESSFUL / NO OUTCOME")
    .value_counts()
)


# ---------------------------------------------------------
# 3. Overall pass outcome distribution
# ---------------------------------------------------------

print("\nOverall pass outcome distribution:")

print(
    pass_events[
        "pass_outcome"
    ]
    .fillna("SUCCESSFUL / NO OUTCOME")
    .value_counts()
)


# ---------------------------------------------------------
# 4. Event-player coverage
# ---------------------------------------------------------

events_with_player = (
    events_df["player_id"].notna()
)

events_without_player = (
    ~events_with_player
)

print("\nEvent-player coverage:")
print(
    "Events with player:",
    events_with_player.sum()
)

print(
    "Events without player:",
    events_without_player.sum()
)

print("\nEvent types without player:")

print(
    events_df.loc[
        events_without_player,
        "event_type"
    ].value_counts()
)


# ---------------------------------------------------------
# 5. Shot outcome distribution
# ---------------------------------------------------------

print("\nShot outcome distribution:")

print(
    shot_events[
        "shot_outcome"
    ].value_counts()
)


# ---------------------------------------------------------
# 6. Compare event goals with match goals
# ---------------------------------------------------------

shot_goals = (
    shot_events["shot_outcome"] == "Goal"
).sum()

own_goals = (
    events_df["event_type"] == "Own Goal For"
).sum()

match_goals = sum(
    match["home_score"] + match["away_score"]
    for match in matches
)

event_total_goals = shot_goals + own_goals

print("\nGoal reconciliation:")
print("Goals from shot events:", shot_goals)
print("Own goals:", own_goals)
print("Total goals from events:", event_total_goals)
print("Goals from match results:", match_goals)
print(
    "Goal counts match:",
    event_total_goals == match_goals
)

# ---------------------------------------------------------
# 7. Check impossible shot xG values
# ---------------------------------------------------------

print("\nShot xG summary:")

print(
    shot_events["shot_xg"].describe()
)


# ---------------------------------------------------------
# 8. Check event coordinates by event type
# ---------------------------------------------------------

coordinate_missing_by_type = (
    events_df
    .groupby("event_type")[
        ["location_x", "location_y"]
    ]
    .apply(
        lambda x: x.isna().any(axis=1).sum()
    )
    .sort_values(ascending=False)
)

print("\nEvents missing location coordinates by type:")

print(coordinate_missing_by_type)


# ---------------------------------------------------------
# 9. Check negative durations
# ---------------------------------------------------------

negative_duration = (
    events_df["duration"].notna()
    & (events_df["duration"] < 0)
).sum()

print("\nDuration validation:")
print(
    "Negative durations:",
    negative_duration
)

# ---------------------------------------------------------
# 9b. Investigate negative durations
# ---------------------------------------------------------

negative_duration_events = events_df[
    events_df["duration"].notna()
    & (events_df["duration"] < 0)
]

print("\nNegative duration events:")

print(
    negative_duration_events[
        [
            "match_id",
            "event_id",
            "event_index",
            "event_type",
            "player_name",
            "team_name",
            "period",
            "timestamp",
            "minute",
            "second",
            "duration"
        ]
    ].to_string(index=False)
)

# ---------------------------------------------------------
# 9c. Inspect raw negative-duration events
# ---------------------------------------------------------

negative_event_ids = set(
    negative_duration_events["event_id"]
)

print("\nRaw details for negative-duration events:")

for match_id in negative_duration_events["match_id"].unique():

    event_file = os.path.join(
        EVENTS_FOLDER,
        f"{match_id}.json"
    )

    with open(event_file, "r", encoding="utf-8") as f:
        raw_events = json.load(f)

    for event in raw_events:

        if event.get("id") in negative_event_ids:

            print("\nMatch:", match_id)

            print(
                json.dumps(
                    event,
                    indent=2,
                    ensure_ascii=False
                )
            )


# ---------------------------------------------------------
# 10. Check impossible pass end coordinates
# ---------------------------------------------------------

invalid_pass_end = pass_events[
    pass_events[
        ["pass_end_x", "pass_end_y"]
    ].notna().all(axis=1)
    & (
        (pass_events["pass_end_x"] < 0)
        | (pass_events["pass_end_x"] > 120)
        | (pass_events["pass_end_y"] < 0)
        | (pass_events["pass_end_y"] > 80)
    )
]

print("\nInvalid pass end coordinates:")
print(
    "Count:",
    len(invalid_pass_end)
)


# ---------------------------------------------------------
# 11. Check impossible carry end coordinates
# ---------------------------------------------------------

invalid_carry_end = carry_events[
    carry_events[
        ["carry_end_x", "carry_end_y"]
    ].notna().all(axis=1)
    & (
        (carry_events["carry_end_x"] < 0)
        | (carry_events["carry_end_x"] > 120)
        | (carry_events["carry_end_y"] < 0)
        | (carry_events["carry_end_y"] > 80)
    )
]

print("\nInvalid carry end coordinates:")
print(
    "Count:",
    len(invalid_carry_end)
)

# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

events_df.to_csv(
    PROJECT_ROOT / "data" / "events_cleaned.csv",
    index=False
)

print("\nSaved:")
print(PROJECT_ROOT / "data" / "events_cleaned.csv")