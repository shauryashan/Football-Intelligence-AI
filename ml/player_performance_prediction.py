import sqlite3
import numpy as np
import pandas as pd

from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


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
        kick_off
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

# Exact chronological match order
matches["match_order"] = np.arange(
    len(matches)
)

print(
    f"Matches loaded: {len(matches)}"
)


# ============================================================
# LOAD PLAYER-MATCH DATA
# ============================================================

player_match = pd.read_sql_query(
    """
    SELECT
        match_id,
        player_id,
        minutes_played
    FROM player_match
    WHERE minutes_played > 0
    """,
    connection
)

print(
    f"Player-match appearances loaded: "
    f"{len(player_match)}"
)


# ============================================================
# LOAD EVENTS
# ============================================================

events = pd.read_sql_query(
    """
    SELECT
        match_id,
        player_id,
        event_type,
        shot_xg
    FROM events
    WHERE player_id IS NOT NULL
    """,
    connection
)

print(
    f"Events loaded: {len(events)}"
)


# ============================================================
# BUILD PLAYER-MATCH EVENT FEATURES
# ============================================================

print(
    "\nBuilding player-match event features..."
)


event_counts = (
    events
    .groupby(
        [
            "match_id",
            "player_id",
            "event_type"
        ]
    )
    .size()
    .unstack(fill_value=0)
    .reset_index()
)


expected_events = [
    "Shot",
    "Pass",
    "Pressure",
    "Duel",
    "Carry",
    "Dribble",
    "Interception",
    "Clearance",
    "Miscontrol",
    "Dispossessed",
    "Ball Recovery"
]


for event_name in expected_events:

    if event_name not in event_counts.columns:

        event_counts[event_name] = 0


# ============================================================
# PLAYER-MATCH XG
# ============================================================

player_match_xg = (
    events[
        events["event_type"] == "Shot"
    ]
    .groupby(
        [
            "match_id",
            "player_id"
        ]
    )["shot_xg"]
    .sum()
    .reset_index(
        name="xg"
    )
)


# ============================================================
# MERGE PLAYER-MATCH + EVENTS
# ============================================================

model_df = player_match.merge(
    event_counts,
    on=[
        "match_id",
        "player_id"
    ],
    how="left"
)


model_df = model_df.merge(
    player_match_xg,
    on=[
        "match_id",
        "player_id"
    ],
    how="left"
)


for event_name in expected_events:

    model_df[event_name] = (
        model_df[event_name]
        .fillna(0)
    )


model_df["xg"] = (
    model_df["xg"]
    .fillna(0)
)


# ============================================================
# PER-90 FEATURES
# ============================================================

model_df["shots_per_90"] = (
    model_df["Shot"]
    / model_df["minutes_played"]
    * 90
)

model_df["xg_per_90"] = (
    model_df["xg"]
    / model_df["minutes_played"]
    * 90
)

model_df["passes_per_90"] = (
    model_df["Pass"]
    / model_df["minutes_played"]
    * 90
)

model_df["pressures_per_90"] = (
    model_df["Pressure"]
    / model_df["minutes_played"]
    * 90
)

model_df["duels_per_90"] = (
    model_df["Duel"]
    / model_df["minutes_played"]
    * 90
)

model_df["carries_per_90"] = (
    model_df["Carry"]
    / model_df["minutes_played"]
    * 90
)

model_df["dribbles_per_90"] = (
    model_df["Dribble"]
    / model_df["minutes_played"]
    * 90
)

model_df["interceptions_per_90"] = (
    model_df["Interception"]
    / model_df["minutes_played"]
    * 90
)

model_df["clearances_per_90"] = (
    model_df["Clearance"]
    / model_df["minutes_played"]
    * 90
)

model_df["miscontrols_per_90"] = (
    model_df["Miscontrol"]
    / model_df["minutes_played"]
    * 90
)

model_df["dispossessed_per_90"] = (
    model_df["Dispossessed"]
    / model_df["minutes_played"]
    * 90
)

model_df["ball_recoveries_per_90"] = (
    model_df["Ball Recovery"]
    / model_df["minutes_played"]
    * 90
)


