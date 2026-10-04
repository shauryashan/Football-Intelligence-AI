# Football Intelligence AI — Machine Learning Methodology

## 1. Purpose

The machine-learning layer of Football Intelligence AI extends the football analytics system with:

- player similarity
- player clustering
- player performance prediction
- match outcome prediction

The models are built on top of the validated football database and derived analytical features.

The project distinguishes between:

- descriptive analytics
- unsupervised machine learning
- supervised machine learning
- model validation
- football-domain interpretation

Machine-learning outputs are treated as analytical predictions rather than guaranteed football outcomes.

---

# 2. ML Dataset Foundation

The main player machine-learning population contains:

- 316 players
- minimum 900 recorded minutes
- 15 validated football performance features

The 15-feature player representation contains:

1. shots per 90
2. xG per 90
3. key passes per 90
4. passes per 90
5. pass distance per 90
6. pressures per 90
7. tackles per 90
8. interceptions per 90
9. clearances per 90
10. carries per 90
11. dribbles per 90
12. duels per 90
13. miscontrols per 90
14. dispossessed per 90
15. ball recoveries per 90

The feature matrix was validated before being used by the machine-learning models.

Validation confirmed:

- 316 players
- 15 features
- zero missing feature values
- zero non-finite values
- zero duplicate player IDs

---

# 3. Feature Selection

An initial 20-feature representation was examined.

Five features were removed from the final similarity representation:

- goals per 90
- assists per 90
- completed passes per 90
- successful dribbles per 90
- aerial duels lost per 90

The reasons were primarily redundancy and feature interpretation.

Goals per 90 was removed because it overlaps strongly with shooting and xG-related information and can be noisy.

Assists per 90 was removed because it overlaps with key-pass information and can be low-volume.

Completed passes per 90 was removed because it is highly redundant with total passes per 90.

Successful dribbles per 90 was removed because it is highly redundant with dribble volume.

Aerial duels lost was removed because it is a one-sided loss measure rather than a complete representation of aerial ability.

This feature reduction is a modeling judgment.

It has not been established as an empirically optimal feature-selection procedure.

---

# 4. Feature Correlation

The original feature matrix was examined for redundancy.

Important high correlations included:

- shots and xG: approximately 0.900
- shots and goals: approximately 0.859
- xG and goals: approximately 0.917
- key passes and assists: approximately 0.825
- passes and completed passes: approximately 0.973
- dribbles and successful dribbles: approximately 0.978
- dribbles and dispossessed: approximately 0.878
- miscontrols and dispossessed: approximately 0.890
- duels and aerial duels lost: approximately 0.858

This analysis informed the reduction from 20 to 15 features.

---

# 5. ML 1 — Feature Engineering and Quality Control

ML 1 established the validated machine-learning feature matrix.

The process included:

1. querying structured football data from SQLite
2. calculating player-level performance features
3. normalizing event statistics per 90 minutes
4. restricting the population to players with at least 900 minutes
5. inspecting feature correlations
6. removing selected redundant features
7. validating the final matrix

The final matrix contains:

`316 players × 15 features`

Quality checks passed for:

- missing values
- non-finite values
- duplicate player IDs
- zero-variance features

---

# 6. ML 2 — Player Similarity

## Objective

Identify statistically similar players using their football performance profiles.

## Method

The 15 player features are standardized using:

`StandardScaler`

Similarity is then calculated using:

`Cosine Similarity`

This produces a:

`316 × 316`

player similarity matrix.

Each matrix value represents the similarity between two standardized player profiles.

---

## Role-Aware Similarity

The similarity model was subsequently made role-aware.

Each player's primary position is determined from accumulated playing minutes.

The primary position is mapped into one of eight analytical role groups:

1. Goalkeeper
2. Centre Back
3. Full Back
4. Defensive Midfielder
5. Central Midfielder
6. Attacking Midfielder
7. Winger
8. Forward

Players are compared only against candidates from the same analytical role.

The role is therefore used as a candidate filter rather than as a numerical ML feature.

This prevents obviously inappropriate cross-role comparisons.

---

## Similarity Interpretation

A high similarity score means that two players have similar values across the selected statistical feature representation.

It does not mean that the players:

- have identical tactical roles
- have identical playing styles
- have equal quality
- have equal potential
- are guaranteed tactical replacements

---

## ML 2 Validation

Similarity validation checked:

- expected player population
- feature completeness
- role availability
- player uniqueness
- absence of self-matches
- role consistency of returned candidates
- availability of at least five similar candidates

Five representative roles were successfully validated:

- Centre Back
- Full Back
- Attacking Midfielder
- Winger
- Forward

The current validation script uses five representative player tests.

Three earlier exact-name tests were not retained because the database names did not exactly match the test strings.

The similarity algorithm itself supports arbitrary players available in the validated population.

---

# 7. ML 3 — Player Clustering

## Objective

Identify natural statistical player archetypes without directly supplying football role labels to the clustering algorithm.

## Method

The same 15-feature player representation is:

1. standardized
2. passed to K-Means clustering

Different values of K were evaluated.

The tested range was:

`K = 2 through 10`

Silhouette scores were:

- K=2: 0.307972
- K=3: 0.259656
- K=4: 0.299865
- K=5: 0.306181
- K=6: 0.282497
- K=7: 0.272230
- K=8: 0.255504
- K=9: 0.245525
- K=10: 0.240544

---

## Cluster Selection

K=2 produced the highest numerical silhouette score.

However, K=5 produced an almost identical score while producing substantially more interpretable football archetypes.

The project therefore selected:

`K = 5`

This decision combines quantitative separation with football-domain interpretability.

---

## Final Archetypes

The five clusters were interpreted as:

1. Goalkeeper
2. Two-Way / High-Volume
3. Finishing Forward
4. Creative Attacker
5. Defensive Player

These names are human interpretations of the resulting statistical clusters.

They are not labels learned by K-Means.

---

## Cluster Quality

The mean silhouette scores for the final clusters were:

- Goalkeeper cluster: approximately 0.806
- Two-Way / High-Volume: approximately 0.178
- Finishing Forward: approximately 0.337
- Creative Attacker: approximately 0.196
- Defensive Player: approximately 0.372

The lower scores for some clusters indicate that certain player profiles overlap.

Therefore, the archetypes should be treated as statistical groupings rather than rigid football categories.

---

## ML 3 Validation

Validation confirmed:

- 316 expected players
- 316 actual players
- five clusters
- no missing cluster labels
- no missing archetype labels
- zero duplicate player IDs
- 316 cluster assignments
- five cluster profiles

ML3 technical validation passed.

---

# 8. ML 4 — Player Performance Prediction

## Objective

Predict a player's total xG across their next five appearances using information from their previous five appearances.

The target is:

`target_future_xg`

where the target represents the sum of xG across the player's next five appearances.

The model does not predict future xG per 90.

This target was selected because future total xG provides a more stable prediction target than short-window goals-per-90 rates.

---

# 9. ML 4 Feature Construction

For each prediction snapshot:

- the previous five appearances provide historical information
- the next five appearances provide the prediction target

The historical features include:

- shots per 90
- xG per 90
- passes per 90
- pressures per 90
- duels per 90
- carries per 90
- dribbles per 90
- interceptions per 90
- clearances per 90
- miscontrols per 90
- dispossessed per 90
- ball recoveries per 90

The model therefore uses recent player performance to forecast near-future attacking output.

---

# 10. ML 4 Temporal Validation

Temporal leakage was treated as a major validation concern.

The final ML4 pipeline enforces:

- exactly five historical appearances
- exactly five future target appearances
- all historical appearances before the future target window
- training target windows entirely before testing target windows
- zero target-window overlap

The final dataset contained:

- 6,276 prediction snapshots
- 3,901 training snapshots
- 1,126 testing snapshots

The training target period was:

`2015-09-19 to 2016-02-07`

The testing target period was:

`2016-03-05 to 2016-04-24`

The latest match used by any training target was match order 281.

The first match used by any testing target was match order 282.

Target-window overlap:

`0`

This confirms that the final train/test target periods were chronologically separated.

---

# 11. ML 4 Models

Three approaches were compared:

### Mean Baseline

Predicts the mean future xG observed in the training set.

### Linear Regression

A linear regression model was used as a simple supervised baseline.

### Random Forest Regressor

The final Random Forest configuration used:

- 300 trees
- maximum depth: 8
- minimum samples per leaf: 10
- random state: 42
- parallel processing

---

# 12. ML 4 Results

## Linear Regression

- MAE: 0.5093
- RMSE: 0.7945
- R²: -0.3682

## Random Forest

- MAE: 0.3271
- RMSE: 0.5352
- R²: 0.3792

## Mean Baseline

- MAE: 0.4748
- RMSE: 0.6793
- R²: approximately 0

The Random Forest improved over the mean baseline by:

- 31.10% MAE
- 21.21% RMSE

The Random Forest therefore provided a meaningful improvement over the baseline under the final strict chronological validation.

The test R² of 0.3792 should not be interpreted as 38% prediction accuracy.

It is the coefficient of determination on this specific held-out test period.

---

# 13. ML 4 Feature Importance

The Random Forest feature importances were:

- xG per 90: 0.491074
- passes per 90: 0.124564
- shots per 90: 0.071259
- pressures per 90: 0.054951
- miscontrols per 90: 0.049254
- clearances per 90: 0.045045
- dribbles per 90: 0.040247
- duels per 90: 0.032758
- carries per 90: 0.030993
- ball recoveries per 90: 0.023064
- dispossessed per 90: 0.020248
- interceptions per 90: 0.016543

Feature importance indicates how useful features were to the fitted Random Forest under its training process.

It does not establish causal relationships.

---

# 14. Rejected ML 4 Formulations

Several earlier formulations were evaluated and rejected.

## Next-appearance goals per 90

This produced unstable values because short appearances can create extremely large per-90 rates.

Results included:

- MAE: 3.2115
- RMSE: 5.8629
- R²: -1.9459

The baseline performed better.

This formulation was rejected.

---

## Next-appearance total goals

A Linear Regression approach produced:

- MAE: 0.1932
- RMSE: 0.3764
- R²: -0.0126

The baseline was slightly better.

Negative predictions were also possible.

This formulation was rejected.

---

## Poisson Regression for next-appearance goals

Results included:

- MAE: 0.1921
- RMSE: 0.3744
- R²: -0.0018

The model was technically valid but provided little useful improvement over the baseline.

This formulation was rejected.

---

## Future five-appearance mean xG per 90

This target produced extremely large values because of small future-minute denominators.

The target reached values above 500 in the training period and above 800 in the testing period.

Linear Regression also produced negative predictions.

The target definition was rejected.

---

# 15. ML 5 — Match Outcome Prediction

## Objective

Predict:

- HOME_WIN
- DRAW
- AWAY_WIN

using only information available before the match.

The system deliberately excludes the current match's result and current-match event information from the predictive features.

---

# 16. ML 5 Feature Construction

The feature-generation pipeline aggregates event data to the team-match level.

The following event categories are used:

- shots
- xG
- passes
- pressures
- carries
- duels
- interceptions
- clearances

Team performance is then converted into previous-match form information.

The system calculates:

- general previous-five-match form
- home-specific previous-five-match form
- away-specific previous-five-match form
- home-vs-away difference features

The current match outcome is excluded from the historical feature calculations.

---

# 17. ML 5 Efficiency Improvement

The original implementation loaded all 1,313,773 event rows into Pandas.

This was replaced by SQL aggregation inside SQLite.

The database aggregates event records into team-match statistics before the data reaches Pandas.

This reduces the event-level working dataset to:

`760 team-match rows`

The change improves memory efficiency while preserving the analytical logic.

It also demonstrates the intended architecture of using SQL for structured aggregation rather than unnecessarily loading the full event table into memory.

---

# 18. ML 5 Feature Validation

The final pre-match feature dataset contains:

- 380 total matches
- 280 matches with sufficient previous-five history
- 100 matches excluded because one or both teams lacked five previous matches

The target distribution is:

- HOME_WIN: 122
- DRAW: 79
- AWAY_WIN: 79

Validation confirmed:

- current match result excluded from features
- zero missing feature values
- zero duplicate match IDs
- chronological match ordering

ML5 feature validation passed.

---

# 19. ML 5 Models

Three approaches were compared:

1. Majority-class baseline
2. Logistic Regression
3. Random Forest Classifier

The Random Forest configuration used:

- 300 trees
- maximum depth: 8
- minimum samples per leaf: 5
- random state: 42
- parallel processing

---

# 20. ML 5 Chronological Validation

The usable 280 matches were split chronologically:

- training: 224 matches
- testing: 56 matches

Training period:

`2015-10-31 to 2016-04-13`

Testing period:

`2016-04-16 to 2016-05-17`

The last training match occurred before the first testing match.

Therefore, the model was evaluated on a later time period rather than a random sample of matches.

---

# 21. Initial ML 5 Results

### Majority Baseline

- Accuracy: 0.4821
- Macro F1: 0.2169
- Log Loss: 18.6655

### Logistic Regression

- Accuracy: 0.3750
- Macro F1: 0.3607
- Log Loss: 1.2175

### Initial Random Forest

- Accuracy: 0.4821
- Macro F1: 0.3854
- Log Loss: 1.0318

The Random Forest was therefore better than the majority baseline on Macro F1 and Log Loss, although its accuracy matched the baseline.

---

# 22. ML 5 Feature Redundancy Analysis

The full ML5 representation contained 45 features.

Several highly redundant relationships were identified.

Examples:

- previous-five home passes and home carries: correlation approximately 0.970
- previous-five away passes and away carries: correlation approximately 0.967
- passes difference and carries difference: correlation approximately 0.974

This motivated testing a compact feature representation.

---

# 23. ML 5 Compact Model

A compact representation containing 12 features was evaluated.

The 12 features are:

1. form points difference
2. goals for difference
3. goals against difference
4. shots difference
5. xG difference
6. passes difference
7. pressures difference
8. carries difference
9. duels difference
10. interceptions difference
11. clearances difference
12. home-away xG difference

The compact representation removes substantial redundancy while retaining the main pre-match performance differences between the two teams.

---

# 24. ML 5 Final Model Results

## Full Random Forest

- Features: 45
- Training accuracy: 0.9241
- Test accuracy: 0.4821
- Macro F1: 0.3854
- Log Loss: 1.0318
- Multiclass Brier score: 0.6155

The large gap between training and testing accuracy indicates substantial overfitting in the full feature representation.

---

## Compact Random Forest

- Features: 12
- Training accuracy: 0.8393
- Test accuracy: 0.5179
- Macro F1: 0.4535
- Log Loss: 1.0641
- Multiclass Brier score: 0.6363

The compact model achieved:

`51.79%`

held-out accuracy and:

`0.4535`

Macro F1.

It also reduced training accuracy, which is consistent with a less complex representation.

The compact model was selected as the final ML5 representation because it improved held-out accuracy and Macro F1 while reducing feature redundancy.

The full model had slightly better Log Loss, so the compact model is not superior on every evaluation metric.

---

# 25. ML 5 Confusion Matrix

The compact/final Random Forest evaluation used three outcome classes.

The confusion matrix from the model evaluation was:

| Actual | Predicted Home Win | Predicted Draw | Predicted Away Win |
|---|---:|---:|---:|
| Home Win | 21 | 3 | 3 |
| Draw | 7 | 2 | 9 |
| Away Win | 5 | 2 | 4 |

Class-level recall showed:

- Home-win recall: approximately 78%
- Draw recall: approximately 11%
- Away-win recall: approximately 36%

The model therefore performs substantially better at identifying home wins than draws.

---

# 26. ML 5 Probability Validation

The final model also produces multiclass probabilities.

Validation confirmed:

- valid prediction counts
- valid probability counts
- finite probabilities
- probability values sum to 1
- all three test classes are represented

This is important because the application can eventually present outcome probabilities rather than only a single predicted class.

---

# 27. ML 5 Limitations

The match-outcome model has several limitations.

### Dataset size

Only 280 matches are available after requiring sufficient previous-five-match history.

The final test set contains only 56 matches.

### Single-season limitation

The model is trained and tested within the Premier League 2015/16 season.

### Temporal limitation

The evaluation uses one chronological holdout period.

Performance may differ on other seasons or competitions.

### Draw prediction

The model has relatively weak draw recall.

### Feature limitation

The current feature set focuses on historical team performance and event-derived statistics.

It does not currently include factors such as:

- injuries
- suspensions
- confirmed lineups
- transfers
- bookmaker odds
- weather
- travel
- current squad strength
- live tactical information

### No current football data

The model is not a live match prediction system.

---

# 28. Machine Learning Validation Principles

The project follows several validation principles:

1. Validate the underlying feature dataset before modeling.
2. Avoid duplicate player or match records.
3. Check missing and non-finite values.
4. Use chronological splits for temporal football prediction tasks.
5. Prevent target-window overlap.
6. Compare against simple baselines.
7. Report multiple evaluation metrics.
8. Inspect feature redundancy.
9. Avoid interpreting test R² as accuracy.
10. Avoid interpreting feature importance as causality.
11. Document rejected modeling approaches.
12. Do not claim model performance outside the evaluated dataset.

---

# 29. Current ML Status

Completed machine-learning components:

- ML1: Feature engineering and QC
- ML2: Role-aware player similarity
- ML3: Player clustering
- ML4: Player performance prediction
- ML5: Match outcome prediction

The machine-learning layer is currently based on the selected Premier League 2015/16 dataset.

Future expansion to additional competitions and seasons should first validate the data coverage, feature consistency, and model behavior on those datasets.

---

# 30. Overall ML Principle

Football Intelligence AI uses machine learning as a decision-support layer.

The system should distinguish between:

- observed football data
- derived analytical metrics
- engineered features
- model predictions
- model interpretations

A machine-learning prediction is not a guaranteed football outcome.

The final AI architecture should use SQL for exact structured statistics, machine learning for predictive and similarity tasks, RAG for grounded project documentation, and an agent layer for coordinating multi-step workflows.