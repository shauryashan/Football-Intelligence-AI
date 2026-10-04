import sqlite3
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity


from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_FILE = PROJECT_ROOT / "database" / "football.db"


# --------------------------------------------------
# 1. CONNECT TO DATABASE
# --------------------------------------------------

connection = sqlite3.connect(DATABASE_FILE)

print("Connected to football.db")


# --------------------------------------------------
# 2. LOAD PLAYER FEATURES AND ROLES
# --------------------------------------------------

query = """
WITH player_minutes AS (

    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes

    FROM player_match

    GROUP BY player_id
),

position_minutes AS (

    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes

    FROM player_match

    WHERE position IS NOT NULL

    GROUP BY
        player_id,
        position
),

primary_position AS (

    SELECT
        player_id,
        position

    FROM (

        SELECT
            player_id,
            position,
            position_minutes,

            ROW_NUMBER() OVER (
                PARTITION BY player_id
                ORDER BY position_minutes DESC
            ) AS position_rank

        FROM position_minutes

    )

    WHERE position_rank = 1
),

player_roles AS (

    SELECT
        player_id,

        CASE
            WHEN position LIKE '%Goalkeeper%'
                THEN 'Goalkeeper'

            WHEN position LIKE '%Center Back%'
                THEN 'Centre Back'

            WHEN position LIKE '%Left Back%'
              OR position LIKE '%Right Back%'
              OR position LIKE '%Wing Back%'
                THEN 'Full Back'

            WHEN position LIKE '%Defensive Midfield%'
                THEN 'Defensive Midfielder'

            WHEN position LIKE '%Central Midfield%'
                THEN 'Central Midfielder'

            WHEN position LIKE '%Attacking Midfield%'
                THEN 'Attacking Midfielder'

            WHEN position LIKE '%Left Wing%'
              OR position LIKE '%Right Wing%'
              OR position LIKE '%Wing%'
                THEN 'Winger'

            WHEN position LIKE '%Center Forward%'
              OR position LIKE '%Striker%'
              OR position LIKE '%Forward%'
                THEN 'Forward'

            ELSE 'Other'

        END AS role_group

    FROM primary_position
),

player_events AS (

    SELECT
        player_id,

        SUM(
            CASE
                WHEN event_type = 'Shot'
                THEN 1
                ELSE 0
            END
        ) AS shots,

        SUM(
            CASE
                WHEN event_type = 'Shot'
                THEN shot_xg
                ELSE 0
            END
        ) AS xg,

        SUM(
            CASE
                WHEN event_type = 'Pass'
                THEN 1
                ELSE 0
            END
        ) AS passes,

        SUM(
            CASE
                WHEN event_type = 'Pass'
                AND pass_outcome IS NULL
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

        SUM(
            CASE
                WHEN event_type = 'Pressure'
                THEN 1
                ELSE 0
            END
        ) AS pressures,

        SUM(
            CASE
                WHEN event_type = 'Tackle'
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

        SUM(
            CASE
                WHEN event_type = 'Carry'
                THEN 1
                ELSE 0
            END
        ) AS carries,

        SUM(
            CASE
                WHEN event_type = 'Dribble'
                THEN 1
                ELSE 0
            END
        ) AS dribbles,

        SUM(
            CASE
                WHEN event_type = 'Duel'
                THEN 1
                ELSE 0
            END
        ) AS duels,

        SUM(
            CASE
                WHEN event_type = 'Miscontrol'
                THEN 1
                ELSE 0
            END
        ) AS miscontrols,

        SUM(
            CASE
                WHEN event_type = 'Dispossessed'
                THEN 1
                ELSE 0
            END
        ) AS dispossessed,

        SUM(
            CASE
                WHEN event_type = 'Ball Recovery'
                THEN 1
                ELSE 0
            END
        ) AS ball_recoveries

    FROM events

    WHERE player_id IS NOT NULL

    GROUP BY player_id
),

player_key_passes AS (

    SELECT
        player_id,
        COUNT(*) AS key_passes

    FROM events

    WHERE event_type = 'Pass'
      AND pass_recipient_id IS NOT NULL

    GROUP BY player_id
)

SELECT
    p.player_id,
    p.player_name,

    pr.role_group,

    pm.total_minutes,

    90.0 * COALESCE(pe.shots, 0)
        / pm.total_minutes
        AS shots_per_90,

    90.0 * COALESCE(pe.xg, 0)
        / pm.total_minutes
        AS xg_per_90,

    90.0 * COALESCE(pk.key_passes, 0)
        / pm.total_minutes
        AS key_passes_per_90,

    90.0 * COALESCE(pe.passes, 0)
        / pm.total_minutes
        AS passes_per_90,

    90.0 * COALESCE(pe.pass_distance, 0)
        / pm.total_minutes
        AS pass_distance_per_90,

    90.0 * COALESCE(pe.pressures, 0)
        / pm.total_minutes
        AS pressures_per_90,

    90.0 * COALESCE(pe.tackles, 0)
        / pm.total_minutes
        AS tackles_per_90,

    90.0 * COALESCE(pe.interceptions, 0)
        / pm.total_minutes
        AS interceptions_per_90,

    90.0 * COALESCE(pe.clearances, 0)
        / pm.total_minutes
        AS clearances_per_90,

    90.0 * COALESCE(pe.carries, 0)
        / pm.total_minutes
        AS carries_per_90,

    90.0 * COALESCE(pe.dribbles, 0)
        / pm.total_minutes
        AS dribbles_per_90,

    90.0 * COALESCE(pe.duels, 0)
        / pm.total_minutes
        AS duels_per_90,

    90.0 * COALESCE(pe.miscontrols, 0)
        / pm.total_minutes
        AS miscontrols_per_90,

    90.0 * COALESCE(pe.dispossessed, 0)
        / pm.total_minutes
        AS dispossessed_per_90,

    90.0 * COALESCE(pe.ball_recoveries, 0)
        / pm.total_minutes
        AS ball_recoveries_per_90

FROM players p

JOIN player_minutes pm
    ON p.player_id = pm.player_id

LEFT JOIN player_roles pr
    ON p.player_id = pr.player_id

LEFT JOIN player_events pe
    ON p.player_id = pe.player_id

LEFT JOIN player_key_passes pk
    ON p.player_id = pk.player_id

WHERE pm.total_minutes >= 900

ORDER BY p.player_name;
"""