# ============================================================
# MERGE MATCH ORDER
# ============================================================

model_df = model_df.merge(
    matches[
        [
            "match_id",
            "match_date",
            "kick_off",
            "match_order"
        ]
    ],
    on="match_id",
    how="left"
)


model_df = model_df.sort_values(
    [
        "player_id",
        "match_order"
    ]
).reset_index(drop=True)


# ============================================================
# MODEL FEATURES
# ============================================================

feature_columns = [

    "shots_per_90",
    "xg_per_90",
    "passes_per_90",
    "pressures_per_90",
    "duels_per_90",
    "carries_per_90",
    "dribbles_per_90",
    "interceptions_per_90",
    "clearances_per_90",
    "miscontrols_per_90",
    "dispossessed_per_90",
    "ball_recoveries_per_90"

]


# ============================================================
# BUILD PREVIOUS-5 → FUTURE-5 SNAPSHOTS
# ============================================================

print(
    "\nBuilding previous-5 → future-5 prediction snapshots..."
)


snapshots = []


for player_id, player_data in model_df.groupby(
    "player_id"
):

    player_data = (
        player_data
        .sort_values("match_order")
        .reset_index(drop=True)
    )


    # Need at least 10 appearances:
    #
    # 5 historical
    # +
    # 5 future

    if len(player_data) < 10:

        continue


    for i in range(
        5,
        len(player_data) - 4
    ):

        previous_five = (
            player_data.iloc[
                i - 5:i
            ]
        )


        future_five = (
            player_data.iloc[
                i:i + 5
            ]
        )


        if len(previous_five) != 5:
            continue

        if len(future_five) != 5:
            continue


        # ----------------------------------------------------
        # Historical features
        # ----------------------------------------------------

        historical_features = (
            previous_five[
                feature_columns
            ]
            .mean()
        )


        historical_minutes = (
            previous_five[
                "minutes_played"
            ]
            .sum()
        )


        # ----------------------------------------------------
        # Future target
        #
        # IMPORTANT:
        # This is TOTAL xG across the next 5
        # appearances, not xG/90.
        # ----------------------------------------------------

        future_total_xg = (
            future_five[
                "xg"
            ]
            .sum()
        )


        snapshot = {

            "player_id":
                player_id,

            "history_start_order":
                previous_five.iloc[0][
                    "match_order"
                ],

            "history_end_order":
                previous_five.iloc[-1][
                    "match_order"
                ],

            "target_start_order":
                future_five.iloc[0][
                    "match_order"
                ],

            "target_end_order":
                future_five.iloc[-1][
                    "match_order"
                ],

            "target_match_id":
                future_five.iloc[0][
                    "match_id"
                ],

            "target_match_date":
                future_five.iloc[0][
                    "match_date"
                ],

            "historical_minutes":
                historical_minutes,

            "target_future_xg":
                future_total_xg

        }


        for feature in feature_columns:

            snapshot[feature] = (
                historical_features[
                    feature
                ]
            )


        snapshots.append(
            snapshot
        )


prediction_df = pd.DataFrame(
    snapshots
)


print(
    f"Prediction snapshots available: "
    f"{len(prediction_df)}"
)


# ============================================================
# BASIC SNAPSHOT VALIDATION
# ============================================================

print(
    "\n--- SNAPSHOT VALIDATION ---"
)


print(
    "Snapshots with exactly 5 historical appearances: "
    "True"
)

print(
    "Snapshots with exactly 5 future appearances: "
    "True"
)


# ============================================================
# TEMPORAL FEATURE VALIDATION
# ============================================================

print(
    "\n--- TEMPORAL FEATURE CHECK ---"
)


historical_before_target = (
    prediction_df[
        "history_end_order"
    ]
    <
    prediction_df[
        "target_start_order"
    ]
)


print(
    "All historical appearances occur before "
    "the future target window:",
    historical_before_target.all()
)


# ============================================================
# DETERMINE STRICT MATCH CUTOFF
# ============================================================

# We use the full 380-match season to establish
# an 80/20 chronological cutoff.

total_matches = len(matches)

split_index = int(
    total_matches * 0.80
)


training_cutoff_order = (
    split_index - 1
)

testing_start_order = (
    split_index
)


print(
    "\n--- STRICT CHRONOLOGICAL CUTOFF ---"
)


print(
    "Total matches:",
    total_matches
)

print(
    "Training cutoff match order:",
    training_cutoff_order
)

print(
    "Testing starts at match order:",
    testing_start_order
)


# ============================================================
# STRICT TRAINING / TESTING SPLIT
# ============================================================
#
# We split using the actual target windows.
#
# Training:
#   The ENTIRE future 5-appearance target window
#   must finish before the test period.
#
# Testing:
#   The ENTIRE future 5-appearance target window
#   must start after the training period.
#
# This prevents a training target from crossing
# into the testing period.
# ============================================================

print(
    "\n--- STRICT CHRONOLOGICAL SPLIT ---"
)


# Use the chronological match order of the
# actual target matches represented by snapshots.

snapshot_target_orders = np.sort(
    prediction_df[
        "target_start_order"
    ].unique()
)


# 80% / 20% chronological cutoff based on
# available prediction snapshots.

snapshot_split_index = int(
    len(snapshot_target_orders) * 0.80
)


testing_start_order = (
    snapshot_target_orders[
        snapshot_split_index
    ]
)


print(
    "First testing target-start match order:",
    testing_start_order
)


# ------------------------------------------------------------
# TRAINING SNAPSHOTS
# ------------------------------------------------------------
#
# The entire future target window must finish
# BEFORE the testing period begins.

train_df = prediction_df[
    prediction_df[
        "target_end_order"
    ]
    <
    testing_start_order
].copy()


# ------------------------------------------------------------
# TESTING SNAPSHOTS
# ------------------------------------------------------------
#
# The entire future target window must start
# AT OR AFTER the testing period begins.

test_df = prediction_df[
    prediction_df[
        "target_start_order"
    ]
    >=
    testing_start_order
].copy()


print(
    f"Training snapshots: {len(train_df)}"
)

print(
    f"Testing snapshots: {len(test_df)}"
)


# ============================================================
# STRICT TEMPORAL VALIDATION
# ============================================================

print(
    "\n--- STRICT TEMPORAL VALIDATION ---"
)


if len(train_df) > 0:

    latest_training_target = (
        train_df[
            "target_end_order"
        ].max()
    )

else:

    latest_training_target = -1


if len(test_df) > 0:

    earliest_testing_target = (
        test_df[
            "target_start_order"
        ].min()
    )

else:

    earliest_testing_target = -1


print(
    "Latest match used by any training target:",
    latest_training_target
)

print(
    "First match used by any testing target:",
    earliest_testing_target
)


target_windows_do_not_overlap = (
    latest_training_target
    <
    earliest_testing_target
)


print(
    "Target-window overlap:",
    0
    if target_windows_do_not_overlap
    else 1
)


print(
    "Training target windows entirely before testing:",
    target_windows_do_not_overlap
)


# ============================================================
# TRAINING / TESTING PERIODS
# ============================================================

print(
    "\n--- TRAINING / TESTING PERIODS ---"
)


if len(train_df) > 0:

    print(
        "Training target period:",
        train_df[
            "target_match_date"
        ].min().date(),
        "to",
        train_df[
            "target_match_date"
        ].max().date()
    )


if len(test_df) > 0:

    print(
        "Testing target period:",
        test_df[
            "target_match_date"
        ].min().date(),
        "to",
        test_df[
            "target_match_date"
        ].max().date()
    )


# ============================================================
# TRAINING / TESTING PERIODS
# ============================================================

print(
    "\n--- TRAINING / TESTING PERIODS ---"
)


if len(train_df) > 0:

    print(
        "Training target period:",
        train_df[
            "target_match_date"
        ].min().date(),
        "to",
        train_df[
            "target_match_date"
        ].max().date()
    )


