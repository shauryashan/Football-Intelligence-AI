import json

import numpy as np
import pandas as pd

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "match_outcome_features.csv"
)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

TARGET = "match_result"

TARGET_CLASSES = [
    "HOME_WIN",
    "DRAW",
    "AWAY_WIN",
]


COMPACT_FEATURES = [
    "form_points_diff",
    "goals_for_diff",
    "goals_against_diff",
    "shots_diff",
    "xg_diff",
    "passes_diff",
    "pressures_diff",
    "carries_diff",
    "duels_diff",
    "interceptions_diff",
    "clearances_diff",
    "home_away_xg_diff",
]


# ============================================================
# MATCH OUTCOME PREDICTION
# ============================================================

def predict_match_outcome(match_id):

    model_df = pd.read_csv(
        INPUT_FILE
    )

    model_df = (
        model_df
        .sort_values("match_order")
        .reset_index(drop=True)
    )


    # --------------------------------------------------------
    # Validate requested match
    # --------------------------------------------------------

    match_rows = model_df[
        model_df["match_id"] == match_id
    ]

    if match_rows.empty:

        return {
            "error": (
                f"Match ID {match_id} is not available "
                "in the validated ML5 feature dataset."
            )
        }


    # --------------------------------------------------------
    # Chronological train/test split
    # --------------------------------------------------------

    split_index = int(
        len(model_df) * 0.80
    )

    train_df = model_df.iloc[
        :split_index
    ].copy()

    test_df = model_df.iloc[
        split_index:
    ].copy()


    # --------------------------------------------------------
    # Ensure requested match is in held-out test period
    # --------------------------------------------------------

    match_order = (
        match_rows.iloc[0]["match_order"]
    )

    testing_start_order = (
        test_df["match_order"].min()
    )

    if match_order < testing_start_order:

        return {
            "error": (
                f"Match ID {match_id} belongs to the "
                "training period and is therefore not "
                "eligible for an unbiased held-out prediction."
            )
        }


    # --------------------------------------------------------
    # Prepare training data
    # --------------------------------------------------------

    X_train = train_df[
        COMPACT_FEATURES
    ]

    y_train = train_df[
        TARGET
    ]


    # --------------------------------------------------------
    # Train validated Random Forest
    # --------------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train
    )


    # --------------------------------------------------------
    # Prepare requested match
    # --------------------------------------------------------

    match_features = match_rows[
        COMPACT_FEATURES
    ]


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = model.predict(
        match_features
    )[0]

    probabilities = model.predict_proba(
        match_features
    )[0]


    probability_map = {
        class_name: 0.0
        for class_name in TARGET_CLASSES
    }

    for index, class_name in enumerate(
        model.classes_
    ):

        probability_map[class_name] = round(
            float(probabilities[index]),
            4
        )


    # --------------------------------------------------------
    # Match information
    # --------------------------------------------------------

    match = match_rows.iloc[0]


    return {
        "match_id": int(match["match_id"]),
        "match_date": str(match["match_date"]),
        "home_team_id": int(match["home_team_id"]),
        "away_team_id": int(match["away_team_id"]),
        "predicted_result": prediction,
        "probabilities": probability_map,
        "model": "Random Forest Classifier",
        "feature_set": "12-feature compact ML5 model",
        "validation": (
            "Prediction generated using the chronological "
            "training period and evaluated on the held-out "
            "test period."
        )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    model_df = pd.read_csv(INPUT_FILE)

    model_df = (
        model_df
        .sort_values("match_order")
        .reset_index(drop=True)
    )

    split_index = int(len(model_df) * 0.80)

    test_matches = model_df.iloc[
        split_index:
    ][[
        "match_id",
        "match_date",
        "home_team_id",
        "away_team_id",
        "match_order"
    ]]

    print("\n--- AVAILABLE HELD-OUT TEST MATCHES ---")
    print(
        test_matches.head(10).to_string(
            index=False
        )
    )

    test_match_id = int(
        test_matches.iloc[0]["match_id"]
    )

    result = predict_match_outcome(
        test_match_id
    )

    print("\n" + "=" * 60)
    print("MATCH OUTCOME PREDICTION TOOL")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )