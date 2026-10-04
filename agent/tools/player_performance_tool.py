import sqlite3
import json
import numpy as np
import pandas as pd

from pathlib import Path
from sklearn.ensemble import RandomForestRegressor


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATABASE_FILE = PROJECT_ROOT / "database" / "football.db"


# ============================================================
# MODEL FEATURES
# ============================================================

FEATURE_COLUMNS = [
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
# PLAYER PERFORMANCE PREDICTION
# ============================================================

def predict_player_future_xg(player_name):

    connection = sqlite3.connect(DATABASE_FILE)

    try:

        # --------------------------------------------------
        # LOAD MATCHES
        # --------------------------------------------------

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

        matches = (
            matches
            .sort_values(
                [
                    "match_date",
                    "kick_off",
                    "match_id"
                ]
            )
            .reset_index(drop=True)
        )

        matches["match_order"] = np.arange(
            len(matches)
        )


        # --------------------------------------------------
        # LOAD PLAYER-MATCH DATA
        # --------------------------------------------------

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


        # --------------------------------------------------
        # LOAD EVENTS
        # --------------------------------------------------

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


        # --------------------------------------------------
        # BUILD EVENT FEATURES
        # --------------------------------------------------

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


        # --------------------------------------------------
        # PLAYER-MATCH XG
        # --------------------------------------------------

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


        # --------------------------------------------------
        # MERGE
        # --------------------------------------------------

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


        # --------------------------------------------------
        # PER-90 FEATURES
        # --------------------------------------------------

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


        # --------------------------------------------------
        # MATCH ORDER
        # --------------------------------------------------

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

        model_df = (
            model_df
            .sort_values(
                [
                    "player_id",
                    "match_order"
                ]
            )
            .reset_index(drop=True)
        )


        # --------------------------------------------------
        # FIND PLAYER
        # --------------------------------------------------

        players = pd.read_sql_query(
            """
            SELECT
                player_id,
                player_name
            FROM players
            """,
            connection
        )

        matches_player = players[
            players["player_name"].str.lower()
            == player_name.lower()
        ]

        if matches_player.empty:

            return {
                "error": (
                    f"Player not found: {player_name}"
                )
            }

        player_id = matches_player.iloc[0]["player_id"]

        actual_player_name = (
            matches_player.iloc[0]["player_name"]
        )


        # --------------------------------------------------
        # PLAYER HISTORY
        # --------------------------------------------------

        player_data = model_df[
            model_df["player_id"] == player_id
        ].copy()

        player_data = (
            player_data
            .sort_values("match_order")
            .reset_index(drop=True)
        )


        # Need at least 10 appearances
        if len(player_data) < 10:

            return {
                "player": actual_player_name,
                "error": (
                    "Insufficient appearance history "
                    "for the validated previous-5 → future-5 "
                    "prediction setup."
                )
            }


        # --------------------------------------------------
        # BUILD ALL SNAPSHOTS
        # --------------------------------------------------

        snapshots = []

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

            historical_features = (
                previous_five[
                    FEATURE_COLUMNS
                ]
                .mean()
            )

            future_total_xg = (
                future_five["xg"].sum()
            )

            snapshot = {
                "target_future_xg":
                    future_total_xg
            }

            for feature in FEATURE_COLUMNS:

                snapshot[feature] = (
                    historical_features[feature]
                )

            snapshots.append(snapshot)


        prediction_df = pd.DataFrame(
            snapshots
        )


        if len(prediction_df) < 2:

            return {
                "player": actual_player_name,
                "error": (
                    "Insufficient prediction snapshots "
                    "for model training."
                )
            }


        # --------------------------------------------------
        # CHRONOLOGICAL SNAPSHOT SPLIT
        # --------------------------------------------------

        split_index = int(
            len(prediction_df) * 0.80
        )

        if split_index <= 0:
            split_index = 1

        if split_index >= len(prediction_df):
            split_index = len(prediction_df) - 1

        train_df = prediction_df.iloc[
            :split_index
        ].copy()

        # Latest available snapshot is the prediction target
        prediction_snapshot = (
            prediction_df.iloc[-1]
        )


        # --------------------------------------------------
        # TRAIN RANDOM FOREST
        # --------------------------------------------------

        X_train = train_df[
            FEATURE_COLUMNS
        ]

        y_train = train_df[
            "target_future_xg"
        ]

        X_prediction = (
            prediction_snapshot[
                FEATURE_COLUMNS
            ]
            .to_frame()
            .T
        )

        rf_model = RandomForestRegressor(
            n_estimators=300,
            max_depth=8,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1
        )

        rf_model.fit(
            X_train,
            y_train
        )


        # --------------------------------------------------
        # PREDICTION
        # --------------------------------------------------

        prediction = rf_model.predict(
            X_prediction
        )[0]


        # --------------------------------------------------
        # RETURN
        # --------------------------------------------------

        return {
            "player": actual_player_name,
            "prediction": round(
                float(prediction),
                4
            ),
            "target": (
                "total xG across the next "
                "5 appearances"
            ),
            "historical_window": (
                "previous 5 appearances"
            ),
            "model": (
                "Random Forest Regressor"
            ),
            "model_configuration": {
                "n_estimators": 300,
                "max_depth": 8,
                "min_samples_leaf": 10,
                "random_state": 42
            }
        }

    finally:

        connection.close()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = predict_player_future_xg(
        "Kevin De Bruyne"
    )

    print("\n" + "=" * 60)
    print("PLAYER PERFORMANCE PREDICTION TOOL")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )