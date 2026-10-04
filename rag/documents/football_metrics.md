# Football Intelligence AI — Football Metrics

## 1. Purpose

This document defines the football metrics used by Football Intelligence AI.

The metrics are derived primarily from StatsBomb event data and player-match data.

Metrics should be interpreted in the context of the project's dataset, methodology, exposure thresholds, and known limitations.

---

## 2. Match-Level Metrics

### Goals

Goals represent the number of goals scored by a team or player.

Match-level goals are obtained from the match data and are also cross-checked against event-level goal information.

In the current dataset:

- 988 goals are recorded through shot events
- 38 own goals are recorded
- 1,026 total match-level goals are represented

The event-level reconciliation is:

`988 shot goals + 38 own goals = 1,026 match-level goals`

---

## 3. Expected Goals (xG)

Expected goals (xG) estimates the probability that a shot results in a goal.

The project uses the `shot_xg` value supplied by the StatsBomb event data.

Player and team xG can therefore be aggregated from shot events.

Examples:

- total xG
- xG per 90
- xG compared with actual goals
- xG-based attacking profiles

xG should not be interpreted as a prediction that a specific shot will definitely become a goal.

---

## 4. Shooting Metrics

### Shots

A shot is an event recorded with event type `Shot`.

Common derived metrics include:

- total shots
- shots per 90
- shots compared with xG
- shots compared with goals

### Goals per 90

Goals per 90 represents goals relative to the player's recorded playing-time exposure.

It can be useful descriptively but can become unstable for players with very small playing-time samples.

For this reason, the project's scouting population uses a minimum exposure threshold.

### xG per 90

xG per 90 represents accumulated xG relative to recorded playing time.

It is used to compare attacking production across players with different amounts of playing time.

---

## 5. Passing Metrics

### Passes

A pass is an event with event type `Pass`.

The project can calculate:

- total passes
- passes per 90
- pass distance per 90
- passing volume by team
- passing volume by player

### Completed Passes

Pass outcomes can be used to identify incomplete passes.

However, successful StatsBomb passes can omit a `pass.outcome` value.

Therefore, the absence of a pass outcome is not automatically treated as an unsuccessful pass.

### Pass Distance

StatsBomb provides pass length.

The project aggregates pass length to measure passing distance and can normalize it per 90 minutes.

### Key Passes

A key pass is treated as a chance-creation event identified through the event data and used in the project's player analytics.

Key passes are used for:

- chance creation analysis
- chance creation per 90
- scouting profiles
- player similarity features

---

## 6. Event-Derived Assists

The project calculates an event-derived assist metric from event relationships.

This metric is not treated as an official league assist statistic.

It is used for analytical purposes such as:

- assists per 90
- player chance creation
- player comparisons
- exploratory analysis

When reporting this metric, it should be described as an event-derived assist rather than an official assist record.

---

## 7. Pressure Metrics

A pressure is a StatsBomb event representing pressure activity.

The project calculates:

- total pressures
- pressures per 90
- team pressure activity
- player pressure activity

Pressure count measures the volume of recorded pressure events.

It does not by itself measure:

- pressure effectiveness
- whether possession was regained
- defensive success
- tactical quality of a pressing action

Therefore, pressure volume should not be interpreted as a complete measure of pressing quality.

---

## 8. Defensive Metrics

The project uses several defensive event types.

### Tackles

Tackle events are used to measure defensive tackling activity.

Common metric:

`tackles per 90`

### Interceptions

Interception events represent recorded interceptions.

Common metrics:

- total interceptions
- interceptions per 90

### Clearances

Clearance events represent recorded clearances.

Common metrics:

- total clearances
- clearances per 90

### Defensive Activity

The project can combine defensive event rates to describe defensive activity.

Defensive activity is a constructed analytical profile rather than an official single football statistic.

---

## 9. Ball-Carrying Metrics

### Carries

A carry is a recorded event where a player moves with the ball.

Common metrics:

- total carries
- carries per 90

### Dribbles

Dribble events are used to measure dribbling activity.

Common metrics:

- total dribbles
- dribbles per 90

### Successful Dribbles

The project can identify successful dribbles using the recorded dribble outcome.

Successful dribbles can be compared with total dribbles to describe dribbling efficiency.

---

## 10. Duel Metrics

Duel events are used to measure player involvement in physical or contested situations.

Common metrics:

- total duels
- duels per 90
- duel-type breakdowns

The project also examines aerial duel losses.

### Aerial Duels Lost

`Aerial Lost` is treated as a descriptive duel subtype.

The project does not invent an aerial-wins metric from incomplete information.

For scouting percentile calculations, aerial duels lost is treated as a lower-is-better metric.

---

## 11. Ball Retention Metrics

The project uses several events to describe ball-retention and ball-recovery behavior.

### Miscontrols

A miscontrol represents a recorded loss of control of the ball.

Common metric:

`miscontrols per 90`

### Dispossessed

A dispossession represents a recorded event where a player loses possession to an opponent.

Common metric:

`dispossessed per 90`

### Ball Recoveries

Ball Recovery events are used to describe recovery activity.

Common metric:

`ball recoveries per 90`

These metrics can be combined into a broader retention/recovery analytical profile.

---

## 12. Per-90 Methodology

Many player metrics are normalized per 90 minutes.

The project uses validated elapsed StatsBomb match-clock minutes for this calculation.

This includes stoppage time when represented in the lineup timing and match-specific final match-clock data.

The basic concept is:

`per 90 metric = event count or value / minutes played × 90`

The project does not describe this as a universal official definition of per-90 playing time.

---

## 13. Player Exposure Threshold

The main scouting population requires at least:

`900 minutes`

Players below this threshold are excluded from the main scouting feature population.

This reduces the effect of extremely small samples on:

- per-90 metrics
- player comparisons
- scouting profiles
- similarity analysis
- clustering

The resulting scouting population contains 316 players.

---

## 14. Role-Based Analysis

Players are assigned to analytical role groups based on their primary position.

The project currently uses eight analytical role groups:

1. Goalkeeper
2. Centre Back
3. Full Back
4. Defensive Midfielder
5. Central Midfielder
6. Attacking Midfielder
7. Winger
8. Forward

Primary position is determined using accumulated playing minutes by position.

The position with the greatest accumulated minutes is treated as the player's primary position.

---

## 15. Percentile Metrics

The scouting system converts selected player metrics into within-role percentile scores.

A percentile indicates how a player compares with other players in the same analytical role.

For example:

- 90th percentile = higher than approximately 90% of players in that role
- 50th percentile = around the middle of the role population

The project's percentile system is comparative rather than an absolute measure of football quality.

Certain metrics are reversed because lower values are considered better for that metric.

Currently reversed examples include:

- aerial duels lost
- miscontrols
- dispossessed

---

## 16. Scouting Profiles

The project groups football metrics into seven analytical categories:

1. Shooting
2. Chance Creation
3. Passing
4. Defensive
5. Carrying
6. Duels
7. Retention/Recovery

These category profiles are constructed from role-specific percentile metrics.

They are used for:

- player scouting
- player comparison
- similarity analysis
- clustering
- scouting scores

---

## 17. Scouting Score

The project creates a role-aware scouting score from the category profiles.

The score uses transparent, project-defined weights that differ by analytical role.

The score is:

- rule-based
- role-specific
- constructed by the project
- not learned by machine learning
- not a universal measure of player quality

Position share is kept separately as a confidence/versatility indicator rather than being directly treated as player quality.

Goalkeeper scoring is provisional because the current feature set contains fewer goalkeeper-specific metrics.

---

## 18. Progressive Passing Limitation

Progressive passing was investigated during analytics development.

It was not finalized as a core metric.

The reason is that raw pitch-coordinate movement alone does not reliably account for attacking direction and team orientation.

Therefore, the project does not currently claim to have a fully direction-aware progressive-passing metric.

---

## 19. Metric Interpretation Principles

Football Intelligence AI follows several principles when interpreting metrics:

1. Event volume is not automatically event quality.
2. Per-90 metrics should be interpreted alongside playing-time exposure.
3. Small samples can produce unstable rates.
4. Derived metrics should be clearly distinguished from official statistics.
5. Percentiles are relative to the comparison population.
6. Scouting scores are project-defined analytical constructs.
7. Correlation does not establish causation.
8. Machine-learning feature importance does not establish causal importance.

---

## 20. Data Source Principle

The underlying event-level football information comes from StatsBomb Open Data.

Where the project creates an analytical metric from those events, the metric should be described as a project-derived or event-derived metric when it is not directly an official statistic.

The system should avoid presenting derived metrics as official league statistics.