if len(test_df) > 0:

    print(
        "Testing target period:",
        test_df[
            "target_match_date"
        ].min().date(),
        "to",
        test_df[
            "target_match_date"
        ].max().date()
    )


# ============================================================
# PREPARE X / y
# ============================================================

X_train = train_df[
    feature_columns
]

X_test = test_df[
    feature_columns
]


y_train = train_df[
    "target_future_xg"
]

y_test = test_df[
    "target_future_xg"
]


# ============================================================
# MISSING VALUE CHECK
# ============================================================

missing_train_features = (
    X_train
    .isna()
    .sum()
    .sum()
)


missing_test_features = (
    X_test
    .isna()
    .sum()
    .sum()
)


missing_train_target = (
    y_train
    .isna()
    .sum()
)


missing_test_target = (
    y_test
    .isna()
    .sum()
)


# ============================================================
# SCALE FOR LINEAR REGRESSION
# ============================================================

scaler = StandardScaler()


X_train_scaled = (
    scaler.fit_transform(
        X_train
    )
)


X_test_scaled = (
    scaler.transform(
        X_test
    )
)


# ============================================================
# LINEAR REGRESSION
# ============================================================

print(
    "\nTraining Linear Regression..."
)


linear_model = LinearRegression()


linear_model.fit(
    X_train_scaled,
    y_train
)


linear_predictions = (
    linear_model.predict(
        X_test_scaled
    )
)


linear_mae = (
    mean_absolute_error(
        y_test,
        linear_predictions
    )
)


linear_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        linear_predictions
    )
)


linear_r2 = (
    r2_score(
        y_test,
        linear_predictions
    )
)


print(
    "\n--- LINEAR REGRESSION ---"
)

print(
    f"MAE:  {linear_mae:.4f}"
)

print(
    f"RMSE: {linear_rmse:.4f}"
)

print(
    f"R²:   {linear_r2:.4f}"
)


# ============================================================
# RANDOM FOREST
# ============================================================

print(
    "\nTraining Random Forest..."
)


rf_model = RandomForestRegressor(

    n_estimators=300,

    max_depth=8,

    min_samples_leaf=10,

    random_state=42,

    n_jobs=-1

)


# Random Forest does not require scaling.

rf_model.fit(
    X_train,
    y_train
)


rf_predictions = (
    rf_model.predict(
        X_test
    )
)


rf_mae = (
    mean_absolute_error(
        y_test,
        rf_predictions
    )
)


rf_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        rf_predictions
    )
)


rf_r2 = (
    r2_score(
        y_test,
        rf_predictions
    )
)


print(
    "\n--- RANDOM FOREST ---"
)

print(
    f"MAE:  {rf_mae:.4f}"
)

print(
    f"RMSE: {rf_rmse:.4f}"
)

print(
    f"R²:   {rf_r2:.4f}"
)


# ============================================================
# MEAN BASELINE
# ============================================================

training_mean = (
    y_train.mean()
)


baseline_predictions = np.full(
    len(y_test),
    training_mean
)


baseline_mae = (
    mean_absolute_error(
        y_test,
        baseline_predictions
    )
)


baseline_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        baseline_predictions
    )
)


baseline_r2 = (
    r2_score(
        y_test,
        baseline_predictions
    )
)


print(
    "\n--- BASELINE COMPARISON ---"
)


print(
    f"Training mean future xG: "
    f"{training_mean:.4f}"
)


print(
    f"Baseline MAE:  "
    f"{baseline_mae:.4f}"
)


print(
    f"Baseline RMSE: "
    f"{baseline_rmse:.4f}"
)


print(
    f"Baseline R²:   "
    f"{baseline_r2:.4f}"
)


# ============================================================
# MODEL IMPROVEMENT
# ============================================================

mae_improvement = (
    (
        baseline_mae
        -
        rf_mae
    )
    /
    baseline_mae
    * 100
)


rmse_improvement = (
    (
        baseline_rmse
        -
        rf_rmse
    )
    /
    baseline_rmse
    * 100
)


print(
    "\n--- RANDOM FOREST IMPROVEMENT ---"
)


