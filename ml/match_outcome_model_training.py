import numpy as np
import pandas as pd

from pathlib import Path

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    log_loss,
    confusion_matrix,
    classification_report,
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

print("Loading pre-match feature dataset...")

model_df = pd.read_csv(INPUT_FILE)

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
# FEATURE COLUMNS
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
# BASIC VALIDATION
# ============================================================

print("\n--- INPUT VALIDATION ---")

missing_columns = [
    column
    for column in feature_columns + [TARGET]
    if column not in model_df.columns
]

print(
    "Missing required columns:",
    len(missing_columns)
)

if missing_columns:
    print(missing_columns)
    raise ValueError(
        "Required feature columns are missing."
    )


missing_features = (
    model_df[feature_columns]
    .isna()
    .sum()
    .sum()
)

missing_target = (
    model_df[TARGET]
    .isna()
    .sum()
)

non_finite_features = (
    ~np.isfinite(
        model_df[feature_columns].to_numpy()
    )
).sum()

duplicate_matches = (
    model_df["match_id"]
    .duplicated()
    .sum()
)

print(
    "Missing feature values:",
    missing_features
)

print(
    "Missing target values:",
    missing_target
)

print(
    "Non-finite feature values:",
    non_finite_features
)

print(
    "Duplicate match IDs:",
    duplicate_matches
)


# ============================================================
# SORT CHRONOLOGICALLY
# ============================================================

model_df = (
    model_df
    .sort_values("match_order")
    .reset_index(drop=True)
)


chronological_order_valid = (
    model_df["match_order"]
    .is_monotonic_increasing
)

print(
    "Chronological order valid:",
    chronological_order_valid
)


# ============================================================
# TARGET CHECK
# ============================================================

unexpected_targets = sorted(
    set(model_df[TARGET])
    - set(TARGET_CLASSES)
)

print(
    "Unexpected target classes:",
    unexpected_targets
)

if unexpected_targets:
    raise ValueError(
        "Unexpected target class found."
    )


# ============================================================
# CHRONOLOGICAL TRAIN / TEST SPLIT
# ============================================================

print(
    "\nCreating chronological train/test split..."
)

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
    f"Training matches: {len(train_df)}"
)

print(
    f"Testing matches: {len(test_df)}"
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


# ============================================================
# EXTRACT FEATURES / TARGET
# ============================================================

X_train = train_df[
    feature_columns
].copy()

X_test = test_df[
    feature_columns
].copy()

y_train = train_df[
    TARGET
].copy()

y_test = test_df[
    TARGET
].copy()


# ============================================================
# CLASS DISTRIBUTION
# ============================================================

print("\n--- TRAINING TARGET DISTRIBUTION ---")

print(
    y_train.value_counts()
    .reindex(TARGET_CLASSES, fill_value=0)
)


print("\n--- TEST TARGET DISTRIBUTION ---")

print(
    y_test.value_counts()
    .reindex(TARGET_CLASSES, fill_value=0)
)


# ============================================================
# STRICT TEMPORAL VALIDATION
# ============================================================

print(
    "\n--- TEMPORAL VALIDATION ---"
)

last_training_order = (
    train_df["match_order"].max()
)

first_testing_order = (
    test_df["match_order"].min()
)

print(
    "Last training match order:",
    last_training_order
)

print(
    "First testing match order:",
    first_testing_order
)

temporal_split_valid = (
    last_training_order
    < first_testing_order
)

print(
    "Training occurs entirely before testing:",
    temporal_split_valid
)


# ============================================================
# MODEL 1 — MAJORITY-CLASS BASELINE
# ============================================================

print(
    "\n============================================================"
)

print(
    "MAJORITY-CLASS BASELINE"
)

print(
    "============================================================"
)

baseline = DummyClassifier(
    strategy="most_frequent"
)

baseline.fit(
    X_train,
    y_train
)

baseline_predictions = (
    baseline.predict(X_test)
)

baseline_probabilities = (
    baseline.predict_proba(X_test)
)

baseline_accuracy = accuracy_score(
    y_test,
    baseline_predictions
)

baseline_macro_f1 = f1_score(
    y_test,
    baseline_predictions,
    labels=TARGET_CLASSES,
    average="macro",
    zero_division=0,
)

baseline_logloss = log_loss(
    y_test,
    baseline_probabilities,
    labels=baseline.classes_,
)

print(
    f"Accuracy: {baseline_accuracy:.4f}"
)

print(
    f"Macro F1: {baseline_macro_f1:.4f}"
)

print(
    f"Log Loss: {baseline_logloss:.4f}"
)

print(
    "Majority class:",
    baseline.classes_[
        np.argmax(
            baseline.class_prior_
        )
    ]
)


# ============================================================
# MODEL 2 — LOGISTIC REGRESSION
# ============================================================

print(
    "\n============================================================"
)

print(
    "LOGISTIC REGRESSION"
)

print(
    "============================================================"
)

logistic_model = Pipeline(
    steps=[
        (
            "scaler",
            StandardScaler()
        ),
        (
            "model",
            LogisticRegression(
                max_iter=2000,
                random_state=42
            )
        ),
    ]
)

logistic_model.fit(
    X_train,
    y_train
)

logistic_predictions = (
    logistic_model.predict(X_test)
)

logistic_probabilities = (
    logistic_model.predict_proba(X_test)
)

logistic_accuracy = accuracy_score(
    y_test,
    logistic_predictions
)

logistic_macro_f1 = f1_score(
    y_test,
    logistic_predictions,
    labels=TARGET_CLASSES,
    average="macro",
    zero_division=0,
)

logistic_logloss = log_loss(
    y_test,
    logistic_probabilities,
    labels=logistic_model.classes_,
)

print(
    f"Accuracy: {logistic_accuracy:.4f}"
)

print(
    f"Macro F1: {logistic_macro_f1:.4f}"
)

print(
    f"Log Loss: {logistic_logloss:.4f}"
)


# ============================================================
# MODEL 3 — RANDOM FOREST
# ============================================================

print(
    "\n============================================================"
)

print(
    "RANDOM FOREST"
)

print(
    "============================================================"
)

random_forest = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1,
)

