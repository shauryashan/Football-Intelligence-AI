import sqlite3
import pandas as pd
import numpy as np


from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_FILE = PROJECT_ROOT / "database" / "football.db"


# --------------------------------------------------
# CONNECT TO DATABASE
# --------------------------------------------------

connection = sqlite3.connect(DATABASE_FILE)

print("Connected to football.db")


# --------------------------------------------------
# LOAD PLAYER SIMILARITY FEATURES
# --------------------------------------------------

query = """
WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
),

player_events AS (
    SELECT
        player_id,

        SUM(CASE WHEN event_type = 'Shot' THEN 1 ELSE 0 END) AS shots,

        SUM(
            CASE
                WHEN event_type = 'Shot'
                THEN COALESCE(shot_xg, 0)
                ELSE 0
            END
        ) AS expected_goals,

        SUM(
            CASE
                WHEN event_type = 'Shot'
                 AND shot_outcome = 'Goal'
                THEN 1
                ELSE 0
            END
        ) AS goals,

        SUM(CASE WHEN event_type = 'Pass' THEN 1 ELSE 0 END) AS passes,

        SUM(
            CASE
                WHEN event_type = 'Pass'
                 AND (
                     pass_outcome IS NULL
                     OR pass_outcome = ''
                     OR pass_outcome NOT IN (
                         'Incomplete',
                         'Out',
                         'Unknown',
                         'Injury Clearance'
                     )
                 )
                THEN 1
                ELSE 0
            END
        ) AS completed_passes,

        SUM(
            CASE
                WHEN event_type = 'Pass'
                THEN COALESCE(pass_length, 0)
                ELSE 0
            END
        ) AS pass_distance,

        SUM(CASE WHEN event_type = 'Pressure' THEN 1 ELSE 0 END) AS pressures,

        SUM(
            CASE
                WHEN event_type = 'Duel'
                 AND duel_type = 'Tackle'
                THEN 1
                ELSE 0
            END
        ) AS tackles,

        SUM(
            CASE
                WHEN event_type = 'Interception'
                THEN 1
                ELSE 0
            END
        ) AS interceptions,

        SUM(
            CASE
                WHEN event_type = 'Clearance'
                THEN 1
                ELSE 0
            END
        ) AS clearances,

        SUM(CASE WHEN event_type = 'Carry' THEN 1 ELSE 0 END) AS carries,

        SUM(CASE WHEN event_type = 'Dribble' THEN 1 ELSE 0 END) AS dribbles,

        SUM(
            CASE
                WHEN event_type = 'Dribble'
                 AND dribble_outcome = 'Complete'
                THEN 1
                ELSE 0
            END
        ) AS successful_dribbles,

        SUM(CASE WHEN event_type = 'Duel' THEN 1 ELSE 0 END) AS duels,

        SUM(
            CASE
                WHEN event_type = 'Duel'
                 AND duel_type = 'Aerial Lost'
                THEN 1
                ELSE 0
            END
        ) AS aerial_duels_lost,

        SUM(CASE WHEN event_type = 'Miscontrol' THEN 1 ELSE 0 END) AS miscontrols,

        SUM(CASE WHEN event_type = 'Dispossessed' THEN 1 ELSE 0 END) AS dispossessed,

        SUM(CASE WHEN event_type = 'Ball Recovery' THEN 1 ELSE 0 END) AS ball_recoveries

    FROM events
    WHERE player_id IS NOT NULL
    GROUP BY player_id
),

player_key_passes AS (
    SELECT
        pass_event.player_id,
        COUNT(*) AS key_passes
    FROM events shot
    JOIN events pass_event
        ON shot.shot_key_pass_id = pass_event.event_id
       AND pass_event.event_type = 'Pass'
    WHERE
        shot.event_type = 'Shot'
        AND shot.shot_key_pass_id IS NOT NULL
        AND pass_event.player_id IS NOT NULL
    GROUP BY pass_event.player_id
),

player_assists AS (
    SELECT
        pass_event.player_id,
        COUNT(*) AS assists
    FROM events shot
    JOIN events pass_event
        ON shot.shot_key_pass_id = pass_event.event_id
       AND pass_event.event_type = 'Pass'
    WHERE
        shot.event_type = 'Shot'
        AND shot.shot_key_pass_id IS NOT NULL
        AND shot.shot_outcome = 'Goal'
        AND pass_event.player_id IS NOT NULL
    GROUP BY pass_event.player_id
)

SELECT
    p.player_id,
    p.player_name,
    ROUND(pm.total_minutes, 2) AS total_minutes,

    ROUND(COALESCE(pe.shots, 0) / (pm.total_minutes / 90.0), 4)
        AS shots_per_90,

    ROUND(COALESCE(pe.expected_goals, 0) / (pm.total_minutes / 90.0), 4)
        AS xg_per_90,

    ROUND(COALESCE(pe.goals, 0) / (pm.total_minutes / 90.0), 4)
        AS goals_per_90,

    ROUND(COALESCE(pk.key_passes, 0) / (pm.total_minutes / 90.0), 4)
        AS key_passes_per_90,

    ROUND(COALESCE(pa.assists, 0) / (pm.total_minutes / 90.0), 4)
        AS assists_per_90,

    ROUND(COALESCE(pe.passes, 0) / (pm.total_minutes / 90.0), 4)
        AS passes_per_90,

    ROUND(COALESCE(pe.completed_passes, 0) / (pm.total_minutes / 90.0), 4)
        AS completed_passes_per_90,

    ROUND(COALESCE(pe.pass_distance, 0) / (pm.total_minutes / 90.0), 4)
        AS pass_distance_per_90,

    ROUND(COALESCE(pe.pressures, 0) / (pm.total_minutes / 90.0), 4)
        AS pressures_per_90,

    ROUND(COALESCE(pe.tackles, 0) / (pm.total_minutes / 90.0), 4)
        AS tackles_per_90,

    ROUND(COALESCE(pe.interceptions, 0) / (pm.total_minutes / 90.0), 4)
        AS interceptions_per_90,

    ROUND(COALESCE(pe.clearances, 0) / (pm.total_minutes / 90.0), 4)
        AS clearances_per_90,

    ROUND(COALESCE(pe.carries, 0) / (pm.total_minutes / 90.0), 4)
        AS carries_per_90,

    ROUND(COALESCE(pe.dribbles, 0) / (pm.total_minutes / 90.0), 4)
        AS dribbles_per_90,

    ROUND(COALESCE(pe.successful_dribbles, 0) / (pm.total_minutes / 90.0), 4)
        AS successful_dribbles_per_90,

    ROUND(COALESCE(pe.duels, 0) / (pm.total_minutes / 90.0), 4)
        AS duels_per_90,

    ROUND(COALESCE(pe.aerial_duels_lost, 0) / (pm.total_minutes / 90.0), 4)
        AS aerial_duels_lost_per_90,

    ROUND(COALESCE(pe.miscontrols, 0) / (pm.total_minutes / 90.0), 4)
        AS miscontrols_per_90,

    ROUND(COALESCE(pe.dispossessed, 0) / (pm.total_minutes / 90.0), 4)
        AS dispossessed_per_90,

    ROUND(COALESCE(pe.ball_recoveries, 0) / (pm.total_minutes / 90.0), 4)
        AS ball_recoveries_per_90

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

LEFT JOIN player_events pe
    ON pm.player_id = pe.player_id

LEFT JOIN player_key_passes pk
    ON pm.player_id = pk.player_id

LEFT JOIN player_assists pa
    ON pm.player_id = pa.player_id

WHERE pm.total_minutes >= 900

ORDER BY p.player_name;
"""


