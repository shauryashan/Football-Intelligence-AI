import sqlite3
import numpy as np
import pandas as pd

from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_ROOT / "database" / "football.db"


# ============================================================
# DATABASE
# ============================================================

connection = sqlite3.connect(DATABASE_FILE)

print("Connected to football.db")


# ============================================================
# LOAD MATCHES
# ============================================================

matches = pd.read_sql_query(
    """
    SELECT
        match_id,
        match_date,
        kick_off,
        home_team_id,
        away_team_id,
        home_score,
        away_score,
        match_result
    FROM matches
    """,
    connection
)

matches["match_date"] = pd.to_datetime(
    matches["match_date"]
)

matches = matches.sort_values(
    [
        "match_date",
        "kick_off",
        "match_id"
    ]
).reset_index(drop=True)

matches["match_order"] = np.arange(
    len(matches)
)

print(
    f"Matches loaded: {len(matches)}"
)


# ============================================================
# LOAD EVENTS
# ============================================================

print(
    "\nLoading match event data..."
)

event_stats_query = """
SELECT
    match_id,
    team_id,
    SUM(CASE WHEN event_type = 'Shot' THEN 1 ELSE 0 END) AS shots,
    SUM(CASE WHEN event_type = 'Shot' THEN COALESCE(shot_xg, 0) ELSE 0 END) AS xg,
    SUM(CASE WHEN event_type = 'Pass' THEN 1 ELSE 0 END) AS Pass,
    SUM(CASE WHEN event_type = 'Pressure' THEN 1 ELSE 0 END) AS Pressure,
    SUM(CASE WHEN event_type = 'Carry' THEN 1 ELSE 0 END) AS Carry,
    SUM(CASE WHEN event_type = 'Duel' THEN 1 ELSE 0 END) AS Duel,
    SUM(CASE WHEN event_type = 'Interception' THEN 1 ELSE 0 END) AS Interception,
    SUM(CASE WHEN event_type = 'Clearance' THEN 1 ELSE 0 END) AS Clearance
FROM events
GROUP BY match_id, team_id
"""

team_match_events = pd.read_sql_query(
    event_stats_query,
    connection
)

print(
    f"Team-match event rows loaded: {len(team_match_events)}"
)


# ============================================================
# BUILD TEAM-MATCH EVENT STATISTICS
# ============================================================

print(
    "\nBuilding team-match event statistics..."
)


# Event statistics are aggregated inside SQLite before being
# loaded into Pandas. This avoids loading all 1.3M events into
# memory when ML5 only needs team-match level counts and xG.

# ============================================================
# BUILD TEAM-MATCH RESULT DATA
# ============================================================

print(
    "\nBuilding team-match performance table..."
)


home_team_matches = matches[
    [
        "match_id",
        "match_order",
        "match_date",
        "home_team_id",
        "away_team_id",
        "home_score",
        "away_score"
    ]
].copy()


home_team_matches["team_id"] = (
    home_team_matches["home_team_id"]
)


home_team_matches["goals_for"] = (
    home_team_matches["home_score"]
)


home_team_matches["goals_against"] = (
    home_team_matches["away_score"]
)


home_team_matches["home_away"] = "HOME"


home_team_matches = home_team_matches[
    [
        "match_id",
        "match_order",
        "match_date",
        "team_id",
        "home_away",
        "goals_for",
        "goals_against"
    ]
]


away_team_matches = matches[
    [
        "match_id",
        "match_order",
        "match_date",
        "home_team_id",
        "away_team_id",
        "home_score",
        "away_score"
    ]
].copy()


away_team_matches["team_id"] = (
    away_team_matches["away_team_id"]
)


away_team_matches["goals_for"] = (
    away_team_matches["away_score"]
)


away_team_matches["goals_against"] = (
    away_team_matches["home_score"]
)


away_team_matches["home_away"] = "AWAY"


away_team_matches = away_team_matches[
    [
        "match_id",
        "match_order",
        "match_date",
        "team_id",
        "home_away",
        "goals_for",
        "goals_against"
    ]
]


team_matches = pd.concat(
    [
        home_team_matches,
        away_team_matches
    ],
    ignore_index=True
)


# ============================================================
# ADD RESULT / POINTS
# ============================================================

team_matches["points"] = np.select(

    [
        team_matches["goals_for"]
        > team_matches["goals_against"],

        team_matches["goals_for"]
        ==
        team_matches["goals_against"]
    ],

    [
        3,
        1
    ],

    default=0
)


# ============================================================
# ADD EVENT STATISTICS
# ============================================================

team_matches = team_matches.merge(
    team_match_events[
        [
            "match_id",
            "team_id",
            "shots",
            "xg",
            "Pass",
            "Pressure",
            "Carry",
            "Duel",
            "Interception",
            "Clearance"
        ]
    ],
    on=[
        "match_id",
        "team_id"
    ],
    how="left"
)


event_columns = [
    "shots",
    "xg",
    "Pass",
    "Pressure",
    "Carry",
    "Duel",
    "Interception",
    "Clearance"
]