random_forest.fit(
    X_train,
    y_train
)

rf_predictions = (
    random_forest.predict(X_test)
)

rf_probabilities = (
    random_forest.predict_proba(X_test)
)

rf_accuracy = accuracy_score(
    y_test,
    rf_predictions
)

rf_macro_f1 = f1_score(
    y_test,
    rf_predictions,
    labels=TARGET_CLASSES,
    average="macro",
    zero_division=0,
)

rf_logloss = log_loss(
    y_test,
    rf_probabilities,
    labels=random_forest.classes_,
)

print(
    f"Accuracy: {rf_accuracy:.4f}"
)

print(
    f"Macro F1: {rf_macro_f1:.4f}"
)

print(
    f"Log Loss: {rf_logloss:.4f}"
)


# ============================================================
# MODEL COMPARISON
# ============================================================

print(
    "\n============================================================"
)

print(
    "MODEL COMPARISON"
)

print(
    "============================================================"
)

comparison = pd.DataFrame(
    {
        "Model": [
            "Majority Baseline",
            "Logistic Regression",
            "Random Forest",
        ],
        "Accuracy": [
            baseline_accuracy,
            logistic_accuracy,
            rf_accuracy,
        ],
        "Macro F1": [
            baseline_macro_f1,
            logistic_macro_f1,
            rf_macro_f1,
        ],
        "Log Loss": [
            baseline_logloss,
            logistic_logloss,
            rf_logloss,
        ],
    }
)

print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# CONFUSION MATRICES
# ============================================================

print(
    "\n============================================================"
)

print(
    "CONFUSION MATRICES"
)

print(
    "============================================================"
)

logistic_cm = confusion_matrix(
    y_test,
    logistic_predictions,
    labels=TARGET_CLASSES
)

rf_cm = confusion_matrix(
    y_test,
    rf_predictions,
    labels=TARGET_CLASSES
)

print(
    "\nLogistic Regression:"
)

print(
    pd.DataFrame(
        logistic_cm,
        index=[
            f"Actual_{x}"
            for x in TARGET_CLASSES
        ],
        columns=[
            f"Predicted_{x}"
            for x in TARGET_CLASSES
        ],
    )
)


print(
    "\nRandom Forest:"
)

print(
    pd.DataFrame(
        rf_cm,
        index=[
            f"Actual_{x}"
            for x in TARGET_CLASSES
        ],
        columns=[
            f"Predicted_{x}"
            for x in TARGET_CLASSES
        ],
    )
)


