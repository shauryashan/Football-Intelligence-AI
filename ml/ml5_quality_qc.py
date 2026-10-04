import numpy as np
import pandas as pd

from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    log_loss,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "match_outcome_features.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading validated ML5 feature dataset...")

model_df = pd.read_csv(INPUT_FILE)

model_df = (
    model_df
    .sort_values("match_order")
    .reset_index(drop=True)
)

print(
    f"Matches loaded: {len(model_df)}"
)


# ============================================================
# TARGET
# ============================================================

TARGET = "match_result"

TARGET_CLASSES = [
    "HOME_WIN",
    "DRAW",
    "AWAY_WIN",
]


# ============================================================
# FULL FEATURE SET
# ============================================================

full_features = [
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
    "previous5_away_xg",

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

    "home_away_points_diff",
    "home_away_goals_for_diff",
    "home_away_goals_against_diff",
    "home_away_xg_diff",
]


# ============================================================
# COMPACT FEATURE SET
# ============================================================

# A deliberately simpler football-form representation.
# These are the most directly interpretable home-vs-away
# differences plus recent xG/form context.

compact_features = [
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
# INPUT QC
# ============================================================

print("\n--- INPUT QC ---")

required_columns = (
    full_features
    + compact_features
    + [TARGET, "match_id", "match_order", "match_date"]
)

missing_columns = sorted(
    set(required_columns)
    - set(model_df.columns)
)

print(
    "Missing required columns:",
    len(missing_columns)
)

if missing_columns:
    print(missing_columns)
    raise ValueError(
        "Required ML5 QC columns are missing."
    )

missing_values = (
    model_df[full_features]
    .isna()
    .sum()
    .sum()
)

non_finite_values = (
    ~np.isfinite(
        model_df[full_features].to_numpy()
    )
).sum()

duplicate_matches = (
    model_df["match_id"]
    .duplicated()
    .sum()
)

print(
    "Missing feature values:",
    missing_values
)

print(
    "Non-finite feature values:",
    non_finite_values
)

print(
    "Duplicate match IDs:",
    duplicate_matches
)


# ============================================================
# CHRONOLOGICAL SPLIT
# ============================================================

split_index = int(
    len(model_df) * 0.80
)

train_df = model_df.iloc[
    :split_index
].copy()

test_df = model_df.iloc[
    split_index:
].copy()

print(
    "\n--- CHRONOLOGICAL SPLIT ---"
)

print(
    "Training matches:",
    len(train_df)
)

print(
    "Testing matches:",
    len(test_df)
)

print(
    "Training period:",
    train_df["match_date"].min(),
    "to",
    train_df["match_date"].max()
)

print(
    "Testing period:",
    test_df["match_date"].min(),
    "to",
    test_df["match_date"].max()
)

temporal_valid = (
    train_df["match_order"].max()
    <
    test_df["match_order"].min()
)

print(
    "Training entirely before testing:",
    temporal_valid
)


# ============================================================
# CLASS DISTRIBUTION
# ============================================================

print(
    "\n--- CLASS DISTRIBUTION ---"
)

train_distribution = (
    train_df[TARGET]
    .value_counts()
    .reindex(TARGET_CLASSES, fill_value=0)
)

test_distribution = (
    test_df[TARGET]
    .value_counts()
    .reindex(TARGET_CLASSES, fill_value=0)
)

distribution_table = pd.DataFrame(
    {
        "Training": train_distribution,
        "Testing": test_distribution,
    }
)

print(
    distribution_table
)


# ============================================================
# FEATURE REDUNDANCY
# ============================================================

print(
    "\n============================================================"
)

print(
    "FEATURE REDUNDANCY CHECK"
)

print(
    "============================================================"
)

correlation_matrix = (
    train_df[full_features]
    .corr()
)

high_correlation_pairs = []

for i in range(len(full_features)):
    for j in range(i + 1, len(full_features)):

        correlation = (
            correlation_matrix.iloc[i, j]
        )

        if abs(correlation) >= 0.90:

            high_correlation_pairs.append(
                (
                    full_features[i],
                    full_features[j],
                    round(
                        float(correlation),
                        4
                    ),
                )
            )

print(
    "Feature pairs with |correlation| >= 0.90:",
    len(high_correlation_pairs)
)

for pair in high_correlation_pairs:
    print(pair)


# ============================================================
# RANDOM FOREST HELPER
# ============================================================

def train_and_evaluate(
    feature_set,
    model_name,
):
    X_train = train_df[
        feature_set
    ]

    X_test = test_df[
        feature_set
    ]

    y_train = train_df[
        TARGET
    ]

    y_test = test_df[
        TARGET
    ]

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

    train_predictions = (
        model.predict(X_train)
    )

    test_predictions = (
        model.predict(X_test)
    )

    test_probabilities = (
        model.predict_proba(X_test)
    )

    test_accuracy = accuracy_score(
        y_test,
        test_predictions,
    )

    test_macro_f1 = f1_score(
        y_test,
        test_predictions,
        labels=TARGET_CLASSES,
        average="macro",
        zero_division=0,
    )

    test_logloss = log_loss(
        y_test,
        test_probabilities,
        labels=model.classes_,
    )

    # Multiclass Brier score:
    # mean squared error across the three class probabilities.
    y_test_one_hot = np.zeros(
        (
            len(y_test),
            len(TARGET_CLASSES),
        )
    )

    class_to_index = {
        class_name: index
        for index, class_name
        in enumerate(TARGET_CLASSES)
    }

    for row_index, class_name in enumerate(y_test):
        y_test_one_hot[
            row_index,
            class_to_index[class_name]
        ] = 1.0

    probability_order = [
        class_to_index[class_name]
        for class_name in model.classes_
    ]

    ordered_probabilities = (
        np.zeros_like(y_test_one_hot)
    )

    for source_index, target_index in enumerate(
        probability_order
    ):
        ordered_probabilities[
            :,
            target_index
        ] = test_probabilities[
            :,
            source_index
        ]

    multiclass_brier = np.mean(
        np.sum(
            (
                ordered_probabilities
                - y_test_one_hot
            ) ** 2,
            axis=1,
        )
    )

    print(
        f"\n--- {model_name} ---"
    )

    print(
        "Feature count:",
        len(feature_set)
    )

    print(
        f"Training accuracy: {accuracy_score(y_train, train_predictions):.4f}"
    )

    print(
        f"Testing accuracy: {test_accuracy:.4f}"
    )

    print(
        f"Testing Macro F1: {test_macro_f1:.4f}"
    )

    print(
        f"Testing Log Loss: {test_logloss:.4f}"
    )

    print(
        f"Testing multiclass Brier score: {multiclass_brier:.4f}"
    )

    return {
        "Model": model_name,
        "Features": len(feature_set),
        "Test Accuracy": test_accuracy,
        "Test Macro F1": test_macro_f1,
        "Test Log Loss": test_logloss,
        "Test Brier Score": multiclass_brier,
        "model": model,
    }


# ============================================================
# FULL VS COMPACT MODEL
# ============================================================

print(
    "\n============================================================"
)

print(
    "FULL VS COMPACT FEATURE MODEL"
)

print(
    "============================================================"
)

full_result = train_and_evaluate(
    full_features,
    "Full Random Forest",
)

compact_result = train_and_evaluate(
    compact_features,
    "Compact Random Forest",
)


# ============================================================
# COMPARISON
# ============================================================

comparison = pd.DataFrame(
    [
        {
            "Model":
                full_result["Model"],
            "Features":
                full_result["Features"],
            "Accuracy":
                full_result["Test Accuracy"],
            "Macro F1":
                full_result["Test Macro F1"],
            "Log Loss":
                full_result["Test Log Loss"],
            "Brier Score":
                full_result["Test Brier Score"],
        },
        {
            "Model":
                compact_result["Model"],
            "Features":
                compact_result["Features"],
            "Accuracy":
                compact_result["Test Accuracy"],
            "Macro F1":
                compact_result["Test Macro F1"],
            "Log Loss":
                compact_result["Test Log Loss"],
            "Brier Score":
                compact_result["Test Brier Score"],
        },
    ]
)

print(
    "\n============================================================"
)

print(
    "MODEL QUALITY COMPARISON"
)

print(
    "============================================================"
)

print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# FULL MODEL FEATURE IMPORTANCE
# ============================================================

print(
    "\n============================================================"
)

print(
    "FULL MODEL TOP FEATURE IMPORTANCE"
)

print(
    "============================================================"
)

full_importance = (
    pd.DataFrame(
        {
            "feature": full_features,
            "importance":
                full_result[
                    "model"
                ].feature_importances_,
        }
    )
    .sort_values(
        "importance",
        ascending=False
    )
    .reset_index(drop=True)
)

print(
    full_importance.head(15)
    .to_string(index=False)
)


# ============================================================
# TEST PERIOD DIFFICULTY
# ============================================================

print(
    "\n============================================================"
)

print(
    "TEST PERIOD DIFFICULTY CHECK"
)

print(
    "============================================================"
)

test_home_win_rate = (
    (
        test_df[TARGET]
        == "HOME_WIN"
    ).mean()
)

test_draw_rate = (
    (
        test_df[TARGET]
        == "DRAW"
    ).mean()
)

test_away_win_rate = (
    (
        test_df[TARGET]
        == "AWAY_WIN"
    ).mean()
)

print(
    f"Test HOME_WIN rate: {test_home_win_rate:.4f}"
)

print(
    f"Test DRAW rate: {test_draw_rate:.4f}"
)

print(
    f"Test AWAY_WIN rate: {test_away_win_rate:.4f}"
)

print(
    "\nThe test period contains all three outcome classes."
)


# ============================================================
# FINAL QC DECISION SUPPORT
# ============================================================

print(
    "\n============================================================"
)

print(
    "ML5 QUALITY QC"
)

print(
    "============================================================"
)

print(
    "This QC does not automatically declare a better model."
)

print(
    "Use test Macro F1 and Log Loss together with accuracy."
)

print(
    "If the compact model performs similarly, prefer the simpler"
)

print(
    "feature representation for interpretability."
)

print(
    "\nTechnical QC:"
)

print(
    "Rows valid:",
    len(model_df) == 280
)

print(
    "Missing values valid:",
    missing_values == 0
)

print(
    "Non-finite values valid:",
    non_finite_values == 0
)

print(
    "Duplicate matches valid:",
    duplicate_matches == 0
)

print(
    "Chronological split valid:",
    temporal_valid
)

print(
    "All test classes present:",
    set(test_df[TARGET])
    == set(TARGET_CLASSES)
)

print(
    "\n========================================"
)

if (
    len(model_df) == 280
    and missing_values == 0
    and non_finite_values == 0
    and duplicate_matches == 0
    and temporal_valid
    and set(test_df[TARGET])
       == set(TARGET_CLASSES)
):

    print(
        "ML5 QUALITY QC: TECHNICALLY PASSED"
    )

else:

    print(
        "ML5 QUALITY QC: FAILED"
    )

print(
    "========================================"
)