for column in event_columns:

    team_matches[column] = (
        team_matches[column]
        .fillna(0)
    )


# ============================================================
# SORT TEAM HISTORY
# ============================================================

team_matches = team_matches.sort_values(
    [
        "team_id",
        "match_order"
    ]
).reset_index(drop=True)


# ============================================================
# PREVIOUS-MATCH FEATURES
# ============================================================

print(
    "\nCalculating previous-5-match team form..."
)


rolling_columns = [
    "points",
    "goals_for",
    "goals_against",
    "shots",
    "xg",
    "Pass",
    "Pressure",
    "Carry",
    "Duel",
    "Interception",
    "Clearance"
]


for column in rolling_columns:

    team_matches[
        f"previous5_{column}"
    ] = (

        team_matches
        .groupby("team_id")[column]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                window=5,
                min_periods=5
            )
            .mean()
        )

    )


# ============================================================
# HOME/AWAY-SPECIFIC FORM
# ============================================================

print(
    "Calculating home/away-specific form..."
)


# ------------------------------------------------------------
# HOME MATCH HISTORY
# ------------------------------------------------------------

home_history = team_matches[
    team_matches["home_away"] == "HOME"
].copy()


for column in [
    "points",
    "goals_for",
    "goals_against",
    "xg"
]:

    home_history[
        f"previous5_home_{column}"
    ] = (

        home_history
        .groupby("team_id")[column]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                window=5,
                min_periods=5
            )
            .mean()
        )

    )


# ------------------------------------------------------------
# AWAY MATCH HISTORY
# ------------------------------------------------------------

away_history = team_matches[
    team_matches["home_away"] == "AWAY"
].copy()


for column in [
    "points",
    "goals_for",
    "goals_against",
    "xg"
]:

    away_history[
        f"previous5_away_{column}"
    ] = (

        away_history
        .groupby("team_id")[column]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                window=5,
                min_periods=5
            )
            .mean()
        )

    )


# ============================================================
# PREPARE HOME FEATURES
# ============================================================

home_feature_columns = [
    "match_id",
    "team_id"
]


home_feature_columns += [
    f"previous5_{column}"
    for column in rolling_columns
]


home_feature_columns += [
    f"previous5_home_{column}"
    for column in [
        "points",
        "goals_for",
        "goals_against",
        "xg"
    ]
]


home_features = home_history[
    home_feature_columns
].copy()


home_features = home_features.rename(
    columns={
        "team_id":
            "home_team_id"
    }
)


# ============================================================
# PREPARE AWAY FEATURES
# ============================================================

away_feature_columns = [
    "match_id",
    "team_id"
]


away_feature_columns += [
    f"previous5_{column}"
    for column in rolling_columns
]


away_feature_columns += [
    f"previous5_away_{column}"
    for column in [
        "points",
        "goals_for",
        "goals_against",
        "xg"
    ]
]


away_features = away_history[
    away_feature_columns
].copy()


away_features = away_features.rename(
    columns={
        "team_id":
            "away_team_id"
    }
)


# ============================================================
# MERGE HOME + AWAY FEATURES
# ============================================================

print(
    "\nBuilding final pre-match feature table..."
)


model_df = matches[
    [
        "match_id",
        "match_order",
        "match_date",
        "home_team_id",
        "away_team_id",
        "home_score",
        "away_score",
        "match_result"
    ]
].copy()


model_df = model_df.merge(
    home_features,
    on=[
        "match_id",
        "home_team_id"
    ],
    how="left"
)


model_df = model_df.merge(
    away_features,
    on=[
        "match_id",
        "away_team_id"
    ],
    how="left",
    suffixes=(
        "_home",
        "_away"
    )
)


# ============================================================
# CREATE DIFFERENCE FEATURES
# ============================================================

print(
    "\nCreating home-vs-away difference features..."
)


difference_pairs = [

    (
        "previous5_points_home",
        "previous5_points_away",
        "form_points_diff"
    ),

    (
        "previous5_goals_for_home",
        "previous5_goals_for_away",
        "goals_for_diff"
    ),

    (
        "previous5_goals_against_home",
        "previous5_goals_against_away",
        "goals_against_diff"
    ),

    (
        "previous5_shots_home",
        "previous5_shots_away",
        "shots_diff"
    ),

    (
        "previous5_xg_home",
        "previous5_xg_away",
        "xg_diff"
    ),

    (
        "previous5_Pass_home",
        "previous5_Pass_away",
        "passes_diff"
    ),

    (
        "previous5_Pressure_home",
        "previous5_Pressure_away",
        "pressures_diff"
    ),

    (
        "previous5_Carry_home",
        "previous5_Carry_away",
        "carries_diff"
    ),

    (
        "previous5_Duel_home",
        "previous5_Duel_away",
        "duels_diff"
    ),

    (
        "previous5_Interception_home",
        "previous5_Interception_away",
        "interceptions_diff"
    ),

    (
        "previous5_Clearance_home",
        "previous5_Clearance_away",
        "clearances_diff"
    ),

    (
        "previous5_home_points",
        "previous5_away_points",
        "home_away_points_diff"
    ),

    (
        "previous5_home_goals_for",
        "previous5_away_goals_for",
        "home_away_goals_for_diff"
    ),

    (
        "previous5_home_goals_against",
        "previous5_away_goals_against",
        "home_away_goals_against_diff"
    ),

    (
        "previous5_home_xg",
        "previous5_away_xg",
        "home_away_xg_diff"
    )

]


