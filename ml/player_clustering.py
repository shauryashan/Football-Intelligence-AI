import sqlite3
import pandas as pd

from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_FILE = PROJECT_ROOT / "database" / "football.db"
DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR.mkdir(exist_ok=True)


# ============================================================
# 2. CONNECT TO DATABASE
# ============================================================

connection = sqlite3.connect(DATABASE_FILE)

print("Connected to football.db")


# ============================================================
# 3. BUILD FINAL 15-FEATURE ML DATASET
# ============================================================

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

        -- Attacking
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
                THEN COALESCE(shot_xg, 0)
                ELSE 0
            END
        ) AS expected_goals,

        -- Passing
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
                THEN COALESCE(pass_length, 0)
                ELSE 0
            END
        ) AS pass_distance,

        -- Defensive
        SUM(
            CASE
                WHEN event_type = 'Pressure'
                THEN 1
                ELSE 0
            END
        ) AS pressures,

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

        -- Carrying / dribbling
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

        -- Duels
        SUM(
            CASE
                WHEN event_type = 'Duel'
                THEN 1
                ELSE 0
            END
        ) AS duels,

        -- Retention / recovery
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

    GROUP BY
        pass_event.player_id
)

SELECT
    p.player_id,
    p.player_name,

    ROUND(
        COALESCE(pe.shots, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS shots_per_90,

    ROUND(
        COALESCE(pe.expected_goals, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS xg_per_90,

    ROUND(
        COALESCE(pk.key_passes, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS key_passes_per_90,

    ROUND(
        COALESCE(pe.passes, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS passes_per_90,

    ROUND(
        COALESCE(pe.pass_distance, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS pass_distance_per_90,

    ROUND(
        COALESCE(pe.pressures, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS pressures_per_90,

    ROUND(
        COALESCE(pe.tackles, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS tackles_per_90,

    ROUND(
        COALESCE(pe.interceptions, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS interceptions_per_90,

    ROUND(
        COALESCE(pe.clearances, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS clearances_per_90,

    ROUND(
        COALESCE(pe.carries, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS carries_per_90,

    ROUND(
        COALESCE(pe.dribbles, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS dribbles_per_90,

    ROUND(
        COALESCE(pe.duels, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS duels_per_90,

    ROUND(
        COALESCE(pe.miscontrols, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS miscontrols_per_90,

    ROUND(
        COALESCE(pe.dispossessed, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS dispossessed_per_90,

    ROUND(
        COALESCE(pe.ball_recoveries, 0)
        / (pm.total_minutes / 90.0),
        4
    ) AS ball_recoveries_per_90

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

LEFT JOIN player_events pe
    ON pm.player_id = pe.player_id

LEFT JOIN player_key_passes pk
    ON pm.player_id = pk.player_id

WHERE
    pm.total_minutes >= 900

ORDER BY
    p.player_id;
"""


# ============================================================
# 4. LOAD DATA
# ============================================================

df = pd.read_sql_query(
    query,
    connection
)

connection.close()

print(f"Players loaded: {len(df)}")


# ============================================================
# 5. DEFINE FINAL ML FEATURES
# ============================================================

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

X = df[feature_columns]


# ============================================================
# 6. STANDARDIZE FEATURES
# ============================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

print(f"Features used: {len(feature_columns)}")
print("Features standardized")


# ============================================================
# 7. FINAL K-MEANS MODEL
# ============================================================

K = 5

model = KMeans(
    n_clusters=K,
    random_state=42,
    n_init=10
)

cluster_labels = model.fit_predict(X_scaled)

df["cluster"] = cluster_labels


# ============================================================
# 8. SILHOUETTE SCORE
# ============================================================

silhouette = silhouette_score(
    X_scaled,
    cluster_labels
)

print("\n--- FINAL CLUSTERING MODEL ---")

print(f"Algorithm: K-Means")
print(f"K: {K}")
print(f"Players: {len(df)}")
print(f"Features: {len(feature_columns)}")
print(f"Silhouette score: {silhouette:.4f}")


# ============================================================
# 9. ASSIGN ANALYTICAL ARCHETYPE NAMES
# ============================================================

cluster_names = {
    0: "Goalkeeper",
    1: "Two-Way / High-Volume",
    2: "Finishing Forward",
    3: "Creative Attacker",
    4: "Defensive Player"
}

df["archetype"] = df["cluster"].map(cluster_names)


# ============================================================
# 10. SAVE PLAYER CLUSTER ASSIGNMENTS
# ============================================================

player_clusters = df[
    [
        "player_id",
        "player_name",
        "cluster",
        "archetype"
    ]
].sort_values(
    ["cluster", "player_name"]
)

player_clusters_file = (
    DATA_DIR / "player_clusters.csv"
)

player_clusters.to_csv(
    player_clusters_file,
    index=False
)

print(
    f"\nSaved player clusters to: "
    f"{player_clusters_file}"
)


# ============================================================
# 11. BUILD CLUSTER PROFILES
# ============================================================

cluster_profiles = (
    df.groupby("cluster")[feature_columns]
    .mean()
    .round(4)
)

cluster_profiles.insert(
    0,
    "archetype",
    cluster_profiles.index.map(cluster_names)
)

cluster_profiles.insert(
    1,
    "player_count",
    df["cluster"].value_counts().sort_index()
)

cluster_profiles.insert(
    2,
    "population_percentage",
    (
        df["cluster"]
        .value_counts()
        .sort_index()
        / len(df)
        * 100
    ).round(2)
)


# ============================================================
# 12. SAVE CLUSTER PROFILES
# ============================================================

cluster_profiles_file = (
    DATA_DIR / "cluster_profiles.csv"
)

cluster_profiles.to_csv(
    cluster_profiles_file
)

print(
    f"Saved cluster profiles to: "
    f"{cluster_profiles_file}"
)


# ============================================================
# 13. PRINT CLUSTER SUMMARY
# ============================================================

print("\n--- FINAL CLUSTER SUMMARY ---")

for cluster in range(K):

    cluster_data = df[
        df["cluster"] == cluster
    ]

    print(
        f"\nCluster {cluster} — "
        f"{cluster_names[cluster]}"
    )

    print(
        f"Players: {len(cluster_data)}"
    )

    print(
        cluster_data[
            [
                "player_name",
                "cluster",
                "archetype"
            ]
        ]
        .sort_values("player_name")
        .head(15)
        .to_string(index=False)
    )


# ============================================================
# 14. FINAL VALIDATION
# ============================================================

print("\n--- FINAL ML3 VALIDATION ---")

print(
    f"Expected players: 316"
)

print(
    f"Actual players: {len(df)}"
)

print(
    f"Expected clusters: 5"
)

print(
    f"Actual clusters: "
    f"{df['cluster'].nunique()}"
)

print(
    f"Missing cluster labels: "
    f"{df['cluster'].isna().sum()}"
)

print(
    f"Missing archetype labels: "
    f"{df['archetype'].isna().sum()}"
)

print(
    f"Duplicate player IDs: "
    f"{df['player_id'].duplicated().sum()}"
)

print(
    f"Cluster assignment rows: "
    f"{len(player_clusters)}"
)

print(
    f"Cluster profile rows: "
    f"{len(cluster_profiles)}"
)


# ============================================================
# 15. CLUSTER COUNTS
# ============================================================

print("\n--- FINAL CLUSTER COUNTS ---")

final_counts = (
    df.groupby(
        ["cluster", "archetype"]
    )
    .size()
    .reset_index(name="player_count")
)

print(
    final_counts.to_string(index=False)
)


# ============================================================
# 16. FINAL STATUS
# ============================================================

validation_passed = (
    len(df) == 316
    and df["cluster"].nunique() == 5
    and df["cluster"].isna().sum() == 0
    and df["archetype"].isna().sum() == 0
    and df["player_id"].duplicated().sum() == 0
    and len(player_clusters) == 316
    and len(cluster_profiles) == 5
)

print("\n========================================")
print(
    f"ML3 FINAL VALIDATION: "
    f"{'PASSED' if validation_passed else 'FAILED'}"
)
print("========================================")