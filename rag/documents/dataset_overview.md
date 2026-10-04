# Football Intelligence AI — Dataset Overview

## 1. Project

Football Intelligence AI is an end-to-end football analytics, scouting, machine learning, NLP, RAG, and agentic AI platform.

The project currently uses StatsBomb Open Data as its football event and match-data source.

The raw StatsBomb data is kept separate from the processed project datasets.

---

## 2. Current Dataset Scope

The current validated development dataset is:

- Competition: Premier League
- Season: 2015/16
- StatsBomb competition ID: 2
- StatsBomb season ID: 27
- Matches: 380
- Teams: 20
- Players: 644
- Player-match records: 13,678
- Event records: 1,313,773

The current database therefore represents one competition-season rather than the entire StatsBomb Open Data collection.

An initial survey identified 80 competition-season datasets across 24 competitions in the available raw data.

The other 79 competition-season datasets are not currently loaded into the project database. They are reserved for future expansion after the current analytics, machine learning, and AI pipeline has been validated.

No live or current football data is currently integrated into the platform.

---

## 3. Raw Data

The raw StatsBomb dataset is stored in:

`open-data-master/`

The raw data includes match, lineup, event, and other StatsBomb Open Data resources.

Raw files are treated as immutable source data.

Processed datasets are generated through the project's ETL pipeline rather than modifying the raw files.

---

## 4. Processed Relational Data

The project converts the selected competition-season into five relational tables.

### Matches

One row represents one match.

Key information includes:

- match ID
- match date
- kick-off time
- season
- home team ID
- away team ID
- home score
- away score
- match week
- competition stage
- stadium
- referee
- match result

The final dataset contains 380 matches.

### Teams

One row represents one team.

Columns:

- team ID
- team name

The dataset contains 20 unique teams.

### Players

One row represents one player.

Columns:

- player ID
- player name
- player nickname
- country

The dataset contains 644 unique players.

Some players do not have a nickname in the source data. This is treated as valid source optionality rather than an ETL failure.

### Player Match

One row represents one player participating in one match record.

Columns include:

- match ID
- player ID
- team ID
- jersey number
- position ID
- position
- start reason
- end reason
- from time
- to time
- minutes played

The table contains 13,678 player-match records.

The composite key is:

`(match_id, player_id)`

### Events

One row represents one football event.

The final event table contains 1,313,773 events.

Event information includes:

- event type
- match
- team
- player
- period
- timestamp
- pitch location
- possession
- pressure information
- passing information
- shot information
- carrying information
- duel information
- dribbling information
- interception information
- clearance information

Important event-derived metrics include shots, expected goals (xG), passes, pressures, carries, duels, interceptions, clearances, dribbles, and other event types available in the source data.

---

## 5. Data Quality and Validation

The processed datasets were validated before being loaded into the database.

Key validation results include:

- Duplicate match IDs: 0
- Duplicate player IDs: 0
- Duplicate team IDs: 0
- Duplicate player-match keys: 0
- Duplicate event IDs: 0
- Foreign-key violations: 0
- Invalid match scores: 0
- Invalid event timestamps: 0
- Invalid event xG values: 0
- Negative player minutes: 0
- Missing key relational identifiers: 0

All 380 matches have a detected final match-clock time from the event data.

Player minutes are calculated using lineup timing and the match-specific final match-clock time when required.

---

## 6. Match Results

The 380 matches contain:

- Home wins: 157
- Draws: 107
- Away wins: 116

These values are used by the match-outcome machine learning pipeline.

---

## 7. Scouting Population

For player scouting and several machine-learning tasks, the project uses a minimum exposure threshold of 900 minutes.

This produces a scouting population of:

- 316 players

This threshold reduces the influence of extremely small playing-time samples when constructing player profiles and per-90 statistics.

---

## 8. Football Analytics

The project derives analytical metrics from the event and player-match data.

Examples include:

- goals
- expected goals
- shots
- key passes
- event-derived assists
- passes
- pressure activity
- tackles
- interceptions
- clearances
- carries
- dribbles
- duels
- ball recoveries
- miscontrols
- dispossessions

Many metrics are normalized per 90 minutes for player comparison.

The project's per-90 calculations use the validated elapsed StatsBomb match-clock minutes, including stoppage time.

This is a project methodology choice and should not be interpreted as a universal official definition of per-90 playing time.

---

## 9. Important Metric Limitations

Some analytical metrics are project-defined rather than official league statistics.

For example:

- Event-derived assists are calculated from event relationships and are not official league assist records.
- Pressure counts represent pressure-event volume and do not by themselves measure pressing quality.
- Progressive passing was investigated but was not finalized because raw pitch-coordinate movement does not account for attacking direction/orientation.
- Aerial duels lost is treated as a descriptive loss metric; an aerial-wins metric was not invented from incomplete information.

These limitations should be considered when interpreting analytical or machine-learning outputs.

---

## 10. Machine Learning Dataset

The project has developed machine-learning datasets from the validated football database.

The player similarity pipeline currently uses:

- 316 players
- 15 football performance features
- per-90 event-based metrics

The player clustering pipeline uses the same validated 15-feature player representation.

The player performance prediction pipeline predicts a player's total xG across their next five appearances using information from their previous five appearances.

The match-outcome prediction pipeline uses pre-match information derived from previous team matches to predict:

- HOME_WIN
- DRAW
- AWAY_WIN

All machine-learning pipelines use chronological validation where appropriate to reduce temporal leakage.

---

## 11. RAG Purpose

The RAG component will use project documentation to provide grounded answers about:

- dataset scope
- football metric definitions
- scouting methodology
- machine-learning methodology
- project limitations
- analytical assumptions

RAG is not intended to replace structured SQL analytics or machine-learning models.

The intended architecture is:

User Question
→ determine information type
→ SQL / ML / RAG / Agent
→ retrieve or calculate evidence
→ generate grounded response

The language model should act as an explanation and orchestration layer rather than the source of truth for structured football statistics.

---

## 12. Current Project Limitations

The current project does not claim:

- coverage of all available StatsBomb Open Data competitions and seasons
- live football data
- current player statistics
- current transfer values
- current market values
- official transfer-fee prediction
- universal player-quality rankings

The current database is intentionally limited to Premier League 2015/16 while the core pipeline is developed and validated.

Future expansion can process additional competition-season datasets using the validated ETL and database architecture.

Any cross-competition or cross-season analysis should first account for differences in dataset coverage and feature availability.

---

## 13. Data Attribution

The project uses StatsBomb Open Data.

If the project or derived work is publicly distributed, the applicable StatsBomb Open Data attribution and usage requirements must be followed.