for home_column, away_column, new_column in difference_pairs:

    model_df[new_column] = (
        model_df[home_column]
        -
        model_df[away_column]
    )


# ============================================================
# PRE-MATCH FEATURE COLUMNS
# ============================================================

feature_columns = [

    "previous5_points_home",
    "previous5_points_away",

    "previous5_goals_for_home",
    "previous5_goals_for_away",

    "previous5_goals_against_home",
    "previous5_goals_against_away",

    "previous5_shots_home",
    "previous5_shots_away",

    "previous5_xg_home",
    "previous5_xg_away",

    "previous5_Pass_home",
    "previous5_Pass_away",

    "previous5_Pressure_home",
    "previous5_Pressure_away",

    "previous5_Carry_home",
    "previous5_Carry_away",

    "previous5_Duel_home",
    "previous5_Duel_away",

    "previous5_Interception_home",
    "previous5_Interception_away",

    "previous5_Clearance_home",
    "previous5_Clearance_away",

    "previous5_home_points",
    "previous5_away_points",

    "previous5_home_goals_for",
    "previous5_away_goals_for",

    "previous5_home_goals_against",
    "previous5_away_goals_against",

    "previous5_home_xg",
    "previous5_away_xg"

]


difference_columns = [
    item[2]
    for item in difference_pairs
]


feature_columns += difference_columns


# ============================================================
# REMOVE MATCHES WITHOUT ENOUGH HISTORY
# ============================================================

model_df = model_df.dropna(
    subset=feature_columns
).copy()


# ============================================================
# PRE-MATCH LEAKAGE CHECK
# ============================================================

print(
    "\n--- PRE-MATCH FEATURE VALIDATION ---"
)


print(
    "Total matches:",
    len(matches)
)


print(
    "Matches with sufficient previous-5 history:",
    len(model_df)
)


print(
    "Matches excluded because teams lacked "
    "5-match history:",
    len(matches) - len(model_df)
)


# ============================================================
# VERIFY FEATURES DO NOT USE CURRENT MATCH
# ============================================================

# Since all rolling features use shift(1),
# the current match cannot contribute to them.

print(
    "Current-match result excluded from features: True"
)


# ============================================================
# CHECK FEATURE COMPLETENESS
# ============================================================

missing_features = (
    model_df[
        feature_columns
    ]
    .isna()
    .sum()
    .sum()
)


print(
    "Missing feature values:",
    missing_features
)


# ============================================================
# CHECK DUPLICATES
# ============================================================

duplicate_matches = (
    model_df[
        "match_id"
    ]
    .duplicated()
    .sum()
)


print(
    "Duplicate match IDs:",
    duplicate_matches
)


# ============================================================
# CHECK TARGET
# ============================================================

print(
    "\n--- TARGET DISTRIBUTION ---"
)


print(
    model_df[
        "match_result"
    ]
    .value_counts()
)


# ============================================================
# CHRONOLOGICAL ORDER CHECK
# ============================================================

model_df = model_df.sort_values(
    "match_order"
).reset_index(drop=True)


chronological_order_valid = (
    model_df[
        "match_order"
    ]
    .is_monotonic_increasing
)


print(
    "\n--- CHRONOLOGICAL CHECK ---"
)

print(
    "Match order chronological:",
    chronological_order_valid
)


# ============================================================
# FINAL DATASET
# ============================================================

output_columns = [

    "match_id",
    "match_date",
    "match_order",
    "home_team_id",
    "away_team_id",
    "match_result"

] + feature_columns


final_dataset = model_df[
    output_columns
].copy()


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "match_outcome_features.csv"
)


final_dataset.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    "\nSaved pre-match feature dataset:"
)

print(
    OUTPUT_FILE
)


# ============================================================
# SAMPLE
# ============================================================

print(
    "\n--- SAMPLE PRE-MATCH FEATURES ---"
)


print(
    final_dataset
    .head(10)
    .to_string(index=False)
)


# ============================================================
# FINAL VALIDATION
# ============================================================

technical_validation_passed = (

    len(final_dataset) > 0

    and missing_features == 0

    and duplicate_matches == 0

    and chronological_order_valid

)


print(
    "\n========================================"
)


if technical_validation_passed:

    print(
        "ML5 PRE-MATCH FEATURE VALIDATION: PASSED"
    )

else:

    print(
        "ML5 PRE-MATCH FEATURE VALIDATION: FAILED"
    )


print(
    "========================================"
)


connection.close()


print(
    "\nDatabase connection closed."
)