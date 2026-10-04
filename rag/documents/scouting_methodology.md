# Football Intelligence AI — Scouting Methodology

## 1. Purpose

Football Intelligence AI uses a role-aware scouting methodology to transform football performance data into player profiles and comparable scouting scores.

The purpose is to support:

- player discovery
- player comparison
- role-specific scouting
- statistical profiling
- similarity analysis
- exploratory recruitment analysis

The scouting system is an analytical framework created for this project.

It should not be interpreted as an official club scouting rating or an objective universal ranking of football players.

---

## 2. Scouting Population

The main scouting population consists of players who accumulated at least:

`900 minutes`

during the selected Premier League 2015/16 dataset.

This produces:

`316 players`

The exposure threshold is used because very small samples can create unstable per-90 statistics.

A player with only a small number of minutes can otherwise appear unusually strong or weak simply because of limited observations.

---

## 3. Primary Position

Players can appear in multiple positions during a season.

The project determines a player's primary position using accumulated playing minutes.

The position with the greatest accumulated playing time is treated as the player's primary position.

This approach provides a reproducible rule for assigning players to analytical role groups.

It does not claim that a player can only perform one tactical role.

---

## 4. Analytical Role Groups

The project maps primary positions into eight analytical role groups:

1. Goalkeeper
2. Centre Back
3. Full Back
4. Defensive Midfielder
5. Central Midfielder
6. Attacking Midfielder
7. Winger
8. Forward

Role groups are used because comparing every player using exactly the same performance expectations can produce misleading scouting conclusions.

For example, high shot volume may be desirable for a forward but not necessarily for a centre back.

---

## 5. Scouting Feature Base

The scouting feature system is built from event-derived football statistics.

The underlying feature categories include:

- Shooting
- Chance Creation
- Passing
- Defensive
- Carrying
- Duels
- Retention/Recovery

Examples of underlying metrics include:

- shots per 90
- xG per 90
- goals per 90
- key passes per 90
- event-derived assists per 90
- passes per 90
- pass distance per 90
- pressures per 90
- tackles per 90
- interceptions per 90
- clearances per 90
- carries per 90
- dribbles per 90
- duels per 90
- aerial duels lost per 90
- miscontrols per 90
- dispossessed per 90
- ball recoveries per 90

Not every underlying metric is used in every role.

---

## 6. Role-Specific Feature Selection

Different roles emphasize different aspects of football performance.

The project therefore selects relevant features according to the player's analytical role.

For example:

### Goalkeeper

Emphasis is placed on:

- passing
- retention/recovery
- defensive activity

### Centre Back

Emphasis is placed on:

- defensive activity
- passing
- duels
- carrying
- retention/recovery

### Full Back

Emphasis is placed on:

- defensive activity
- passing
- carrying
- chance creation
- retention/recovery

### Defensive Midfielder

Emphasis is placed on:

- defensive activity
- passing
- retention/recovery
- carrying
- chance creation

### Central Midfielder

Emphasis is placed on:

- passing
- defensive activity
- chance creation
- carrying
- retention/recovery

### Attacking Midfielder

Emphasis is placed on:

- chance creation
- shooting
- passing
- carrying
- retention/recovery

### Winger

Emphasis is placed on:

- chance creation
- shooting
- carrying
- passing
- retention/recovery

### Forward

Emphasis is placed on:

- shooting
- chance creation
- duels
- carrying
- retention/recovery

These weights are project-defined assumptions rather than weights learned from historical recruitment outcomes.

---

## 7. Percentile Transformation

Raw performance metrics can have very different scales.

For example:

- passes can occur hundreds of times
- shots occur much less frequently
- interceptions occur at another frequency

The project converts selected metrics into percentile scores within each analytical role.

This creates a common approximate 0–100 scale.

A higher percentile means the player's value is relatively high compared with other players in the same role.

For example:

- 90 = approximately 90th percentile
- 50 = approximately median
- 10 = approximately 10th percentile

These values are relative rather than absolute.

---

## 8. Direction of Metrics

Not every metric has a "higher is better" interpretation.

For example, high values for:

- miscontrols
- dispossessed
- aerial duels lost

can represent undesirable outcomes depending on the analytical context.

The scouting percentile methodology therefore reverses selected lower-is-better metrics.

Current reversed metrics include:

- aerial duels lost
- miscontrols
- dispossessed

This means a player with fewer such events can receive a higher percentile score for that component.

---

## 9. Scouting Category Profiles

The percentile features are grouped into seven scouting categories:

1. Shooting
2. Chance Creation
3. Passing
4. Defensive
5. Carrying
6. Duels
7. Retention/Recovery

Each category represents a different aspect of player performance.

The category profiles allow the system to describe a player's strengths and weaknesses rather than relying only on one overall number.

---

## 10. Role-Aware Scouting Score

The project combines the category profiles into a role-aware scouting score.

The score uses transparent, manually defined weights.

The weights differ by role.

### Goalkeeper

- Passing: 50%
- Retention/Recovery: 30%
- Defensive: 20%

### Centre Back

- Defensive: 40%
- Passing: 25%
- Duels: 20%
- Carrying: 10%
- Retention/Recovery: 5%

### Full Back

- Defensive: 30%
- Passing: 25%
- Carrying: 25%
- Chance Creation: 10%
- Retention/Recovery: 10%

### Defensive Midfielder

- Defensive: 30%
- Passing: 30%
- Retention/Recovery: 20%
- Carrying: 15%
- Chance Creation: 5%

### Central Midfielder