# ============================================================
# CLASSIFICATION REPORTS
# ============================================================

print(
    "\n============================================================"
)

print(
    "CLASSIFICATION REPORTS"
)

print(
    "============================================================"
)

print(
    "\nLogistic Regression:"
)

print(
    classification_report(
        y_test,
        logistic_predictions,
        labels=TARGET_CLASSES,
        zero_division=0,
    )
)


print(
    "Random Forest:"
)

print(
    classification_report(
        y_test,
        rf_predictions,
        labels=TARGET_CLASSES,
        zero_division=0,
    )
)


# ============================================================
# RANDOM FOREST FEATURE IMPORTANCE
# ============================================================

print(
    "\n============================================================"
)

print(
    "RANDOM FOREST FEATURE IMPORTANCE"
)

print(
    "============================================================"
)

feature_importance = (
    pd.DataFrame(
        {
            "feature": feature_columns,
            "importance":
                random_forest.feature_importances_,
        }
    )
    .sort_values(
        "importance",
        ascending=False
    )
    .reset_index(drop=True)
)

print(
    feature_importance.to_string(
        index=False
    )
)


# ============================================================
# SAMPLE PREDICTIONS WITH PROBABILITIES
# ============================================================

print(
    "\n============================================================"
)

print(
    "SAMPLE RANDOM FOREST PREDICTIONS"
)

print(
    "============================================================"
)

sample_predictions = test_df[
    [
        "match_id",
        "match_date",
        "home_team_id",
        "away_team_id",
        "match_result",
    ]
].copy()

sample_predictions[
    "predicted_result"
] = rf_predictions

rf_probability_df = pd.DataFrame(
    rf_probabilities,
    columns=random_forest.classes_,
)

sample_predictions[
    "prob_home_win"
] = rf_probability_df[
    "HOME_WIN"
].to_numpy()

sample_predictions[
    "prob_draw"
] = rf_probability_df[
    "DRAW"
].to_numpy()

sample_predictions[
    "prob_away_win"
] = rf_probability_df[
    "AWAY_WIN"
].to_numpy()

print(
    sample_predictions
    .head(10)
    .to_string(index=False)
)


# ============================================================
# FINAL TECHNICAL VALIDATION
# ============================================================

print(
    "\n============================================================"
)

print(
    "ML5 MODEL VALIDATION"
)

print(
    "============================================================"
)

prediction_length_valid = (
    len(rf_predictions)
    == len(y_test)
)

probability_length_valid = (
    len(rf_probabilities)
    == len(y_test)
)

probabilities_finite = (
    np.isfinite(
        rf_probabilities
    ).all()
)

probabilities_valid = (
    np.allclose(
        rf_probabilities.sum(axis=1),
        1.0
    )
)

all_test_classes_seen = (
    set(y_test)
    == set(TARGET_CLASSES)
)

technical_validation_passed = (
    len(model_df) == 280
    and len(train_df) == 224
    and len(test_df) == 56
    and missing_features == 0
    and missing_target == 0
    and non_finite_features == 0
    and duplicate_matches == 0
    and chronological_order_valid
    and temporal_split_valid
    and not unexpected_targets
    and prediction_length_valid
    and probability_length_valid
    and probabilities_finite
    and probabilities_valid
    and all_test_classes_seen
)

print(
    "Total matches:",
    len(model_df)
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
    "Missing training/test features:",
    missing_features
)

print(
    "Missing target values:",
    missing_target
)

print(
    "Duplicate match IDs:",
    duplicate_matches
)

print(
    "Chronological order valid:",
    chronological_order_valid
)

print(
    "Training entirely before testing:",
    temporal_split_valid
)

print(
    "Prediction count valid:",
    prediction_length_valid
)

print(
    "Probability count valid:",
    probability_length_valid
)

print(
    "All probabilities finite:",
    probabilities_finite
)

print(
    "Probabilities sum to 1:",
    probabilities_valid
)

print(
    "All three test classes present:",
    all_test_classes_seen
)

print(
    "\n========================================"
)

if technical_validation_passed:

    print(
        "ML5 MODEL TECHNICAL VALIDATION: PASSED"
    )

else:

    print(
        "ML5 MODEL TECHNICAL VALIDATION: FAILED"
    )

print(
    "========================================"
)