print(
    f"MAE improvement: "
    f"{mae_improvement:.2f}%"
)


print(
    f"RMSE improvement: "
    f"{rmse_improvement:.2f}%"
)


# ============================================================
# TARGET DISTRIBUTION
# ============================================================

print(
    "\n--- TARGET DISTRIBUTION ---"
)


print(
    "Training target:"
)

print(
    y_train.describe()
)


print(
    "\nTesting target:"
)

print(
    y_test.describe()
)


# ============================================================
# PREDICTION RANGE
# ============================================================

print(
    "\n--- PREDICTION RANGE ---"
)


print(
    "Linear minimum:",
    f"{linear_predictions.min():.4f}"
)

print(
    "Linear maximum:",
    f"{linear_predictions.max():.4f}"
)

print(
    "Random Forest minimum:",
    f"{rf_predictions.min():.4f}"
)

print(
    "Random Forest maximum:",
    f"{rf_predictions.max():.4f}"
)


# ============================================================
# RANDOM FOREST FEATURE IMPORTANCE
# ============================================================

feature_importance = pd.DataFrame({

    "feature":
        feature_columns,

    "importance":
        rf_model.feature_importances_

})


feature_importance = (
    feature_importance
    .sort_values(
        "importance",
        ascending=False
    )
)


print(
    "\n--- RANDOM FOREST FEATURE IMPORTANCE ---"
)


print(
    feature_importance.to_string(
        index=False
    )
)


# ============================================================
# SAMPLE PREDICTIONS
# ============================================================

sample_predictions = test_df[
    [
        "player_id",
        "target_match_id",
        "target_match_date"
    ]
].copy()


sample_predictions[
    "target_future_xg"
] = y_test.values


sample_predictions[
    "predicted_future_xg"
] = rf_predictions


sample_predictions[
    "prediction_error"
] = (

    sample_predictions[
        "target_future_xg"
    ]

    -

    sample_predictions[
        "predicted_future_xg"
    ]

)


print(
    "\n--- SAMPLE FUTURE PREDICTIONS ---"
)


print(
    sample_predictions
    .head(15)
    .to_string(index=False)
)


# ============================================================
# FINAL VALIDATION
# ============================================================

print(
    "\n--- ML4 FINAL VALIDATION ---"
)


print(
    "Total player-match rows:",
    len(player_match)
)

print(
    "Prediction snapshots:",
    len(prediction_df)
)

print(
    "Training snapshots:",
    len(train_df)
)

print(
    "Testing snapshots:",
    len(test_df)
)

print(
    "Missing training features:",
    missing_train_features
)

print(
    "Missing testing features:",
    missing_test_features
)

print(
    "Missing training targets:",
    missing_train_target
)

print(
    "Missing testing targets:",
    missing_test_target
)

print(
    "Historical features before target:",
    historical_before_target.all()
)

print(
    "Target-window overlap:",
    0
    if target_windows_do_not_overlap
    else 1
)

print(
    "Training targets entirely before testing:",
    target_windows_do_not_overlap
)

print(
    "Linear non-finite predictions:",
    not np.isfinite(
        linear_predictions
    ).all()
)

print(
    "Random Forest non-finite predictions:",
    not np.isfinite(
        rf_predictions
    ).all()
)


technical_validation_passed = (

    len(prediction_df) > 0

    and len(train_df) > 0

    and len(test_df) > 0

    and missing_train_features == 0

    and missing_test_features == 0

    and missing_train_target == 0

    and missing_test_target == 0

    and historical_before_target.all()

    and target_windows_do_not_overlap

    and np.isfinite(
        linear_predictions
    ).all()

    and np.isfinite(
        rf_predictions
    ).all()

)


print(
    "\n========================================"
)


if technical_validation_passed:

    print(
        "ML4 STRICT TECHNICAL VALIDATION: PASSED"
    )

else:

    print(
        "ML4 STRICT TECHNICAL VALIDATION: FAILED"
    )


print(
    "========================================"
)


connection.close()


print(
    "\nDatabase connection closed."
)