- Passing: 30%
- Defensive: 20%
- Chance Creation: 20%
- Carrying: 20%
- Retention/Recovery: 10%

### Attacking Midfielder

- Chance Creation: 35%
- Shooting: 25%
- Passing: 20%
- Carrying: 15%
- Retention/Recovery: 5%

### Winger

- Chance Creation: 30%
- Shooting: 30%
- Carrying: 25%
- Passing: 10%
- Retention/Recovery: 5%

### Forward

- Shooting: 40%
- Chance Creation: 20%
- Duels: 15%
- Carrying: 10%
- Retention/Recovery: 15%

The weights sum to 100% within each role.

---

## 11. Interpretation of the Scouting Score

The scouting score is a project-defined composite score.

It represents how strongly a player's statistical profile matches the project's role-specific performance framework.

It does not represent:

- transfer value
- market value
- salary value
- future potential
- injury risk
- tactical compatibility with a specific club
- guaranteed future performance
- an official player rating

A high score means the player performs strongly according to the selected statistical dimensions and role-specific weights.

---

## 12. Position Share

The project also calculates position share.

Position share represents the percentage of a player's recorded minutes associated with the player's primary position.

It is kept separate from the scouting score.

This is important because a player can have a high statistical score while having relatively limited exposure in the position used for the comparison.

Position share therefore acts as an additional confidence or versatility indicator rather than directly increasing player quality.

---

## 13. Player Profiles

The scouting system can represent each player using a profile across the seven categories.

A player can therefore be described using a vector such as:

- Shooting
- Chance Creation
- Passing
- Defensive
- Carrying
- Duels
- Retention/Recovery

This provides more information than an overall score alone.

For example, two players could have similar overall scores while having very different strengths.

One may be stronger in passing and defensive activity, while another may be stronger in shooting and chance creation.

---

## 14. Player Ranking

Players can be ranked within their analytical role using the role-aware scouting score.

The ranking should be interpreted as:

"Players whose statistical profiles score highly under this project's role-specific framework."

It should not be interpreted as:

"These are objectively the best football players."

The ranking is dependent on:

- the selected dataset
- the 900-minute exposure threshold
- the selected metrics
- the role definitions
- the percentile methodology
- the manually selected weights

Changing any of these assumptions can change the ranking.

---

## 15. Player Similarity

The scouting features also support a separate player-similarity system.

The similarity model uses a validated 15-feature representation based on per-90 football event metrics.

The final similarity feature set includes:

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

Before calculating similarity, the features are standardized.

Cosine similarity is then used to compare player profiles.

---

## 16. Role-Aware Player Similarity

The similarity system uses the player's analytical role as a comparison constraint.

A player is compared with other players from the same role group.

The role is not inserted as a numerical machine-learning feature.

Instead, it is used to restrict the candidate comparison population.

This reduces obviously inappropriate comparisons between players whose statistical profiles may be similar in some dimensions but who perform fundamentally different roles.

Similarity should therefore be interpreted as:

"How similar are these players statistically under the selected feature representation?"

It does not mean:

- identical tactical role
- identical playing style
- identical quality
- identical potential
- guaranteed interchangeability

---

## 17. Player Clustering

The project also uses unsupervised machine learning to identify statistical player archetypes.

K-Means clustering is applied to the standardized 15-feature player representation.

The number of clusters was evaluated using silhouette scores for:

`K = 2 through 10`

The project selected:

`K = 5`

K=2 had the highest numerical silhouette score, but K=5 produced an almost identical score while providing substantially more interpretable football archetypes.

The resulting five clusters were interpreted as:

1. Goalkeeper
2. Two-Way / High-Volume
3. Finishing Forward
4. Creative Attacker
5. Defensive Player

These names are human interpretations of the statistical clusters.

They are not labels learned directly by K-Means.

Some clusters have lower silhouette scores, indicating overlap between certain player profiles.

Therefore, cluster membership should not be treated as a rigid football position or definitive player type.

---

## 18. Scouting Methodology Limitations

The scouting framework has several important limitations.

### Dataset limitation

The current scouting population comes from one competition-season:

Premier League 2015/16.

### Feature limitation

The model uses the event fields available in the selected StatsBomb Open Data.

It does not currently include:

- transfer values
- salaries
- player wages
- contract information
- injury history
- physical testing data
- scouting reports
- tactical instructions
- live/current performance

### Weight limitation

The scouting score weights are manually defined.

They are not learned from:

- transfer outcomes
- club recruitment decisions
- future player performance
- expert scout labels

### Tactical limitation

Event statistics cannot fully capture tactical context.

A player's role, team system, possession share, teammates, opposition, game state, and tactical instructions can affect event volume and behavior.

### Sample limitation

Even with a 900-minute threshold, one season is still a limited sample.

---

## 19. Recommended Interpretation

The scouting framework should be used as a decision-support tool.

A sensible scouting workflow is:

1. Identify players using statistical filters.
2. Compare players within relevant roles.
3. Inspect category profiles.
4. Examine player similarity.
5. Examine cluster/archetype membership.
6. Consider playing-time exposure and position share.
7. Combine statistical evidence with football context.
8. Use the output to support, not replace, scouting judgment.

---

## 20. Core Principle

Football Intelligence AI does not treat one number as the truth about a football player.

The purpose of the scouting system is to combine:

- role-aware statistical analysis
- transparent feature definitions
- player similarity
- unsupervised archetyping
- machine-learning outputs
- contextual interpretation

into a reproducible analytical framework.

The system should clearly distinguish between measured data, project-derived metrics, modeling assumptions, and interpretation.