df = pd.read_sql_query(query, connection)


# --------------------------------------------------
# 3. DEFINE ML FEATURES
# --------------------------------------------------

feature_columns = [
    "shots_per_90",
    "xg_per_90",
    "key_passes_per_90",
    "passes_per_90",
    "pass_distance_per_90",
    "pressures_per_90",
    "tackles_per_90",
    "interceptions_per_90",
    "clearances_per_90",
    "carries_per_90",
    "dribbles_per_90",
    "duels_per_90",
    "miscontrols_per_90",
    "dispossessed_per_90",
    "ball_recoveries_per_90"
]


# --------------------------------------------------
# 4. BASIC DATA VALIDATION
# --------------------------------------------------

print("\n--- DATA VALIDATION ---")

print("Players:", len(df))
print("Features:", len(feature_columns))

print(
    "Missing feature values:",
    df[feature_columns].isna().sum().sum()
)

print(
    "Missing roles:",
    df["role_group"].isna().sum()
)

print(
    "Duplicate player IDs:",
    df["player_id"].duplicated().sum()
)


# --------------------------------------------------
# 5. STANDARDIZE FEATURES
# --------------------------------------------------

X = df[feature_columns]

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# --------------------------------------------------
# 6. CALCULATE COSINE SIMILARITY
# --------------------------------------------------

similarity_matrix = cosine_similarity(X_scaled)


# --------------------------------------------------
# 7. TEST MULTIPLE ROLES
# --------------------------------------------------

test_players = [
    "Daley Blind",
    "Abdul Rahman Baba",
    "Kevin De Bruyne",
    "Dimitri Payet",
    "Jamie Vardy"
]


print("\n========================================")
print("ROLE-AWARE SIMILARITY VALIDATION")
print("========================================")


validation_passed = True


for player_name in test_players:

    matches = df[
        df["player_name"].str.lower()
        == player_name.lower()
    ]

    if matches.empty:

        print(
            f"\nERROR: {player_name} not found"
        )

        validation_passed = False
        continue

    player_index = matches.index[0]

    player_role = df.loc[
        player_index,
        "role_group"
    ]

    player_position = df.index.get_loc(
        player_index
    )

    similarities = similarity_matrix[
        player_position
    ]

    # Only compare against the same role
    role_indices = df.index[
        df["role_group"] == player_role
    ]

    results = []

    for index in role_indices:

        if index == player_index:
            continue

        matrix_position = df.index.get_loc(
            index
        )

        results.append({
            "player_name":
                df.loc[index, "player_name"],

            "role_group":
                df.loc[index, "role_group"],

            "similarity":
                similarities[matrix_position]
        })

    results_df = (
        pd.DataFrame(results)
        .sort_values(
            "similarity",
            ascending=False
        )
        .head(5)
    )

    print(
        f"\nPlayer: {player_name}"
    )

    print(
        f"Role: {player_role}"
    )

    print(
        "\nTop 5 similar players:"
    )

    print(
        results_df.to_string(
            index=False
        )
    )

    # --------------------------------------------------
    # VALIDATE RESULTS
    # --------------------------------------------------

    if len(results_df) == 0:

        print(
            "ERROR: No similar players returned"
        )

        validation_passed = False

    elif not all(
        results_df["role_group"]
        == player_role
    ):

        print(
            "ERROR: Different role found!"
        )

        validation_passed = False

    elif player_name in (
        results_df["player_name"].tolist()
    ):

        print(
            "ERROR: Player matched with themselves!"
        )

        validation_passed = False

    else:

        print(
            "Validation: PASSED"
        )


# --------------------------------------------------
# 8. FINAL VALIDATION
# --------------------------------------------------

print("\n========================================")
print("FINAL SIMILARITY VALIDATION")
print("========================================")

print(
    "Expected players: 316"
)

print(
    "Actual players:",
    len(df)
)

print(
    "Expected features: 15"
)

print(
    "Actual features:",
    len(feature_columns)
)

print(
    "Missing feature values:",
    df[feature_columns].isna().sum().sum()
)

print(
    "Missing roles:",
    df["role_group"].isna().sum()
)

print(
    "Duplicate player IDs:",
    df["player_id"].duplicated().sum()
)


if (
    len(df) == 316
    and len(feature_columns) == 15
    and df[feature_columns].isna().sum().sum() == 0
    and df["role_group"].isna().sum() == 0
    and df["player_id"].duplicated().sum() == 0
    and validation_passed
):

    print(
        "\nROLE-AWARE PLAYER SIMILARITY: PASSED"
    )

else:

    print(
        "\nROLE-AWARE PLAYER SIMILARITY: FAILED"
    )


# --------------------------------------------------
# 9. CLOSE DATABASE
# --------------------------------------------------

connection.close()

print("\nDatabase connection closed.")