df = pd.read_sql_query(query, connection)


# --------------------------------------------------
# BASIC DATASET CHECK
# --------------------------------------------------

print("\n--- DATASET CHECK ---")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())


# --------------------------------------------------
# MISSING VALUES
# --------------------------------------------------

print("\n--- MISSING VALUES ---")

print(df.isna().sum())


# --------------------------------------------------
# DUPLICATE PLAYER CHECK
# --------------------------------------------------

print("\n--- DUPLICATE PLAYER CHECK ---")

print(
    "Duplicate player IDs:",
    df["player_id"].duplicated().sum()
)


# --------------------------------------------------
# FEATURE COLUMNS
# --------------------------------------------------

feature_columns = [
    "shots_per_90",
    "xg_per_90",
    "goals_per_90",
    "key_passes_per_90",
    "assists_per_90",
    "passes_per_90",
    "completed_passes_per_90",
    "pass_distance_per_90",
    "pressures_per_90",
    "tackles_per_90",
    "interceptions_per_90",
    "clearances_per_90",
    "carries_per_90",
    "dribbles_per_90",
    "successful_dribbles_per_90",
    "duels_per_90",
    "aerial_duels_lost_per_90",
    "miscontrols_per_90",
    "dispossessed_per_90",
    "ball_recoveries_per_90"
]


X = df[feature_columns]


# --------------------------------------------------
# FEATURE SUMMARY
# --------------------------------------------------

print("\n--- FEATURE SUMMARY ---")

summary = X.describe().T[
    ["mean", "std", "min", "50%", "max"]
]

print(summary)


# --------------------------------------------------
# ZERO-VARIANCE FEATURES
# --------------------------------------------------

print("\n--- ZERO-VARIANCE CHECK ---")

zero_variance = [
    column
    for column in feature_columns
    if X[column].nunique() <= 1
]

print("Zero-variance features:", zero_variance)


# --------------------------------------------------
# CORRELATION ANALYSIS
# --------------------------------------------------

print("\n--- HIGH CORRELATION PAIRS ---")

correlation_matrix = X.corr()

high_correlation_pairs = []

for i in range(len(feature_columns)):
    for j in range(i + 1, len(feature_columns)):

        correlation = correlation_matrix.iloc[i, j]

        if abs(correlation) >= 0.80:
            high_correlation_pairs.append(
                (
                    feature_columns[i],
                    feature_columns[j],
                    round(correlation, 3)
                )
            )

if high_correlation_pairs:
    for pair in high_correlation_pairs:
        print(pair)
else:
    print("No feature pairs with |correlation| >= 0.80")


# --------------------------------------------------
# NON-FINITE VALUE CHECK
# --------------------------------------------------

print("\n--- NON-FINITE VALUE CHECK ---")

non_finite_counts = (~np.isfinite(X)).sum()

print(non_finite_counts)


# --------------------------------------------------
# CLOSE DATABASE
# --------------------------------------------------

connection.close()

print("\nDatabase connection closed.")