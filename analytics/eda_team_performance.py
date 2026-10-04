import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os


# ------------------------------------------------------------
# Automatic chart saving
# ------------------------------------------------------------

CHART_DIR = "eda_outputs"

os.makedirs(CHART_DIR, exist_ok=True)

existing_charts = [
    filename
    for filename in os.listdir(CHART_DIR)
    if filename.startswith("chart_")
    and filename.endswith(".png")
]

chart_number = len(existing_charts)


def auto_show():
    global chart_number

    chart_number += 1

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            CHART_DIR,
            f"chart_{chart_number:02d}.png"
        ),
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()


plt.show = auto_show

# ----------------------------------------
# 1. Connect to the database
# ----------------------------------------

connection = sqlite3.connect("football.db")


# ----------------------------------------
# 2. League table query
# ----------------------------------------

query = """
SELECT
    t.team_name,

    COUNT(*) AS played,

    SUM(
        CASE
            WHEN (m.home_team_id = t.team_id AND m.home_score > m.away_score)
              OR (m.away_team_id = t.team_id AND m.away_score > m.home_score)
            THEN 1
            ELSE 0
        END
    ) AS wins,

    SUM(
        CASE
            WHEN m.home_score = m.away_score
            THEN 1
            ELSE 0
        END
    ) AS draws,

    SUM(
        CASE
            WHEN (m.home_team_id = t.team_id AND m.home_score < m.away_score)
              OR (m.away_team_id = t.team_id AND m.away_score < m.home_score)
            THEN 1
            ELSE 0
        END
    ) AS losses,

    SUM(
        CASE
            WHEN m.home_team_id = t.team_id THEN m.home_score
            WHEN m.away_team_id = t.team_id THEN m.away_score
            ELSE 0
        END
    ) AS goals_for,

    SUM(
        CASE
            WHEN m.home_team_id = t.team_id THEN m.away_score
            WHEN m.away_team_id = t.team_id THEN m.home_score
            ELSE 0
        END
    ) AS goals_against,

    SUM(
        CASE
            WHEN m.home_team_id = t.team_id
                THEN m.home_score - m.away_score
            WHEN m.away_team_id = t.team_id
                THEN m.away_score - m.home_score
            ELSE 0
        END
    ) AS goal_difference,

    SUM(
        CASE
            WHEN (m.home_team_id = t.team_id AND m.home_score > m.away_score)
              OR (m.away_team_id = t.team_id AND m.away_score > m.home_score)
            THEN 3

            WHEN m.home_score = m.away_score
            THEN 1

            ELSE 0
        END
    ) AS points

FROM teams t

JOIN matches m
    ON t.team_id = m.home_team_id
    OR t.team_id = m.away_team_id

GROUP BY
    t.team_id,
    t.team_name

ORDER BY
    points DESC,
    goal_difference DESC,
    goals_for DESC;
"""


# ----------------------------------------
# 3. Load SQL result into Pandas
# ----------------------------------------

league_table = pd.read_sql_query(query, connection)


# ----------------------------------------
# 5. Display the data
# ----------------------------------------

print("\nLeague Table:")
print(league_table.to_string(index=False))


# ----------------------------------------
# 6. Create points visualization
# ----------------------------------------

plt.figure(figsize=(10, 7))

plt.barh(
    league_table["team_name"],
    league_table["points"]
)

plt.xlabel("Points")
plt.ylabel("Team")
plt.title("Premier League 2015/16 - Points by Team")

plt.gca().invert_yaxis()

plt.tight_layout()
plt.show()

# ----------------------------------------
# 7. Attacking vs defensive performance
# ----------------------------------------

plt.figure(figsize=(10, 7))

plt.scatter(
    league_table["goals_against"],
    league_table["goals_for"]
)

# Calculate league averages
avg_goals_for = league_table["goals_for"].mean()
avg_goals_against = league_table["goals_against"].mean()

# Add league-average reference lines
plt.axhline(
    avg_goals_for,
    linestyle="--",
    label=f"Average Goals For ({avg_goals_for:.1f})"
)

plt.axvline(
    avg_goals_against,
    linestyle="--",
    label=f"Average Goals Against ({avg_goals_against:.1f})"
)

for _, row in league_table.iterrows():
    plt.annotate(
        row["team_name"],
        (
            row["goals_against"],
            row["goals_for"]
        ),
        xytext=(5, 5),
        textcoords="offset points"
    )

plt.xlabel("Goals Against")
plt.ylabel("Goals For")
plt.title("Premier League 2015/16 - Attacking vs Defensive Performance")

plt.tight_layout()
plt.show()

# ----------------------------------------
# 8. Expected goals vs actual goals
# ----------------------------------------

xg_analysis = pd.read_sql_query(
    """
    SELECT
        t.team_name,
        SUM(e.shot_xg) AS expected_goals,
        SUM(
            CASE
                WHEN e.shot_outcome = 'Goal' THEN 1
                ELSE 0
            END
        ) AS actual_goals
    FROM events e
    JOIN teams t
        ON e.team_id = t.team_id
    WHERE e.event_type = 'Shot'
    GROUP BY
        t.team_id,
        t.team_name
    ORDER BY
        expected_goals DESC
    """,
    connection
)

print("\nTeam xG vs Actual Goals:")
print(xg_analysis)

plt.figure(figsize=(10, 7))

plt.scatter(
    xg_analysis["expected_goals"],
    xg_analysis["actual_goals"]
)

for _, row in xg_analysis.iterrows():
    plt.annotate(
        row["team_name"],
        (
            row["expected_goals"],
            row["actual_goals"]
        ),
        xytext=(5, 5),
        textcoords="offset points"
    )

plt.xlabel("Expected Goals (xG)")
plt.ylabel("Actual Goals")
plt.title("Premier League 2015/16 - Expected Goals vs Actual Goals")

plt.tight_layout()
plt.show()

# ----------------------------------------
# 9. Team passing profile
# ----------------------------------------

passing_analysis = pd.read_sql_query(
    """
    SELECT
        t.team_name,
        COUNT(e.event_id) AS total_passes,
        SUM(
            CASE
                WHEN e.pass_outcome IS NULL
                     OR e.pass_outcome = 'Complete'
                THEN 1
                ELSE 0
            END
        ) AS completed_passes,
        ROUND(
            100.0 * SUM(
                CASE
                    WHEN e.pass_outcome IS NULL
                         OR e.pass_outcome = 'Complete'
                    THEN 1
                    ELSE 0
                END
            ) / COUNT(e.event_id),
            2
        ) AS pass_completion_pct
    FROM events e
    JOIN teams t
        ON e.team_id = t.team_id
    WHERE e.event_type = 'Pass'
    GROUP BY
        t.team_id,
        t.team_name
    ORDER BY
        total_passes DESC
    """,
    connection
)

print("\nTeam Passing Profile:")
print(passing_analysis)

plt.figure(figsize=(10, 7))

plt.scatter(
    passing_analysis["total_passes"],
    passing_analysis["pass_completion_pct"]
)

for _, row in passing_analysis.iterrows():
    plt.annotate(
        row["team_name"],
        (
            row["total_passes"],
            row["pass_completion_pct"]
        ),
        xytext=(5, 5),
        textcoords="offset points"
    )

plt.xlabel("Total Passes")
plt.ylabel("Pass Completion (%)")
plt.title("Premier League 2015/16 - Team Passing Profile")

plt.tight_layout()
plt.show()

# ----------------------------------------
# 10. Team pressure activity vs points
# ----------------------------------------

pressure_analysis = pd.read_sql_query(
    """
    SELECT
        t.team_name,
        COUNT(e.event_id) AS pressures
    FROM events e
    JOIN teams t
        ON e.team_id = t.team_id
    WHERE e.event_type = 'Pressure'
    GROUP BY
        t.team_id,
        t.team_name
    """,
    connection
)

pressure_analysis = pressure_analysis.merge(
    league_table[["team_name", "points"]],
    on="team_name"
)

print("\nTeam Pressure Activity vs Points:")
print(pressure_analysis.sort_values("pressures", ascending=False))

plt.figure(figsize=(10, 7))

plt.scatter(
    pressure_analysis["pressures"],
    pressure_analysis["points"]
)

for _, row in pressure_analysis.iterrows():
    plt.annotate(
        row["team_name"],
        (
            row["pressures"],
            row["points"]
        ),
        xytext=(5, 5),
        textcoords="offset points"
    )

plt.xlabel("Total Pressures")
plt.ylabel("League Points")
plt.title("Premier League 2015/16 - Pressure Activity vs League Points")

plt.tight_layout()
plt.show()

# ----------------------------------------
# 11. Player attacking output
# ----------------------------------------

player_attack = pd.read_sql_query(
    """
    WITH player_minutes AS (
        SELECT
            player_id,
            SUM(minutes_played) AS total_minutes
        FROM player_match
        GROUP BY player_id
    ),

    player_shooting AS (
        SELECT
            player_id,
            SUM(shot_xg) AS expected_goals,
            SUM(
                CASE
                    WHEN shot_outcome = 'Goal' THEN 1
                    ELSE 0
                END
            ) AS goals
        FROM events
        WHERE event_type = 'Shot'
        GROUP BY player_id
    )

    SELECT
        p.player_name,
        pm.total_minutes,
        COALESCE(ps.expected_goals, 0) AS expected_goals,
        COALESCE(ps.goals, 0) AS goals,

        ROUND(
            COALESCE(ps.expected_goals, 0)
            / (pm.total_minutes / 90.0),
            2
        ) AS xg_per_90,

        ROUND(
            COALESCE(ps.goals, 0)
            / (pm.total_minutes / 90.0),
            2
        ) AS goals_per_90

    FROM player_minutes pm

    JOIN players p
        ON pm.player_id = p.player_id

    LEFT JOIN player_shooting ps
        ON pm.player_id = ps.player_id

    WHERE pm.total_minutes >= 900

    ORDER BY goals_per_90 DESC
    """,
    connection
)

print("\nPlayer Attacking Output:")
print(player_attack.head(20))

plt.figure(figsize=(10, 7))

plt.scatter(
    player_attack["xg_per_90"],
    player_attack["goals_per_90"]
)

plt.xlabel("Expected Goals per 90")
plt.ylabel("Goals per 90")
plt.title("Premier League 2015/16 - Player xG/90 vs Goals/90")

plt.tight_layout()
plt.show()

# ----------------------------------------
# 12. Player chance creation
# ----------------------------------------

player_creation = pd.read_sql_query(
    """
    WITH player_minutes AS (
        SELECT
            player_id,
            SUM(minutes_played) AS total_minutes
        FROM player_match
        GROUP BY player_id
    ),

    key_passes AS (
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
        GROUP BY pass_event.player_id
    ),

    assists AS (
        SELECT
            pass_event.player_id,
            COUNT(*) AS assists
        FROM events shot
        JOIN events pass_event
            ON shot.shot_key_pass_id = pass_event.event_id
           AND pass_event.event_type = 'Pass'
        WHERE
            shot.event_type = 'Shot'
            AND shot.shot_key_pass_id IS NOT NULL
            AND shot.shot_outcome = 'Goal'
        GROUP BY pass_event.player_id
    )

    SELECT
        p.player_name,
        pm.total_minutes,

        COALESCE(kp.key_passes, 0) AS key_passes,
        COALESCE(a.assists, 0) AS assists,

        ROUND(
            COALESCE(kp.key_passes, 0)
            / (pm.total_minutes / 90.0),
            2
        ) AS key_passes_per_90,

        ROUND(
            COALESCE(a.assists, 0)
            / (pm.total_minutes / 90.0),
            2
        ) AS assists_per_90

    FROM player_minutes pm

    JOIN players p
        ON pm.player_id = p.player_id

    LEFT JOIN key_passes kp
        ON pm.player_id = kp.player_id

    LEFT JOIN assists a
        ON pm.player_id = a.player_id

    WHERE pm.total_minutes >= 900

    ORDER BY key_passes_per_90 DESC
    """,
    connection
)

print("\nPlayer Chance Creation:")
print(player_creation.head(20))

plt.figure(figsize=(10, 7))

plt.scatter(
    player_creation["key_passes_per_90"],
    player_creation["assists_per_90"]
)

plt.xlabel("Key Passes per 90")
plt.ylabel("Event-Derived Assists per 90")
plt.title("Premier League 2015/16 - Player Chance Creation")

plt.tight_layout()
plt.show()

# ----------------------------------------
# 13. Player passing profile
# ----------------------------------------

player_passing = pd.read_sql_query(
    """
    WITH player_minutes AS (
        SELECT
            player_id,
            SUM(minutes_played) AS total_minutes
        FROM player_match
        GROUP BY player_id
    ),

    player_passes AS (
        SELECT
            player_id,

            COUNT(*) AS total_passes,

            SUM(
                CASE
                    WHEN pass_outcome IS NULL
                         OR pass_outcome = 'Complete'
                    THEN 1
                    ELSE 0
                END
            ) AS completed_passes

        FROM events
        WHERE event_type = 'Pass'
        GROUP BY player_id
    )

    SELECT
        p.player_name,
        pm.total_minutes,

        COALESCE(pp.total_passes, 0) AS total_passes,
        COALESCE(pp.completed_passes, 0) AS completed_passes,

        ROUND(
            COALESCE(pp.total_passes, 0)
            / (pm.total_minutes / 90.0),
            2
        ) AS passes_per_90,

        ROUND(
            100.0 * COALESCE(pp.completed_passes, 0)
            / NULLIF(pp.total_passes, 0),
            2
        ) AS pass_completion_pct

    FROM player_minutes pm

    JOIN players p
        ON pm.player_id = p.player_id

    LEFT JOIN player_passes pp
        ON pm.player_id = pp.player_id

    WHERE pm.total_minutes >= 900

    ORDER BY passes_per_90 DESC
    """,
    connection
)

print("\nPlayer Passing Profile:")
print(player_passing.head(20))

plt.figure(figsize=(10, 7))

plt.scatter(
    player_passing["passes_per_90"],
    player_passing["pass_completion_pct"]
)

plt.xlabel("Passes per 90")
plt.ylabel("Pass Completion (%)")
plt.title("Premier League 2015/16 - Player Passing Profile")

plt.tight_layout()
plt.show()

# ----------------------------------------
# 14. Player defensive activity
# ----------------------------------------

player_defense = pd.read_sql_query(
    """
    WITH player_minutes AS (
        SELECT
            player_id,
            SUM(minutes_played) AS total_minutes
        FROM player_match
        GROUP BY player_id
    ),

    defensive_events AS (
        SELECT
            player_id,

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
            ) AS interceptions

        FROM events

        WHERE event_type IN (
            'Pressure',
            'Duel',
            'Interception'
        )

        GROUP BY player_id
    )

    SELECT
        p.player_name,
        pm.total_minutes,

        COALESCE(de.pressures, 0) AS pressures,
        COALESCE(de.tackles, 0) AS tackles,
        COALESCE(de.interceptions, 0) AS interceptions,

        ROUND(
            COALESCE(de.pressures, 0)
            / (pm.total_minutes / 90.0),
            2
        ) AS pressures_per_90,

        ROUND(
            COALESCE(de.tackles, 0)
            / (pm.total_minutes / 90.0),
            2
        ) AS tackles_per_90,

        ROUND(
            COALESCE(de.interceptions, 0)
            / (pm.total_minutes / 90.0),
            2
        ) AS interceptions_per_90

    FROM player_minutes pm

    JOIN players p
        ON pm.player_id = p.player_id

    LEFT JOIN defensive_events de
        ON pm.player_id = de.player_id

    WHERE pm.total_minutes >= 900

    ORDER BY pressures_per_90 DESC
    """,
    connection
)

print("\nPlayer Defensive Activity:")
print(player_defense.head(20))

plt.figure(figsize=(10, 7))

plt.scatter(
    player_defense["pressures_per_90"],
    player_defense["tackles_per_90"]
)

plt.xlabel("Pressures per 90")
plt.ylabel("Tackles per 90")
plt.title("Premier League 2015/16 - Player Defensive Activity")

plt.tight_layout()
plt.show()

# ----------------------------------------
# 15. Player carrying and dribbling
# ----------------------------------------

player_carrying = pd.read_sql_query(
    """
    WITH player_minutes AS (
        SELECT
            player_id,
            SUM(minutes_played) AS total_minutes
        FROM player_match
        GROUP BY player_id
    ),

    carrying_events AS (
        SELECT
            player_id,

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

            SUM(
                CASE
                    WHEN event_type = 'Dribble'
                         AND dribble_outcome = 'Complete'
                    THEN 1
                    ELSE 0
                END
            ) AS successful_dribbles

        FROM events

        WHERE event_type IN (
            'Carry',
            'Dribble'
        )

        GROUP BY player_id
    )

    SELECT
        p.player_name,
        pm.total_minutes,

        COALESCE(ce.carries, 0) AS carries,
        COALESCE(ce.dribbles, 0) AS dribbles,
        COALESCE(ce.successful_dribbles, 0) AS successful_dribbles,

        ROUND(
            COALESCE(ce.carries, 0)
            / (pm.total_minutes / 90.0),
            2
        ) AS carries_per_90,

        ROUND(
            COALESCE(ce.dribbles, 0)
            / (pm.total_minutes / 90.0),
            2
        ) AS dribbles_per_90,

        ROUND(
            COALESCE(ce.successful_dribbles, 0)
            / (pm.total_minutes / 90.0),
            2
        ) AS successful_dribbles_per_90

    FROM player_minutes pm

    JOIN players p
        ON pm.player_id = p.player_id

    LEFT JOIN carrying_events ce
        ON pm.player_id = ce.player_id

    WHERE pm.total_minutes >= 900

    ORDER BY carries_per_90 DESC
    """,
    connection
)

print("\nPlayer Carrying and Dribbling:")
print(player_carrying.head(20))

plt.figure(figsize=(10, 7))

plt.scatter(
    player_carrying["carries_per_90"],
    player_carrying["successful_dribbles_per_90"]
)

plt.xlabel("Carries per 90")
plt.ylabel("Successful Dribbles per 90")
plt.title("Premier League 2015/16 - Player Carrying vs Dribbling")

plt.tight_layout()
plt.show()

# ----------------------------------------
# 16. Player role group distribution
# ----------------------------------------

role_distribution = pd.read_sql_query(
    """
    WITH player_minutes AS (
        SELECT
            player_id,
            SUM(minutes_played) AS total_minutes
        FROM player_match
        GROUP BY player_id
    ),

    position_minutes AS (
        SELECT
            pm.player_id,
            pm.position,
            SUM(pm.minutes_played) AS position_minutes
        FROM player_match pm
        JOIN player_minutes pmin
            ON pm.player_id = pmin.player_id
        WHERE
            pmin.total_minutes >= 900
            AND pm.position IS NOT NULL
        GROUP BY
            pm.player_id,
            pm.position
    ),

    primary_positions AS (
        SELECT
            player_id,
            position,
            position_minutes,
            ROW_NUMBER() OVER (
                PARTITION BY player_id
                ORDER BY position_minutes DESC
            ) AS rn
        FROM position_minutes
    ),

    primary_role_groups AS (
        SELECT
            player_id,

            CASE

                WHEN position = 'Goalkeeper'
                    THEN 'Goalkeeper'

                WHEN position IN (
                    'Left Center Back',
                    'Right Center Back'
                )
                    THEN 'Centre Back'

                WHEN position IN (
                    'Left Back',
                    'Right Back'
                )
                    THEN 'Full Back'

                WHEN position IN (
                    'Left Defensive Midfield',
                    'Right Defensive Midfield',
                    'Center Defensive Midfield'
                )
                    THEN 'Defensive Midfielder'

                WHEN position IN (
                    'Left Center Midfield',
                    'Right Center Midfield',
                    'Left Midfield',
                    'Right Midfield'
                )
                    THEN 'Central Midfielder'

                WHEN position = 'Center Attacking Midfield'
                    THEN 'Attacking Midfielder'

                WHEN position IN (
                    'Left Wing',
                    'Right Wing'
                )
                    THEN 'Winger'

                WHEN position IN (
                    'Center Forward',
                    'Left Center Forward',
                    'Right Center Forward'
                )
                    THEN 'Forward'

                ELSE 'Other'

            END AS role_group

        FROM primary_positions

        WHERE rn = 1
    )

    SELECT
        role_group,
        COUNT(*) AS players
    FROM primary_role_groups
    GROUP BY role_group
    ORDER BY players DESC;
    """,
    connection
)

print("\nPlayer Role Group Distribution:")
print(role_distribution.to_string(index=False))

plt.figure(figsize=(10, 7))

plt.bar(
    role_distribution["role_group"],
    role_distribution["players"]
)

plt.xlabel("Role Group")
plt.ylabel("Number of Players")
plt.title("Premier League 2015/16 - Player Role Group Distribution")

plt.xticks(rotation=30)

plt.tight_layout()
plt.show()

# ============================================================
# EDA 12 — Average xG per 90 by Role Group
# ============================================================

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

position_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE position IS NOT NULL
    GROUP BY player_id, position
""", connection)

position_ranked = position_minutes.copy()

position_ranked["rank"] = (
    position_ranked
    .groupby("player_id")["position_minutes"]
    .rank(method="first", ascending=False)
)

primary_positions = position_ranked[
    position_ranked["rank"] == 1
].copy()

primary_positions = primary_positions[
    ["player_id", "position"]
].rename(
    columns={"position": "primary_position"}
)

player_xg = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(shot_xg) AS total_xg
    FROM events
    WHERE
        event_type = 'Shot'
        AND shot_xg IS NOT NULL
    GROUP BY player_id
""", connection)

role_df = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_xg, on="player_id", how="left")
)

role_df["total_xg"] = role_df["total_xg"].fillna(0)

# Keep the same 900-minute exposure threshold
role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()


def assign_role(position):
    if position == "Goalkeeper":
        return "Goalkeeper"

    elif position in [
        "Left Center Back",
        "Right Center Back"
    ]:
        return "Centre Back"

    elif position in [
        "Left Back",
        "Right Back"
    ]:
        return "Full Back"

    elif position in [
        "Left Defensive Midfield",
        "Right Defensive Midfield",
        "Center Defensive Midfield"
    ]:
        return "Defensive Midfielder"

    elif position in [
        "Left Center Midfield",
        "Right Center Midfield",
        "Center Midfield",
        "Left Midfield",
        "Right Midfield"
    ]:
        return "Central Midfielder"

    elif position == "Center Attacking Midfield":
        return "Attacking Midfielder"

    elif position in [
        "Left Wing",
        "Right Wing"
    ]:
        return "Winger"

    elif position in [
        "Center Forward",
        "Left Center Forward",
        "Right Center Forward"
    ]:
        return "Forward"

    else:
        return "Other"


role_df["role_group"] = role_df[
    "primary_position"
].apply(assign_role)

role_df["xg_per_90"] = (
    role_df["total_xg"]
    / (role_df["total_minutes"] / 90)
)

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_xg_per_90=("xg_per_90", "mean")
    )
    .reset_index()
    .sort_values(
        "avg_xg_per_90",
        ascending=False
    )
)

print("\n" + "=" * 60)
print("EDA 12 — Average xG per 90 by Role Group")
print("=" * 60)

print(role_summary)

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_xg_per_90"]
)

plt.title("Average xG per 90 by Role Group")
plt.xlabel("Role Group")
plt.ylabel("Average xG per 90")
plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 13 — Average Goals per 90 by Role Group
# ============================================================

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

position_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE position IS NOT NULL
    GROUP BY player_id, position
""", connection)

# Determine each player's primary position
# based on the position in which they played the most minutes.

position_ranked = position_minutes.copy()

position_ranked["rank"] = (
    position_ranked
    .groupby("player_id")["position_minutes"]
    .rank(method="first", ascending=False)
)

primary_positions = position_ranked[
    position_ranked["rank"] == 1
].copy()

primary_positions = primary_positions[
    ["player_id", "position"]
].rename(
    columns={"position": "primary_position"}
)

# Calculate goals from Shot events.
player_goals = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(
            CASE
                WHEN shot_outcome = 'Goal'
                THEN 1
                ELSE 0
            END
        ) AS goals
    FROM events
    WHERE event_type = 'Shot'
    GROUP BY player_id
""", connection)

# Combine player exposure, position and goals.
role_df = (
    player_minutes
    .merge(
        primary_positions,
        on="player_id",
        how="left"
    )
    .merge(
        player_goals,
        on="player_id",
        how="left"
    )
)

role_df["goals"] = role_df["goals"].fillna(0)

# Keep the same 900-minute exposure threshold.
role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()


# ------------------------------------------------------------
# Assign analytical role group
# ------------------------------------------------------------

def assign_role(position):

    if position == "Goalkeeper":
        return "Goalkeeper"

    elif position in [
        "Left Center Back",
        "Right Center Back"
    ]:
        return "Centre Back"

    elif position in [
        "Left Back",
        "Right Back"
    ]:
        return "Full Back"

    elif position in [
        "Left Defensive Midfield",
        "Right Defensive Midfield",
        "Center Defensive Midfield"
    ]:
        return "Defensive Midfielder"

    elif position in [
        "Left Center Midfield",
        "Right Center Midfield",
        "Center Midfield",
        "Left Midfield",
        "Right Midfield"
    ]:
        return "Central Midfielder"

    elif position == "Center Attacking Midfield":
        return "Attacking Midfielder"

    elif position in [
        "Left Wing",
        "Right Wing"
    ]:
        return "Winger"

    elif position in [
        "Center Forward",
        "Left Center Forward",
        "Right Center Forward"
    ]:
        return "Forward"

    else:
        return "Other"


role_df["role_group"] = (
    role_df["primary_position"]
    .apply(assign_role)
)


# ------------------------------------------------------------
# Calculate goals per 90
# ------------------------------------------------------------

role_df["goals_per_90"] = (
    role_df["goals"]
    / (role_df["total_minutes"] / 90)
)


# ------------------------------------------------------------
# Average goals per 90 within each role
# ------------------------------------------------------------

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_goals_per_90=("goals_per_90", "mean")
    )
    .reset_index()
    .sort_values(
        "avg_goals_per_90",
        ascending=False
    )
)


# ------------------------------------------------------------
# Display results
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("EDA 13 — Average Goals per 90 by Role Group")
print("=" * 60)

print(
    role_summary.to_string(index=False)
)


# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_goals_per_90"]
)

plt.title(
    "Average Goals per 90 by Role Group"
)   

plt.xlabel("Role Group")
plt.ylabel("Average Goals per 90")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()
plt.show()

# ============================================================
# EDA 14 — Average Key Passes per 90 by Role Group
# ============================================================

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

position_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE position IS NOT NULL
    GROUP BY player_id, position
""", connection)

# Determine primary position by minutes played
position_ranked = position_minutes.copy()

position_ranked["rank"] = (
    position_ranked
    .groupby("player_id")["position_minutes"]
    .rank(
        method="first",
        ascending=False
    )
)

primary_positions = position_ranked[
    position_ranked["rank"] == 1
].copy()

primary_positions = primary_positions[
    ["player_id", "position"]
].rename(
    columns={
        "position": "primary_position"
    }
)

# Calculate key passes from shots that reference
# a previous pass through shot_key_pass_id.
player_key_passes = pd.read_sql_query("""
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
    GROUP BY
        pass_event.player_id
""", connection)

# Combine exposure, position and key passes
role_df = (
    player_minutes
    .merge(
        primary_positions,
        on="player_id",
        how="left"
    )
    .merge(
        player_key_passes,
        on="player_id",
        how="left"
    )
)

role_df["key_passes"] = (
    role_df["key_passes"].fillna(0)
)

# Apply the validated 900-minute threshold
role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()


# ------------------------------------------------------------
# Assign analytical role group
# ------------------------------------------------------------

def assign_role(position):

    if position == "Goalkeeper":
        return "Goalkeeper"

    elif position in [
        "Left Center Back",
        "Right Center Back"
    ]:
        return "Centre Back"

    elif position in [
        "Left Back",
        "Right Back"
    ]:
        return "Full Back"

    elif position in [
        "Left Defensive Midfield",
        "Right Defensive Midfield",
        "Center Defensive Midfield"
    ]:
        return "Defensive Midfielder"

    elif position in [
        "Left Center Midfield",
        "Right Center Midfield",
        "Center Midfield",
        "Left Midfield",
        "Right Midfield"
    ]:
        return "Central Midfielder"

    elif position == "Center Attacking Midfield":
        return "Attacking Midfielder"

    elif position in [
        "Left Wing",
        "Right Wing"
    ]:
        return "Winger"

    elif position in [
        "Center Forward",
        "Left Center Forward",
        "Right Center Forward"
    ]:
        return "Forward"

    else:
        return "Other"


role_df["role_group"] = (
    role_df["primary_position"]
    .apply(assign_role)
)


# ------------------------------------------------------------
# Calculate key passes per 90
# ------------------------------------------------------------

role_df["key_passes_per_90"] = (
    role_df["key_passes"]
    / (role_df["total_minutes"] / 90)
)


# ------------------------------------------------------------
# Average key passes per 90 by role
# ------------------------------------------------------------

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_key_passes_per_90=(
            "key_passes_per_90",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "avg_key_passes_per_90",
        ascending=False
    )
)


# ------------------------------------------------------------
# Display results
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("EDA 14 — Average Key Passes per 90 by Role Group")
print("=" * 60)

print(
    role_summary.to_string(index=False)
)


# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_key_passes_per_90"]
)

plt.title(
    "Average Key Passes per 90 by Role Group"
)

plt.xlabel("Role Group")
plt.ylabel("Average Key Passes per 90")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()
plt.show()

# ============================================================
# EDA 15 — Average Event-Derived Assists per 90 by Role Group
# ============================================================

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)


position_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE position IS NOT NULL
    GROUP BY player_id, position
""", connection)


# Determine primary position by minutes played
position_ranked = position_minutes.copy()

position_ranked["rank"] = (
    position_ranked
    .groupby("player_id")["position_minutes"]
    .rank(
        method="first",
        ascending=False
    )
)


primary_positions = position_ranked[
    position_ranked["rank"] == 1
].copy()

primary_positions = primary_positions[
    ["player_id", "position"]
].rename(
    columns={
        "position": "primary_position"
    }
)


# ------------------------------------------------------------
# Calculate event-derived assists
# ------------------------------------------------------------
# A goal-ending shot references the pass that created the chance
# through shot_key_pass_id.
#
# Shot
#   ↓
# shot_key_pass_id
#   ↓
# referenced Pass event
#   ↓
# passer
#
# Therefore the passer receives the assist.

player_assists = pd.read_sql_query("""
    SELECT
        pass_event.player_id,
        COUNT(*) AS assists
    FROM events shot
    JOIN events pass_event
        ON shot.shot_key_pass_id = pass_event.event_id
       AND pass_event.event_type = 'Pass'
    WHERE
        shot.event_type = 'Shot'
        AND shot.shot_key_pass_id IS NOT NULL
        AND shot.shot_outcome = 'Goal'
    GROUP BY
        pass_event.player_id
""", connection)


# ------------------------------------------------------------
# Combine player exposure, position and assists
# ------------------------------------------------------------

role_df = (
    player_minutes
    .merge(
        primary_positions,
        on="player_id",
        how="left"
    )
    .merge(
        player_assists,
        on="player_id",
        how="left"
    )
)


role_df["assists"] = (
    role_df["assists"].fillna(0)
)


# Keep the validated 900-minute population
role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()


# ------------------------------------------------------------
# Assign analytical role group
# ------------------------------------------------------------

def assign_role(position):

    if position == "Goalkeeper":
        return "Goalkeeper"

    elif position in [
        "Left Center Back",
        "Right Center Back"
    ]:
        return "Centre Back"

    elif position in [
        "Left Back",
        "Right Back"
    ]:
        return "Full Back"

    elif position in [
        "Left Defensive Midfield",
        "Right Defensive Midfield",
        "Center Defensive Midfield"
    ]:
        return "Defensive Midfielder"

    elif position in [
        "Left Center Midfield",
        "Right Center Midfield",
        "Center Midfield",
        "Left Midfield",
        "Right Midfield"
    ]:
        return "Central Midfielder"

    elif position == "Center Attacking Midfield":
        return "Attacking Midfielder"

    elif position in [
        "Left Wing",
        "Right Wing"
    ]:
        return "Winger"

    elif position in [
        "Center Forward",
        "Left Center Forward",
        "Right Center Forward"
    ]:
        return "Forward"

    else:
        return "Other"


role_df["role_group"] = (
    role_df["primary_position"]
    .apply(assign_role)
)


# ------------------------------------------------------------
# Calculate assists per 90
# ------------------------------------------------------------

role_df["assists_per_90"] = (
    role_df["assists"]
    / (role_df["total_minutes"] / 90)
)


# ------------------------------------------------------------
# Average assists per 90 by role
# ------------------------------------------------------------

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_assists_per_90=(
            "assists_per_90",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "avg_assists_per_90",
        ascending=False
    )
)


# ------------------------------------------------------------
# Display results
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("EDA 15 — Average Event-Derived Assists per 90 by Role Group")
print("=" * 60)

print(
    role_summary.to_string(index=False)
)


# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_assists_per_90"]
)

plt.title(
    "Average Event-Derived Assists per 90 by Role Group"
)

plt.xlabel("Role Group")
plt.ylabel("Average Event-Derived Assists per 90")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()
plt.show()

# ============================================================
# EDA 16 — Average Pressures per 90 by Role Group
# ============================================================

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)


position_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE position IS NOT NULL
    GROUP BY player_id, position
""", connection)


# ------------------------------------------------------------
# Determine primary position by minutes played
# ------------------------------------------------------------

position_ranked = position_minutes.copy()

position_ranked["rank"] = (
    position_ranked
    .groupby("player_id")["position_minutes"]
    .rank(
        method="first",
        ascending=False
    )
)


primary_positions = position_ranked[
    position_ranked["rank"] == 1
].copy()

primary_positions = primary_positions[
    ["player_id", "position"]
].rename(
    columns={
        "position": "primary_position"
    }
)


# ------------------------------------------------------------
# Calculate player pressures
# ------------------------------------------------------------

player_pressures = pd.read_sql_query("""
    SELECT
        player_id,
        COUNT(*) AS pressures
    FROM events
    WHERE
        event_type = 'Pressure'
        AND player_id IS NOT NULL
    GROUP BY
        player_id
""", connection)


# ------------------------------------------------------------
# Combine player exposure, position and pressures
# ------------------------------------------------------------

role_df = (
    player_minutes
    .merge(
        primary_positions,
        on="player_id",
        how="left"
    )
    .merge(
        player_pressures,
        on="player_id",
        how="left"
    )
)


role_df["pressures"] = (
    role_df["pressures"].fillna(0)
)


# Keep the validated 900-minute population
role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()


# ------------------------------------------------------------
# Assign analytical role group
# ------------------------------------------------------------

def assign_role(position):

    if position == "Goalkeeper":
        return "Goalkeeper"

    elif position in [
        "Left Center Back",
        "Right Center Back"
    ]:
        return "Centre Back"

    elif position in [
        "Left Back",
        "Right Back"
    ]:
        return "Full Back"

    elif position in [
        "Left Defensive Midfield",
        "Right Defensive Midfield",
        "Center Defensive Midfield"
    ]:
        return "Defensive Midfielder"

    elif position in [
        "Left Center Midfield",
        "Right Center Midfield",
        "Center Midfield",
        "Left Midfield",
        "Right Midfield"
    ]:
        return "Central Midfielder"

    elif position == "Center Attacking Midfield":
        return "Attacking Midfielder"

    elif position in [
        "Left Wing",
        "Right Wing"
    ]:
        return "Winger"

    elif position in [
        "Center Forward",
        "Left Center Forward",
        "Right Center Forward"
    ]:
        return "Forward"

    else:
        return "Other"


role_df["role_group"] = (
    role_df["primary_position"]
    .apply(assign_role)
)


# ------------------------------------------------------------
# Calculate pressures per 90
# ------------------------------------------------------------

role_df["pressures_per_90"] = (
    role_df["pressures"]
    / (role_df["total_minutes"] / 90)
)


# ------------------------------------------------------------
# Average pressures per 90 by role
# ------------------------------------------------------------

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_pressures_per_90=(
            "pressures_per_90",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "avg_pressures_per_90",
        ascending=False
    )
)


# ------------------------------------------------------------
# Display results
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("EDA 16 — Average Pressures per 90 by Role Group")
print("=" * 60)

print(
    role_summary.to_string(index=False)
)


# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_pressures_per_90"]
)

plt.title(
    "Average Pressures per 90 by Role Group"
)

plt.xlabel("Role Group")
plt.ylabel("Average Pressures per 90")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()
plt.show()

# ============================================================
# EDA 17 — Average Tackles per 90 by Role Group
# ============================================================

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

position_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE position IS NOT NULL
    GROUP BY player_id, position
""", connection)

position_ranked = position_minutes.copy()

position_ranked["rank"] = (
    position_ranked
    .groupby("player_id")["position_minutes"]
    .rank(method="first", ascending=False)
)

primary_positions = position_ranked[
    position_ranked["rank"] == 1
][["player_id", "position"]].rename(
    columns={"position": "primary_position"}
)

player_tackles = pd.read_sql_query("""
    SELECT
        player_id,
        COUNT(*) AS tackles
    FROM events
    WHERE
        event_type = 'Duel'
        AND duel_type = 'Tackle'
        AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

role_df = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_tackles, on="player_id", how="left")
)

role_df["tackles"] = role_df["tackles"].fillna(0)

role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()


def assign_role(position):

    if position == "Goalkeeper":
        return "Goalkeeper"

    elif position in [
        "Left Center Back",
        "Right Center Back"
    ]:
        return "Centre Back"

    elif position in [
        "Left Back",
        "Right Back"
    ]:
        return "Full Back"

    elif position in [
        "Left Defensive Midfield",
        "Right Defensive Midfield",
        "Center Defensive Midfield"
    ]:
        return "Defensive Midfielder"

    elif position in [
        "Left Center Midfield",
        "Right Center Midfield",
        "Center Midfield",
        "Left Midfield",
        "Right Midfield"
    ]:
        return "Central Midfielder"

    elif position == "Center Attacking Midfield":
        return "Attacking Midfielder"

    elif position in [
        "Left Wing",
        "Right Wing"
    ]:
        return "Winger"

    elif position in [
        "Center Forward",
        "Left Center Forward",
        "Right Center Forward"
    ]:
        return "Forward"

    else:
        return "Other"


role_df["role_group"] = (
    role_df["primary_position"].apply(assign_role)
)

role_df["tackles_per_90"] = (
    role_df["tackles"]
    / (role_df["total_minutes"] / 90)
)

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_tackles_per_90=("tackles_per_90", "mean")
    )
    .reset_index()
    .sort_values("avg_tackles_per_90", ascending=False)
)

print("\n" + "=" * 60)
print("EDA 17 — Average Tackles per 90 by Role Group")
print("=" * 60)

print(role_summary.to_string(index=False))

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_tackles_per_90"]
)

plt.title("Average Tackles per 90 by Role Group")
plt.xlabel("Role Group")
plt.ylabel("Average Tackles per 90")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 18 — Average Interceptions per 90 by Role Group
# ============================================================

player_interceptions = pd.read_sql_query("""
    SELECT
        player_id,
        COUNT(*) AS interceptions
    FROM events
    WHERE
        event_type = 'Interception'
        AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

role_df = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_interceptions, on="player_id", how="left")
)

role_df["interceptions"] = (
    role_df["interceptions"].fillna(0)
)

role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()

role_df["role_group"] = (
    role_df["primary_position"].apply(assign_role)
)

role_df["interceptions_per_90"] = (
    role_df["interceptions"]
    / (role_df["total_minutes"] / 90)
)

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_interceptions_per_90=(
            "interceptions_per_90",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "avg_interceptions_per_90",
        ascending=False
    )
)

print("\n" + "=" * 60)
print("EDA 18 — Average Interceptions per 90 by Role Group")
print("=" * 60)

print(role_summary.to_string(index=False))

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_interceptions_per_90"]
)

plt.title(
    "Average Interceptions per 90 by Role Group"
)

plt.xlabel("Role Group")
plt.ylabel("Average Interceptions per 90")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 19 — Average Clearances per 90 by Role Group
# ============================================================

player_clearances = pd.read_sql_query("""
    SELECT
        player_id,
        COUNT(*) AS clearances
    FROM events
    WHERE
        event_type = 'Clearance'
        AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

role_df = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_clearances, on="player_id", how="left")
)

role_df["clearances"] = (
    role_df["clearances"].fillna(0)
)

role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()

role_df["role_group"] = (
    role_df["primary_position"].apply(assign_role)
)

role_df["clearances_per_90"] = (
    role_df["clearances"]
    / (role_df["total_minutes"] / 90)
)

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_clearances_per_90=(
            "clearances_per_90",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "avg_clearances_per_90",
        ascending=False
    )
)

print("\n" + "=" * 60)
print("EDA 19 — Average Clearances per 90 by Role Group")
print("=" * 60)

print(role_summary.to_string(index=False))

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_clearances_per_90"]
)

plt.title(
    "Average Clearances per 90 by Role Group"
)

plt.xlabel("Role Group")
plt.ylabel("Average Clearances per 90")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 20 — Average Carries per 90 by Role Group
# ============================================================

player_carries = pd.read_sql_query("""
    SELECT
        player_id,
        COUNT(*) AS carries
    FROM events
    WHERE event_type = 'Carry'
      AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

role_df = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_carries, on="player_id", how="left")
)

role_df["carries"] = role_df["carries"].fillna(0)

role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()

role_df["role_group"] = role_df["primary_position"].apply(assign_role)

role_df["carries_per_90"] = (
    role_df["carries"] / (role_df["total_minutes"] / 90)
)

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_carries_per_90=("carries_per_90", "mean")
    )
    .reset_index()
    .sort_values("avg_carries_per_90", ascending=False)
)

print("\n" + "=" * 60)
print("EDA 20 — Average Carries per 90 by Role Group")
print("=" * 60)
print(role_summary.to_string(index=False))

plt.figure(figsize=(10, 6))
plt.bar(role_summary["role_group"], role_summary["avg_carries_per_90"])
plt.title("Average Carries per 90 by Role Group")
plt.xlabel("Role Group")
plt.ylabel("Average Carries per 90")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()


# ============================================================
# EDA 21 — Average Dribbles per 90 by Role Group
# ============================================================

player_dribbles = pd.read_sql_query("""
    SELECT
        player_id,
        COUNT(*) AS dribbles
    FROM events
    WHERE event_type = 'Dribble'
      AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

role_df = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_dribbles, on="player_id", how="left")
)

role_df["dribbles"] = role_df["dribbles"].fillna(0)

role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()

role_df["role_group"] = role_df["primary_position"].apply(assign_role)

role_df["dribbles_per_90"] = (
    role_df["dribbles"] / (role_df["total_minutes"] / 90)
)

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_dribbles_per_90=("dribbles_per_90", "mean")
    )
    .reset_index()
    .sort_values("avg_dribbles_per_90", ascending=False)
)

print("\n" + "=" * 60)
print("EDA 21 — Average Dribbles per 90 by Role Group")
print("=" * 60)
print(role_summary.to_string(index=False))

plt.figure(figsize=(10, 6))
plt.bar(role_summary["role_group"], role_summary["avg_dribbles_per_90"])
plt.title("Average Dribbles per 90 by Role Group")
plt.xlabel("Role Group")
plt.ylabel("Average Dribbles per 90")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()


# ============================================================
# EDA 22 — Average Successful Dribbles per 90 by Role Group
# ============================================================

player_successful_dribbles = pd.read_sql_query("""
    SELECT
        player_id,
        COUNT(*) AS successful_dribbles
    FROM events
    WHERE event_type = 'Dribble'
      AND dribble_outcome = 'Complete'
      AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

role_df = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_successful_dribbles, on="player_id", how="left")
)

role_df["successful_dribbles"] = (
    role_df["successful_dribbles"].fillna(0)
)

role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()

role_df["role_group"] = role_df["primary_position"].apply(assign_role)

role_df["successful_dribbles_per_90"] = (
    role_df["successful_dribbles"]
    / (role_df["total_minutes"] / 90)
)

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_successful_dribbles_per_90=(
            "successful_dribbles_per_90",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "avg_successful_dribbles_per_90",
        ascending=False
    )
)

print("\n" + "=" * 60)
print("EDA 22 — Average Successful Dribbles per 90 by Role Group")
print("=" * 60)
print(role_summary.to_string(index=False))

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_successful_dribbles_per_90"]
)

plt.title("Average Successful Dribbles per 90 by Role Group")
plt.xlabel("Role Group")
plt.ylabel("Average Successful Dribbles per 90")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

# ============================================================
# EDA 23 — Average Ball Recoveries per 90 by Role Group
# ============================================================

player_recoveries = pd.read_sql_query("""
    SELECT
        player_id,
        COUNT(*) AS ball_recoveries
    FROM events
    WHERE
        event_type = 'Ball Recovery'
        AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

role_df = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_recoveries, on="player_id", how="left")
)

role_df["ball_recoveries"] = (
    role_df["ball_recoveries"].fillna(0)
)

role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()

role_df["role_group"] = (
    role_df["primary_position"].apply(assign_role)
)

role_df["ball_recoveries_per_90"] = (
    role_df["ball_recoveries"]
    / (role_df["total_minutes"] / 90)
)

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_ball_recoveries_per_90=(
            "ball_recoveries_per_90",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "avg_ball_recoveries_per_90",
        ascending=False
    )
)

print("\n" + "=" * 60)
print("EDA 23 — Average Ball Recoveries per 90 by Role Group")
print("=" * 60)

print(role_summary.to_string(index=False))

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_ball_recoveries_per_90"]
)

plt.title(
    "Average Ball Recoveries per 90 by Role Group"
)

plt.xlabel("Role Group")
plt.ylabel("Average Ball Recoveries per 90")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 24 — Average Miscontrols per 90 by Role Group
# ============================================================

player_miscontrols = pd.read_sql_query("""
    SELECT
        player_id,
        COUNT(*) AS miscontrols
    FROM events
    WHERE
        event_type = 'Miscontrol'
        AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

role_df = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_miscontrols, on="player_id", how="left")
)

role_df["miscontrols"] = (
    role_df["miscontrols"].fillna(0)
)

role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()

role_df["role_group"] = (
    role_df["primary_position"].apply(assign_role)
)

role_df["miscontrols_per_90"] = (
    role_df["miscontrols"]
    / (role_df["total_minutes"] / 90)
)

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_miscontrols_per_90=(
            "miscontrols_per_90",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "avg_miscontrols_per_90",
        ascending=False
    )
)

print("\n" + "=" * 60)
print("EDA 24 — Average Miscontrols per 90 by Role Group")
print("=" * 60)

print(role_summary.to_string(index=False))

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_miscontrols_per_90"]
)

plt.title(
    "Average Miscontrols per 90 by Role Group"
)

plt.xlabel("Role Group")
plt.ylabel("Average Miscontrols per 90")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 25 — Average Dispossessed per 90 by Role Group
# ============================================================

player_dispossessed = pd.read_sql_query("""
    SELECT
        player_id,
        COUNT(*) AS dispossessed
    FROM events
    WHERE
        event_type = 'Dispossessed'
        AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

role_df = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_dispossessed, on="player_id", how="left")
)

role_df["dispossessed"] = (
    role_df["dispossessed"].fillna(0)
)

role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()

role_df["role_group"] = (
    role_df["primary_position"].apply(assign_role)
)

role_df["dispossessed_per_90"] = (
    role_df["dispossessed"]
    / (role_df["total_minutes"] / 90)
)

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_dispossessed_per_90=(
            "dispossessed_per_90",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "avg_dispossessed_per_90",
        ascending=False
    )
)

print("\n" + "=" * 60)
print("EDA 25 — Average Dispossessed per 90 by Role Group")
print("=" * 60)

print(role_summary.to_string(index=False))

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_dispossessed_per_90"]
)

plt.title(
    "Average Dispossessed per 90 by Role Group"
)

plt.xlabel("Role Group")
plt.ylabel("Average Dispossessed per 90")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 26 — Average Duels per 90 by Role Group
# ============================================================

player_duels = pd.read_sql_query("""
    SELECT
        player_id,
        COUNT(*) AS duels
    FROM events
    WHERE
        event_type = 'Duel'
        AND duel_type IN ('Tackle', 'Aerial Lost')
        AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

role_df = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_duels, on="player_id", how="left")
)

role_df["duels"] = (
    role_df["duels"].fillna(0)
)

role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()

role_df["role_group"] = (
    role_df["primary_position"].apply(assign_role)
)

role_df["duels_per_90"] = (
    role_df["duels"]
    / (role_df["total_minutes"] / 90)
)

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_duels_per_90=(
            "duels_per_90",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "avg_duels_per_90",
        ascending=False
    )
)

print("\n" + "=" * 60)
print("EDA 26 — Average Duels per 90 by Role Group")
print("=" * 60)

print(role_summary.to_string(index=False))

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_duels_per_90"]
)

plt.title(
    "Average Duels per 90 by Role Group"
)

plt.xlabel("Role Group")
plt.ylabel("Average Duels per 90")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 27 — Average Aerial Duels Lost per 90 by Role Group
# ============================================================

player_aerial_lost = pd.read_sql_query("""
    SELECT
        player_id,
        COUNT(*) AS aerial_duels_lost
    FROM events
    WHERE
        event_type = 'Duel'
        AND duel_type = 'Aerial Lost'
        AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

role_df = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_aerial_lost, on="player_id", how="left")
)

role_df["aerial_duels_lost"] = (
    role_df["aerial_duels_lost"].fillna(0)
)

role_df = role_df[
    role_df["total_minutes"] >= 900
].copy()

role_df["role_group"] = (
    role_df["primary_position"].apply(assign_role)
)

role_df["aerial_duels_lost_per_90"] = (
    role_df["aerial_duels_lost"]
    / (role_df["total_minutes"] / 90)
)

role_summary = (
    role_df
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_aerial_duels_lost_per_90=(
            "aerial_duels_lost_per_90",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "avg_aerial_duels_lost_per_90",
        ascending=False
    )
)

print("\n" + "=" * 60)
print("EDA 27 — Average Aerial Duels Lost per 90 by Role Group")
print("=" * 60)

print(
    role_summary.to_string(index=False)
)

plt.figure(figsize=(10, 6))

plt.bar(
    role_summary["role_group"],
    role_summary["avg_aerial_duels_lost_per_90"]
)

plt.title(
    "Average Aerial Duels Lost per 90 by Role Group"
)

plt.xlabel("Role Group")
plt.ylabel("Average Aerial Duels Lost per 90")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 28 — xG vs Goals by Player
# ============================================================

player_xg_goals = pd.read_sql_query("""
    SELECT
        p.player_id,
        p.player_name,
        SUM(e.shot_xg) AS expected_goals,
        SUM(
            CASE
                WHEN e.shot_outcome = 'Goal' THEN 1
                ELSE 0
            END
        ) AS goals
    FROM events e
    JOIN players p
        ON e.player_id = p.player_id
    WHERE
        e.event_type = 'Shot'
    GROUP BY
        p.player_id,
        p.player_name
""", connection)

player_xg_goals = player_xg_goals.merge(
    player_minutes,
    on="player_id",
    how="left"
)

player_xg_goals = player_xg_goals[
    player_xg_goals["total_minutes"] >= 900
].copy()

player_xg_goals["goals_minus_xg"] = (
    player_xg_goals["goals"]
    - player_xg_goals["expected_goals"]
)

print("\n" + "=" * 60)
print("EDA 28 — xG vs Goals by Player")
print("=" * 60)

print(
    player_xg_goals
    .sort_values("goals_minus_xg", ascending=False)
    [["player_name", "total_minutes",
      "expected_goals", "goals", "goals_minus_xg"]]
    .head(20)
    .to_string(index=False)
)

plt.figure(figsize=(10, 7))

plt.scatter(
    player_xg_goals["expected_goals"],
    player_xg_goals["goals"]
)

max_value = max(
    player_xg_goals["expected_goals"].max(),
    player_xg_goals["goals"].max()
)

plt.plot(
    [0, max_value],
    [0, max_value],
    linestyle="--"
)

plt.title("Player xG vs Actual Goals")
plt.xlabel("Expected Goals (xG)")
plt.ylabel("Actual Goals")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 29 — Key Passes vs Event-Derived Assists
# ============================================================

player_key_assists = pd.read_sql_query("""
    SELECT
        p.player_id,
        p.player_name,

        COUNT(*) AS key_passes,

        SUM(
            CASE
                WHEN shot.shot_outcome = 'Goal'
                THEN 1
                ELSE 0
            END
        ) AS assists

    FROM events shot

    JOIN events pass_event
        ON shot.shot_key_pass_id = pass_event.event_id
       AND pass_event.event_type = 'Pass'

    JOIN players p
        ON pass_event.player_id = p.player_id

    WHERE
        shot.event_type = 'Shot'
        AND shot.shot_key_pass_id IS NOT NULL

    GROUP BY
        p.player_id,
        p.player_name
""", connection)

player_key_assists = player_key_assists.merge(
    player_minutes,
    on="player_id",
    how="left"
)

player_key_assists = player_key_assists[
    player_key_assists["total_minutes"] >= 900
].copy()

print("\n" + "=" * 60)
print("EDA 29 — Key Passes vs Event-Derived Assists")
print("=" * 60)

print(
    player_key_assists
    .sort_values("key_passes", ascending=False)
    [["player_name", "total_minutes",
      "key_passes", "assists"]]
    .head(20)
    .to_string(index=False)
)

plt.figure(figsize=(10, 7))

plt.scatter(
    player_key_assists["key_passes"],
    player_key_assists["assists"]
)

plt.title(
    "Key Passes vs Event-Derived Assists"
)

plt.xlabel("Key Passes")
plt.ylabel("Event-Derived Assists")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 30 — Passing Volume vs Passing Efficiency
# ============================================================

player_passing = pd.read_sql_query("""
    SELECT
        player_id,

        COUNT(*) AS total_passes,

        SUM(
            CASE
                WHEN pass_outcome IS NULL
                     OR pass_outcome = 'Complete'
                THEN 1
                ELSE 0
            END
        ) AS completed_passes

    FROM events

    WHERE
        event_type = 'Pass'

    GROUP BY
        player_id
""", connection)

player_passing = player_passing.merge(
    player_minutes,
    on="player_id",
    how="left"
)

player_passing = player_passing[
    player_passing["total_minutes"] >= 900
].copy()

player_passing["passes_per_90"] = (
    player_passing["total_passes"]
    / (player_passing["total_minutes"] / 90)
)

player_passing["pass_completion_pct"] = (
    player_passing["completed_passes"]
    / player_passing["total_passes"]
    * 100
)

player_passing = player_passing.merge(
    pd.read_sql_query(
        """
        SELECT player_id, player_name
        FROM players
        """,
        connection
    ),
    on="player_id",
    how="left"
)

print("\n" + "=" * 60)
print("EDA 30 — Passing Volume vs Passing Efficiency")
print("=" * 60)

print(
    player_passing
    .sort_values("passes_per_90", ascending=False)
    [["player_name", "total_minutes",
      "passes_per_90", "pass_completion_pct"]]
    .head(20)
    .to_string(index=False)
)

plt.figure(figsize=(10, 7))

plt.scatter(
    player_passing["passes_per_90"],
    player_passing["pass_completion_pct"]
)

plt.title(
    "Passing Volume vs Passing Efficiency"
)

plt.xlabel("Passes per 90")
plt.ylabel("Pass Completion %")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 31 — Pressures vs Tackles
# ============================================================

player_defensive = pd.read_sql_query("""
    SELECT
        player_id,

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
        ) AS tackles

    FROM events

    WHERE
        event_type IN ('Pressure', 'Duel')

    GROUP BY
        player_id
""", connection)

player_defensive = player_defensive.merge(
    player_minutes,
    on="player_id",
    how="left"
)

player_defensive = player_defensive[
    player_defensive["total_minutes"] >= 900
].copy()

player_defensive["pressures_per_90"] = (
    player_defensive["pressures"]
    / (player_defensive["total_minutes"] / 90)
)

player_defensive["tackles_per_90"] = (
    player_defensive["tackles"]
    / (player_defensive["total_minutes"] / 90)
)

player_defensive = player_defensive.merge(
    pd.read_sql_query(
        """
        SELECT player_id, player_name
        FROM players
        """,
        connection
    ),
    on="player_id",
    how="left"
)
print("\n" + "=" * 60)
print("EDA 31 — Pressures vs Tackles")
print("=" * 60)

print(
    player_defensive
    .sort_values("pressures_per_90", ascending=False)
    [["player_name", "total_minutes",
      "pressures_per_90", "tackles_per_90"]]
    .head(20)
    .to_string(index=False)
)

plt.figure(figsize=(10, 7))

plt.scatter(
    player_defensive["pressures_per_90"],
    player_defensive["tackles_per_90"]
)

plt.title(
    "Pressures vs Tackles per 90"
)

plt.xlabel("Pressures per 90")
plt.ylabel("Tackles per 90")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 32 — Carries vs Dribbles
# ============================================================

player_carry_dribble = pd.read_sql_query("""
    SELECT
        player_id,

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
        ) AS dribbles

    FROM events

    WHERE
        event_type IN ('Carry', 'Dribble')

    GROUP BY
        player_id
""", connection)

player_carry_dribble = player_carry_dribble.merge(
    player_minutes,
    on="player_id",
    how="left"
)

player_carry_dribble = player_carry_dribble[
    player_carry_dribble["total_minutes"] >= 900
].copy()

player_carry_dribble["carries_per_90"] = (
    player_carry_dribble["carries"]
    / (player_carry_dribble["total_minutes"] / 90)
)

player_carry_dribble["dribbles_per_90"] = (
    player_carry_dribble["dribbles"]
    / (player_carry_dribble["total_minutes"] / 90)
)

player_carry_dribble = player_carry_dribble.merge(
    pd.read_sql_query(
        """
        SELECT player_id, player_name
        FROM players
        """,
        connection
    ),
    on="player_id",
    how="left"
)

print("\n" + "=" * 60)
print("EDA 32 — Carries vs Dribbles")
print("=" * 60)

print(
    player_carry_dribble
    .sort_values("carries_per_90", ascending=False)
    [["player_name", "total_minutes",
      "carries_per_90", "dribbles_per_90"]]
    .head(20)
    .to_string(index=False)
)

plt.figure(figsize=(10, 7))

plt.scatter(
    player_carry_dribble["carries_per_90"],
    player_carry_dribble["dribbles_per_90"]
)

plt.title(
    "Carries vs Dribbles per 90"
)

plt.xlabel("Carries per 90")
plt.ylabel("Dribbles per 90")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 33 — xG/90 vs Event-Derived Assists/90
# ============================================================

print("\n" + "=" * 60)
print("EDA 33 — xG/90 vs Event-Derived Assists/90")
print("=" * 60)

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

player_xg = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(shot_xg) AS expected_goals
    FROM events
    WHERE
        event_type = 'Shot'
    GROUP BY player_id
""", connection)

player_assists = pd.read_sql_query("""
    SELECT
        pass_event.player_id,
        COUNT(*) AS assists
    FROM events shot
    JOIN events pass_event
        ON shot.shot_key_pass_id = pass_event.event_id
       AND pass_event.event_type = 'Pass'
    WHERE
        shot.event_type = 'Shot'
        AND shot.shot_key_pass_id IS NOT NULL
        AND shot.shot_outcome = 'Goal'
    GROUP BY pass_event.player_id
""", connection)

eda33 = (
    player_minutes
    .merge(player_xg, on="player_id", how="left")
    .merge(player_assists, on="player_id", how="left")
)

eda33["expected_goals"] = eda33["expected_goals"].fillna(0)
eda33["assists"] = eda33["assists"].fillna(0)

eda33 = eda33[eda33["total_minutes"] >= 900].copy()

eda33["xg_per_90"] = (
    eda33["expected_goals"]
    / (eda33["total_minutes"] / 90)
)

eda33["assists_per_90"] = (
    eda33["assists"]
    / (eda33["total_minutes"] / 90)
)

player_names = pd.read_sql_query("""
    SELECT
        player_id,
        player_name
    FROM players
""", connection)

eda33 = eda33.merge(player_names, on="player_id", how="left")

print(
    eda33[
        [
            "player_name",
            "total_minutes",
            "xg_per_90",
            "assists_per_90"
        ]
    ]
    .sort_values("xg_per_90", ascending=False)
    .head(20)
)

plt.figure(figsize=(10, 7))

plt.scatter(
    eda33["xg_per_90"],
    eda33["assists_per_90"],
    alpha=0.7
)

plt.xlabel("xG per 90")
plt.ylabel("Event-Derived Assists per 90")
plt.title("xG/90 vs Event-Derived Assists/90")

plt.grid(alpha=0.2)
plt.tight_layout()
plt.show()

# ============================================================
# EDA 34 — Attacking Output vs Minutes
# ============================================================

print("\n" + "=" * 60)
print("EDA 34 — Attacking Output vs Minutes")
print("=" * 60)

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

player_shots = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(shot_xg) AS expected_goals,
        SUM(
            CASE
                WHEN shot_outcome = 'Goal' THEN 1
                ELSE 0
            END
        ) AS goals
    FROM events
    WHERE
        event_type = 'Shot'
    GROUP BY player_id
""", connection)

eda34 = (
    player_minutes
    .merge(player_shots, on="player_id", how="left")
)

eda34["expected_goals"] = eda34["expected_goals"].fillna(0)
eda34["goals"] = eda34["goals"].fillna(0)

eda34 = eda34[eda34["total_minutes"] >= 900].copy()

eda34["xg_per_90"] = (
    eda34["expected_goals"]
    / (eda34["total_minutes"] / 90)
)

eda34["goals_per_90"] = (
    eda34["goals"]
    / (eda34["total_minutes"] / 90)
)

player_names = pd.read_sql_query("""
    SELECT
        player_id,
        player_name
    FROM players
""", connection)

eda34 = eda34.merge(player_names, on="player_id", how="left")

print(
    eda34[
        [
            "player_name",
            "total_minutes",
            "xg_per_90",
            "goals_per_90"
        ]
    ]
    .sort_values("total_minutes", ascending=False)
    .head(20)
)

plt.figure(figsize=(10, 7))

plt.scatter(
    eda34["total_minutes"],
    eda34["xg_per_90"],
    alpha=0.7
)

plt.xlabel("Total Minutes")
plt.ylabel("xG per 90")
plt.title("Attacking Output vs Playing-Time Exposure")

plt.grid(alpha=0.2)
plt.tight_layout()
plt.show()

# ============================================================
# EDA 35 — Defensive Activity vs Minutes
# ============================================================

print("\n" + "=" * 60)
print("EDA 35 — Defensive Activity vs Minutes")
print("=" * 60)

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

defensive_events = pd.read_sql_query("""
    SELECT
        player_id,

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
        ) AS interceptions

    FROM events

    WHERE event_type IN (
        'Pressure',
        'Duel',
        'Interception'
    )

    GROUP BY player_id
""", connection)

eda35 = (
    player_minutes
    .merge(defensive_events, on="player_id", how="left")
)

for column in ["pressures", "tackles", "interceptions"]:
    eda35[column] = eda35[column].fillna(0)

eda35 = eda35[eda35["total_minutes"] >= 900].copy()

minutes_90 = eda35["total_minutes"] / 90

eda35["pressures_per_90"] = (
    eda35["pressures"] / minutes_90
)

eda35["tackles_per_90"] = (
    eda35["tackles"] / minutes_90
)

eda35["interceptions_per_90"] = (
    eda35["interceptions"] / minutes_90
)

player_names = pd.read_sql_query("""
    SELECT
        player_id,
        player_name
    FROM players
""", connection)

eda35 = eda35.merge(player_names, on="player_id", how="left")

print(
    eda35[
        [
            "player_name",
            "total_minutes",
            "pressures_per_90",
            "tackles_per_90",
            "interceptions_per_90"
        ]
    ]
    .sort_values("total_minutes", ascending=False)
    .head(20)
)

plt.figure(figsize=(10, 7))

plt.scatter(
    eda35["total_minutes"],
    eda35["pressures_per_90"],
    alpha=0.7
)

plt.xlabel("Total Minutes")
plt.ylabel("Pressures per 90")
plt.title("Defensive Activity vs Playing-Time Exposure")

plt.grid(alpha=0.2)
plt.tight_layout()
plt.show()

# ============================================================
# EDA 36 — Role Group Performance Comparison
# ============================================================

print("\n" + "=" * 60)
print("EDA 36 — Role Group Performance Comparison")
print("=" * 60)

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

position_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE position IS NOT NULL
    GROUP BY player_id, position
""", connection)

position_ranked = position_minutes.copy()

position_ranked["rank"] = (
    position_ranked
    .groupby("player_id")["position_minutes"]
    .rank(
        method="first",
        ascending=False
    )
)

primary_positions = (
    position_ranked[
        position_ranked["rank"] == 1
    ][
        ["player_id", "position"]
    ]
    .rename(
        columns={
            "position": "primary_position"
        }
    )
)

# Use the same role mapping as previous EDAs.
primary_positions["role_group"] = (
    primary_positions["primary_position"]
    .apply(assign_role)
)

player_minutes = player_minutes[
    player_minutes["total_minutes"] >= 900
]

player_metrics = pd.read_sql_query("""
    SELECT
        player_id,

        SUM(
            CASE
                WHEN event_type = 'Shot'
                THEN shot_xg
                ELSE 0
            END
        ) AS expected_goals,

        SUM(
            CASE
                WHEN event_type = 'Shot'
                     AND shot_outcome = 'Goal'
                THEN 1
                ELSE 0
            END
        ) AS goals,

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
                WHEN event_type = 'Carry'
                THEN 1
                ELSE 0
            END
        ) AS carries,

        SUM(
            CASE
                WHEN event_type = 'Dribble'
                     AND dribble_outcome = 'Complete'
                THEN 1
                ELSE 0
            END
        ) AS successful_dribbles,

        SUM(
            CASE
                WHEN event_type = 'Pass'
                THEN 1
                ELSE 0
            END
        ) AS passes

    FROM events

    GROUP BY player_id
""", connection)

player_assists = pd.read_sql_query("""
    SELECT
        pass_event.player_id,
        COUNT(*) AS assists
    FROM events shot
    JOIN events pass_event
        ON shot.shot_key_pass_id = pass_event.event_id
       AND pass_event.event_type = 'Pass'
    WHERE
        shot.event_type = 'Shot'
        AND shot.shot_key_pass_id IS NOT NULL
        AND shot.shot_outcome = 'Goal'
    GROUP BY pass_event.player_id
""", connection)

eda36 = (
    player_minutes
    .merge(primary_positions, on="player_id", how="left")
    .merge(player_metrics, on="player_id", how="left")
    .merge(player_assists, on="player_id", how="left")
)

metric_columns = [
    "expected_goals",
    "goals",
    "pressures",
    "tackles",
    "interceptions",
    "carries",
    "successful_dribbles",
    "passes",
    "assists"
]

for column in metric_columns:
    eda36[column] = eda36[column].fillna(0)

minutes_90 = eda36["total_minutes"] / 90

eda36["xg_per_90"] = eda36["expected_goals"] / minutes_90
eda36["assists_per_90"] = eda36["assists"] / minutes_90
eda36["passes_per_90"] = eda36["passes"] / minutes_90
eda36["pressures_per_90"] = eda36["pressures"] / minutes_90
eda36["tackles_per_90"] = eda36["tackles"] / minutes_90
eda36["interceptions_per_90"] = eda36["interceptions"] / minutes_90
eda36["carries_per_90"] = eda36["carries"] / minutes_90
eda36["successful_dribbles_per_90"] = (
    eda36["successful_dribbles"] / minutes_90
)

role_comparison = (
    eda36
    .groupby("role_group")
    .agg(
        players=("player_id", "count"),
        avg_xg_per_90=("xg_per_90", "mean"),
        avg_assists_per_90=("assists_per_90", "mean"),
        avg_passes_per_90=("passes_per_90", "mean"),
        avg_pressures_per_90=("pressures_per_90", "mean"),
        avg_tackles_per_90=("tackles_per_90", "mean"),
        avg_interceptions_per_90=("interceptions_per_90", "mean"),
        avg_carries_per_90=("carries_per_90", "mean"),
        avg_successful_dribbles_per_90=(
            "successful_dribbles_per_90",
            "mean"
        )
    )
    .reset_index()
)

print(role_comparison.to_string(index=False))

# ============================================================
# EDA 37 — Position Share vs Performance
# ============================================================

print("\n" + "=" * 60)
print("EDA 37 — Position Share vs Performance")
print("=" * 60)

# ------------------------------------------------------------
# Player minutes
# ------------------------------------------------------------

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

# ------------------------------------------------------------
# Minutes by position
# ------------------------------------------------------------

position_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE position IS NOT NULL
    GROUP BY
        player_id,
        position
""", connection)

# ------------------------------------------------------------
# Determine primary position
# ------------------------------------------------------------

position_ranked = position_minutes.copy()

position_ranked["rank"] = (
    position_ranked
    .groupby("player_id")["position_minutes"]
    .rank(
        method="first",
        ascending=False
    )
)

primary_positions = (
    position_ranked[
        position_ranked["rank"] == 1
    ][
        [
            "player_id",
            "position",
            "position_minutes"
        ]
    ]
    .rename(
        columns={
            "position": "primary_position"
        }
    )
)

# ------------------------------------------------------------
# Calculate position share
# ------------------------------------------------------------

position_share = (
    primary_positions
    .merge(
        player_minutes,
        on="player_id",
        how="left"
    )
)

position_share["position_share_pct"] = (
    position_share["position_minutes"]
    / position_share["total_minutes"]
    * 100
)

# ------------------------------------------------------------
# Player xG
# ------------------------------------------------------------

player_xg = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(shot_xg) AS expected_goals
    FROM events
    WHERE
        event_type = 'Shot'
        AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

# ------------------------------------------------------------
# Combine
# ------------------------------------------------------------

eda37 = (
    position_share
    .merge(
        player_xg,
        on="player_id",
        how="left"
    )
)

eda37["expected_goals"] = (
    eda37["expected_goals"]
    .fillna(0)
)

# ------------------------------------------------------------
# Keep scouting population
# ------------------------------------------------------------

eda37 = eda37[
    eda37["total_minutes"] >= 900
].copy()

# ------------------------------------------------------------
# Calculate xG per 90
# ------------------------------------------------------------

eda37["xg_per_90"] = (
    eda37["expected_goals"]
    / (eda37["total_minutes"] / 90)
)

# ------------------------------------------------------------
# Add player names
# ------------------------------------------------------------

player_names = pd.read_sql_query("""
    SELECT
        player_id,
        player_name
    FROM players
""", connection)

eda37 = eda37.merge(
    player_names,
    on="player_id",
    how="left"
)

# ------------------------------------------------------------
# Output
# ------------------------------------------------------------

print(
    eda37[
        [
            "player_name",
            "total_minutes",
            "primary_position",
            "position_share_pct",
            "xg_per_90"
        ]
    ]
    .sort_values(
        "position_share_pct",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)

# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------

plt.figure(figsize=(10, 7))

plt.scatter(
    eda37["position_share_pct"],
    eda37["xg_per_90"],
    alpha=0.7
)

plt.xlabel(
    "Primary Position Share (%)"
)

plt.ylabel(
    "xG per 90"
)

plt.title(
    "Primary Position Share vs xG per 90"
)

plt.grid(alpha=0.2)

plt.tight_layout()
plt.show()

# ============================================================
# EDA 38 — Player Exposure vs Performance
# ============================================================

print("\n" + "=" * 60)
print("EDA 38 — Player Exposure vs Performance")
print("=" * 60)

# ------------------------------------------------------------
# Player minutes
# ------------------------------------------------------------

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

# ------------------------------------------------------------
# Player attacking output
# ------------------------------------------------------------

player_attacking = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(shot_xg) AS expected_goals,
        SUM(
            CASE
                WHEN shot_outcome = 'Goal' THEN 1
                ELSE 0
            END
        ) AS goals
    FROM events
    WHERE
        event_type = 'Shot'
        AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

# ------------------------------------------------------------
# Combine
# ------------------------------------------------------------

eda38 = (
    player_minutes
    .merge(
        player_attacking,
        on="player_id",
        how="left"
    )
)

eda38["expected_goals"] = (
    eda38["expected_goals"]
    .fillna(0)
)

eda38["goals"] = (
    eda38["goals"]
    .fillna(0)
)

# ------------------------------------------------------------
# Scouting population
# ------------------------------------------------------------

eda38 = eda38[
    eda38["total_minutes"] >= 900
].copy()

# ------------------------------------------------------------
# Per-90 metrics
# ------------------------------------------------------------

eda38["xg_per_90"] = (
    eda38["expected_goals"]
    / (eda38["total_minutes"] / 90)
)

eda38["goals_per_90"] = (
    eda38["goals"]
    / (eda38["total_minutes"] / 90)
)

# ------------------------------------------------------------
# Player names
# ------------------------------------------------------------

player_names = pd.read_sql_query("""
    SELECT
        player_id,
        player_name
    FROM players
""", connection)

eda38 = eda38.merge(
    player_names,
    on="player_id",
    how="left"
)

# ------------------------------------------------------------
# Output
# ------------------------------------------------------------

print(
    eda38[
        [
            "player_name",
            "total_minutes",
            "xg_per_90",
            "goals_per_90"
        ]
    ]
    .sort_values(
        "total_minutes",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)

# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------

plt.figure(figsize=(10, 7))

plt.scatter(
    eda38["total_minutes"],
    eda38["xg_per_90"],
    alpha=0.7
)

plt.xlabel("Total Minutes")
plt.ylabel("xG per 90")
plt.title("Player Exposure vs xG per 90")
plt.grid(alpha=0.2)

plt.tight_layout()
plt.show()

# ============================================================
# EDA 39 — Scouting Population by Role
# ============================================================

print("\n" + "=" * 60)
print("EDA 39 — Scouting Population by Role")
print("=" * 60)

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

position_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE position IS NOT NULL
    GROUP BY player_id, position
""", connection)

position_minutes["rank"] = (
    position_minutes
    .groupby("player_id")["position_minutes"]
    .rank(
        method="first",
        ascending=False
    )
)

primary_positions = (
    position_minutes[
        position_minutes["rank"] == 1
    ][
        ["player_id", "position"]
    ]
    .rename(
        columns={"position": "primary_position"}
    )
)

def assign_role(position):
    if position in [
        "Left Center Back",
        "Right Center Back",
        "Center Back"
    ]:
        return "Centre Back"

    elif position in [
        "Left Back",
        "Right Back"
    ]:
        return "Full Back"

    elif position in [
        "Left Defensive Midfield",
        "Right Defensive Midfield",
        "Center Defensive Midfield"
    ]:
        return "Defensive Midfielder"

    elif position in [
        "Left Center Midfield",
        "Right Center Midfield",
        "Center Midfield"
    ]:
        return "Central Midfielder"

    elif position in [
        "Left Center Attacking Midfield",
        "Right Center Attacking Midfield",
        "Center Attacking Midfield"
    ]:
        return "Attacking Midfielder"

    elif position in [
        "Left Wing",
        "Right Wing"
    ]:
        return "Winger"

    elif position in [
        "Left Center Forward",
        "Right Center Forward",
        "Center Forward"
    ]:
        return "Forward"

    elif position == "Goalkeeper":
        return "Goalkeeper"

    return "Other"

scouting_population = (
    player_minutes
    .merge(
        primary_positions,
        on="player_id",
        how="left"
    )
)

scouting_population["role_group"] = (
    scouting_population["primary_position"]
    .apply(assign_role)
)

print("\nPositions currently classified as Other:")

other_positions = (
    scouting_population.loc[
        scouting_population["role_group"] == "Other",
        "primary_position"
    ]
    .value_counts()
    .sort_index()
)

print(other_positions.to_string())

scouting_population = scouting_population[
    scouting_population["total_minutes"] >= 900
].copy()

role_counts = (
    scouting_population
    .groupby("role_group")
    .agg(
        players=("player_id", "nunique")
    )
    .reset_index()
    .sort_values(
        "players",
        ascending=False
    )
)

print(role_counts.to_string(index=False))

plt.figure(figsize=(10, 6))

plt.bar(
    role_counts["role_group"],
    role_counts["players"]
)

plt.xlabel("Role Group")
plt.ylabel("Number of Players")
plt.title("Scouting Population by Role Group")

plt.xticks(
    rotation=30,
    ha="right"
)

plt.tight_layout()
plt.show()

# ============================================================
# EDA 40 — Role-Specific Metric Distributions
# ============================================================

print("\n" + "=" * 60)
print("EDA 40 — Role-Specific Metric Distributions")
print("=" * 60)

# ------------------------------------------------------------
# Player minutes
# ------------------------------------------------------------

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

# ------------------------------------------------------------
# Position minutes
# ------------------------------------------------------------

position_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE position IS NOT NULL
    GROUP BY player_id, position
""", connection)

position_minutes["rank"] = (
    position_minutes
    .groupby("player_id")["position_minutes"]
    .rank(
        method="first",
        ascending=False
    )
)

primary_positions = (
    position_minutes[
        position_minutes["rank"] == 1
    ][
        ["player_id", "position"]
    ]
    .rename(
        columns={"position": "primary_position"}
    )
)

# ------------------------------------------------------------
# Role mapping
# ------------------------------------------------------------

def assign_role(position):
    if position in [
        "Left Center Back",
        "Right Center Back",
        "Center Back"
    ]:
        return "Centre Back"

    elif position in [
        "Left Back",
        "Right Back"
    ]:
        return "Full Back"

    elif position in [
        "Left Defensive Midfield",
        "Right Defensive Midfield",
        "Center Defensive Midfield"
    ]:
        return "Defensive Midfielder"

    elif position in [
        "Left Center Midfield",
        "Right Center Midfield",
        "Center Midfield",
        "Left Midfield",
        "Right Midfield"
    ]:
        return "Central Midfielder"

    elif position in [
        "Left Center Attacking Midfield",
        "Right Center Attacking Midfield",
        "Center Attacking Midfield"
    ]:
        return "Attacking Midfielder"

    elif position in [
        "Left Wing",
        "Right Wing"
    ]:
        return "Winger"

    elif position in [
        "Left Center Forward",
        "Right Center Forward",
        "Center Forward"
    ]:
        return "Forward"

    elif position == "Goalkeeper":
        return "Goalkeeper"

    return "Other"

player_roles = (
    player_minutes
    .merge(
        primary_positions,
        on="player_id",
        how="left"
    )
)

player_roles["role_group"] = (
    player_roles["primary_position"]
    .apply(assign_role)
)

player_roles = player_roles[
    player_roles["total_minutes"] >= 900
].copy()

# ------------------------------------------------------------
# Player xG
# ------------------------------------------------------------

player_xg = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(shot_xg) AS expected_goals
    FROM events
    WHERE
        event_type = 'Shot'
        AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

eda40 = player_roles.merge(
    player_xg,
    on="player_id",
    how="left"
)

eda40["expected_goals"] = (
    eda40["expected_goals"]
    .fillna(0)
)

eda40["xg_per_90"] = (
    eda40["expected_goals"]
    / (eda40["total_minutes"] / 90)
)

# ------------------------------------------------------------
# Summary statistics by role
# ------------------------------------------------------------

role_distribution = (
    eda40
    .groupby("role_group")["xg_per_90"]
    .agg(
        players="count",
        mean="mean",
        median="median",
        minimum="min",
        maximum="max",
        std="std"
    )
    .reset_index()
    .sort_values(
        "mean",
        ascending=False
    )
)

print(
    role_distribution.to_string(
        index=False
    )
)

# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------

role_order = (
    role_distribution
    .sort_values("mean")["role_group"]
    .tolist()
)

data = [
    eda40.loc[
        eda40["role_group"] == role,
        "xg_per_90"
    ]
    for role in role_order
]

plt.figure(figsize=(11, 7))

plt.boxplot(
    data,
    tick_labels=role_order,
    showfliers=False
)

plt.xlabel("Role Group")
plt.ylabel("xG per 90")
plt.title("xG per 90 Distribution by Role Group")

plt.xticks(
    rotation=30,
    ha="right"
)

plt.tight_layout()
plt.show()

# ============================================================
# EDA 41 — Role-Specific Percentile Distributions
# ============================================================

print("\n" + "=" * 60)
print("EDA 41 — Role-Specific Percentile Distributions")
print("=" * 60)

# ------------------------------------------------------------
# Player minutes
# ------------------------------------------------------------

player_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
""", connection)

# ------------------------------------------------------------
# Position minutes
# ------------------------------------------------------------

position_minutes = pd.read_sql_query("""
    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE position IS NOT NULL
    GROUP BY player_id, position
""", connection)

position_minutes["rank"] = (
    position_minutes
    .groupby("player_id")["position_minutes"]
    .rank(
        method="first",
        ascending=False
    )
)

primary_positions = (
    position_minutes[
        position_minutes["rank"] == 1
    ][
        ["player_id", "position"]
    ]
    .rename(
        columns={"position": "primary_position"}
    )
)

# ------------------------------------------------------------
# Role mapping
# ------------------------------------------------------------

def assign_role(position):
    if position in [
        "Left Center Back",
        "Right Center Back",
        "Center Back"
    ]:
        return "Centre Back"

    elif position in [
        "Left Back",
        "Right Back"
    ]:
        return "Full Back"

    elif position in [
        "Left Defensive Midfield",
        "Right Defensive Midfield",
        "Center Defensive Midfield"
    ]:
        return "Defensive Midfielder"

    elif position in [
        "Left Center Midfield",
        "Right Center Midfield",
        "Center Midfield",
        "Left Midfield",
        "Right Midfield"
    ]:
        return "Central Midfielder"

    elif position in [
        "Left Center Attacking Midfield",
        "Right Center Attacking Midfield",
        "Center Attacking Midfield"
    ]:
        return "Attacking Midfielder"

    elif position in [
        "Left Wing",
        "Right Wing"
    ]:
        return "Winger"

    elif position in [
        "Left Center Forward",
        "Right Center Forward",
        "Center Forward"
    ]:
        return "Forward"

    elif position == "Goalkeeper":
        return "Goalkeeper"

    return "Other"

player_roles = (
    player_minutes
    .merge(
        primary_positions,
        on="player_id",
        how="left"
    )
)

player_roles["role_group"] = (
    player_roles["primary_position"]
    .apply(assign_role)
)

player_roles = player_roles[
    player_roles["total_minutes"] >= 900
].copy()

# ------------------------------------------------------------
# Player xG
# ------------------------------------------------------------

player_xg = pd.read_sql_query("""
    SELECT
        player_id,
        SUM(shot_xg) AS expected_goals
    FROM events
    WHERE
        event_type = 'Shot'
        AND player_id IS NOT NULL
    GROUP BY player_id
""", connection)

eda41 = player_roles.merge(
    player_xg,
    on="player_id",
    how="left"
)

eda41["expected_goals"] = (
    eda41["expected_goals"]
    .fillna(0)
)

eda41["xg_per_90"] = (
    eda41["expected_goals"]
    / (eda41["total_minutes"] / 90)
)

# ------------------------------------------------------------
# Within-role percentile
# ------------------------------------------------------------

eda41["xg_percentile"] = (
    eda41
    .groupby("role_group")["xg_per_90"]
    .rank(
        method="min",
        pct=True
    ) * 100
)

# ------------------------------------------------------------
# Percentile distribution
# ------------------------------------------------------------

percentile_distribution = (
    eda41
    .groupby("role_group")["xg_percentile"]
    .agg(
        players="count",
        mean="mean",
        median="median",
        minimum="min",
        maximum="max"
    )
    .reset_index()
    .sort_values(
        "mean",
        ascending=False
    )
)

print(
    percentile_distribution.to_string(
        index=False
    )
)

# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------

role_order = (
    percentile_distribution
    .sort_values("mean")["role_group"]
    .tolist()
)

data = [
    eda41.loc[
        eda41["role_group"] == role,
        "xg_percentile"
    ]
    for role in role_order
]

plt.figure(figsize=(11, 7))

plt.boxplot(
    data,
    tick_labels=role_order,
    showfliers=False
)

plt.xlabel("Role Group")
plt.ylabel("xG/90 Percentile")
plt.title("Within-Role xG/90 Percentile Distribution")

plt.xticks(
    rotation=30,
    ha="right"
)

plt.tight_layout()
plt.show()

# ============================================================
# EDA 42 — Scouting Score Distribution
# ============================================================

print("\n" + "=" * 60)
print("EDA 42 — Scouting Score Distribution")
print("=" * 60)

# ------------------------------------------------------------
# Load Query 49 role-aware profiles
# ------------------------------------------------------------

query49 = """
WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
),

position_minutes AS (
    SELECT
        player_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE position IS NOT NULL
    GROUP BY player_id, position
),

position_ranked AS (
    SELECT
        player_id,
        position,
        position_minutes,
        ROW_NUMBER() OVER (
            PARTITION BY player_id
            ORDER BY position_minutes DESC
        ) AS rn
    FROM position_minutes
),

player_roles AS (
    SELECT
        pm.player_id,
        pm.total_minutes,
        pr.position AS primary_position,
        pr.position_minutes * 100.0
            / pm.total_minutes AS position_share_pct
    FROM player_minutes pm
    JOIN position_ranked pr
        ON pm.player_id = pr.player_id
       AND pr.rn = 1
    WHERE pm.total_minutes >= 900
),

role_classified AS (
    SELECT
        *,
        CASE
            WHEN primary_position IN (
                'Left Center Back',
                'Right Center Back',
                'Center Back'
            ) THEN 'Centre Back'

            WHEN primary_position IN (
                'Left Back',
                'Right Back'
            ) THEN 'Full Back'

            WHEN primary_position IN (
                'Left Defensive Midfield',
                'Right Defensive Midfield',
                'Center Defensive Midfield'
            ) THEN 'Defensive Midfielder'

            WHEN primary_position IN (
                'Left Center Midfield',
                'Right Center Midfield',
                'Center Midfield',
                'Left Midfield',
                'Right Midfield'
            ) THEN 'Central Midfielder'

            WHEN primary_position IN (
                'Left Center Attacking Midfield',
                'Right Center Attacking Midfield',
                'Center Attacking Midfield'
            ) THEN 'Attacking Midfielder'

            WHEN primary_position IN (
                'Left Wing',
                'Right Wing'
            ) THEN 'Winger'

            WHEN primary_position IN (
                'Left Center Forward',
                'Right Center Forward',
                'Center Forward'
            ) THEN 'Forward'

            WHEN primary_position = 'Goalkeeper'
                THEN 'Goalkeeper'

            ELSE 'Other'
        END AS role_group
    FROM player_roles
),

player_metrics AS (
    SELECT
        player_id,

        SUM(
            CASE
                WHEN event_type = 'Shot'
                THEN shot_xg
                ELSE 0
            END
        ) AS xg,

        SUM(
            CASE
                WHEN event_type = 'Shot'
                     AND shot_outcome = 'Goal'
                THEN 1
                ELSE 0
            END
        ) AS goals,

        SUM(
            CASE
                WHEN event_type = 'Pass'
                THEN 1
                ELSE 0
            END
        ) AS passes,

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
                WHEN event_type = 'Carry'
                THEN 1
                ELSE 0
            END
        ) AS carries,

        SUM(
            CASE
                WHEN event_type = 'Dribble'
                     AND dribble_outcome = 'Complete'
                THEN 1
                ELSE 0
            END
        ) AS successful_dribbles,

        SUM(
            CASE
                WHEN event_type = 'Ball Recovery'
                THEN 1
                ELSE 0
            END
        ) AS ball_recoveries,

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
                WHEN event_type = 'Duel'
                THEN 1
                ELSE 0
            END
        ) AS duels,

        SUM(
            CASE
                WHEN event_type = 'Duel'
                     AND duel_type = 'Aerial Lost'
                THEN 1
                ELSE 0
            END
        ) AS aerial_duels_lost

    FROM events
    WHERE player_id IS NOT NULL
    GROUP BY player_id
),

player_assists AS (
    SELECT
        pass_event.player_id,
        COUNT(*) AS assists
    FROM events shot
    JOIN events pass_event
        ON shot.shot_key_pass_id = pass_event.event_id
       AND pass_event.event_type = 'Pass'
    WHERE
        shot.event_type = 'Shot'
        AND shot.shot_key_pass_id IS NOT NULL
        AND shot.shot_outcome = 'Goal'
    GROUP BY pass_event.player_id
),

base AS (
    SELECT
        rc.*,

        COALESCE(pm.xg, 0) AS xg,
        COALESCE(pm.goals, 0) AS goals,
        COALESCE(pm.passes, 0) AS passes,
        COALESCE(pm.pressures, 0) AS pressures,
        COALESCE(pm.tackles, 0) AS tackles,
        COALESCE(pm.interceptions, 0) AS interceptions,
        COALESCE(pm.carries, 0) AS carries,
        COALESCE(pm.successful_dribbles, 0)
            AS successful_dribbles,
        COALESCE(pm.ball_recoveries, 0)
            AS ball_recoveries,
        COALESCE(pm.miscontrols, 0)
            AS miscontrols,
        COALESCE(pm.dispossessed, 0)
            AS dispossessed,
        COALESCE(pm.duels, 0) AS duels,
        COALESCE(pm.aerial_duels_lost, 0)
            AS aerial_duels_lost,
        COALESCE(pa.assists, 0) AS assists

    FROM role_classified rc

    LEFT JOIN player_metrics pm
        ON rc.player_id = pm.player_id

    LEFT JOIN player_assists pa
        ON rc.player_id = pa.player_id
),

rates AS (
    SELECT
        *,
        xg / (total_minutes / 90.0) AS xg_per_90,
        goals / (total_minutes / 90.0) AS goals_per_90,
        passes / (total_minutes / 90.0) AS passes_per_90,
        pressures / (total_minutes / 90.0)
            AS pressures_per_90,
        tackles / (total_minutes / 90.0)
            AS tackles_per_90,
        interceptions / (total_minutes / 90.0)
            AS interceptions_per_90,
        carries / (total_minutes / 90.0)
            AS carries_per_90,
        successful_dribbles / (total_minutes / 90.0)
            AS successful_dribbles_per_90,
        ball_recoveries / (total_minutes / 90.0)
            AS ball_recoveries_per_90,
        miscontrols / (total_minutes / 90.0)
            AS miscontrols_per_90,
        dispossessed / (total_minutes / 90.0)
            AS dispossessed_per_90,
        duels / (total_minutes / 90.0)
            AS duels_per_90,
        aerial_duels_lost / (total_minutes / 90.0)
            AS aerial_duels_lost_per_90,
        assists / (total_minutes / 90.0)
            AS assists_per_90
    FROM base
),

percentiles AS (
    SELECT
        *,
        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY xg_per_90
        ) * 100 AS xg_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY goals_per_90
        ) * 100 AS goals_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY passes_per_90
        ) * 100 AS passes_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY pressures_per_90
        ) * 100 AS pressures_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY tackles_per_90
        ) * 100 AS tackles_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY interceptions_per_90
        ) * 100 AS interceptions_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY carries_per_90
        ) * 100 AS carries_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY successful_dribbles_per_90
        ) * 100 AS successful_dribbles_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY ball_recoveries_per_90
        ) * 100 AS ball_recoveries_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY miscontrols_per_90
        ) * 100 AS miscontrols_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY dispossessed_per_90
        ) * 100 AS dispossessed_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY duels_per_90
        ) * 100 AS duels_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY aerial_duels_lost_per_90 DESC
        ) * 100 AS aerial_duels_lost_pct,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY assists_per_90
        ) * 100 AS assists_pct
    FROM rates
),

profiles AS (
    SELECT
        *,
        (
            xg_pct + goals_pct
        ) / 2.0 AS shooting_profile,

        (
            assists_pct
        ) AS chance_creation_profile,

        (
            passes_pct
        ) AS passing_profile,

        (
            pressures_pct
            + tackles_pct
            + interceptions_pct
        ) / 3.0 AS defensive_profile,

        (
            carries_pct
            + successful_dribbles_pct
        ) / 2.0 AS carrying_profile,

        duels_pct AS duel_profile,

        (
            100 - miscontrols_pct
            + 100 - dispossessed_pct
            + ball_recoveries_pct
        ) / 3.0 AS retention_recovery_profile

    FROM percentiles
)

SELECT
    player_id,
    role_group,
    total_minutes,
    primary_position,
    position_share_pct,
    shooting_profile,
    chance_creation_profile,
    passing_profile,
    defensive_profile,
    carrying_profile,
    duel_profile,
    retention_recovery_profile
FROM profiles
"""

profiles = pd.read_sql_query(
    query49,
    connection
)

# ------------------------------------------------------------
# Role-specific weights
# ------------------------------------------------------------

weights = {
    "Goalkeeper": {
        "passing_profile": 0.50,
        "retention_recovery_profile": 0.30,
        "defensive_profile": 0.20
    },

    "Centre Back": {
        "defensive_profile": 0.40,
        "passing_profile": 0.25,
        "duel_profile": 0.20,
        "carrying_profile": 0.10,
        "retention_recovery_profile": 0.05
    },

    "Full Back": {
        "defensive_profile": 0.30,
        "passing_profile": 0.25,
        "carrying_profile": 0.25,
        "chance_creation_profile": 0.10,
        "retention_recovery_profile": 0.10
    },

    "Defensive Midfielder": {
        "defensive_profile": 0.30,
        "passing_profile": 0.30,
        "retention_recovery_profile": 0.20,
        "carrying_profile": 0.15,
        "chance_creation_profile": 0.05
    },

    "Central Midfielder": {
        "passing_profile": 0.30,
        "defensive_profile": 0.20,
        "chance_creation_profile": 0.20,
        "carrying_profile": 0.20,
        "retention_recovery_profile": 0.10
    },

    "Attacking Midfielder": {
        "chance_creation_profile": 0.35,
        "shooting_profile": 0.25,
        "passing_profile": 0.20,
        "carrying_profile": 0.15,
        "retention_recovery_profile": 0.05
    },

    "Winger": {
        "chance_creation_profile": 0.30,
        "shooting_profile": 0.30,
        "carrying_profile": 0.25,
        "passing_profile": 0.10,
        "retention_recovery_profile": 0.05
    },

    "Forward": {
        "shooting_profile": 0.40,
        "chance_creation_profile": 0.20,
        "duel_profile": 0.15,
        "carrying_profile": 0.10,
        "retention_recovery_profile": 0.15
    }
}

def calculate_score(row):
    role_weights = weights[row["role_group"]]

    score = 0

    for metric, weight in role_weights.items():
        score += row[metric] * weight

    return score

profiles["scouting_score"] = (
    profiles.apply(
        calculate_score,
        axis=1
    )
)

# ------------------------------------------------------------
# Player names
# ------------------------------------------------------------

player_names = pd.read_sql_query("""
    SELECT
        player_id,
        player_name
    FROM players
""", connection)

eda42 = profiles.merge(
    player_names,
    on="player_id",
    how="left"
)

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print(
    eda42[
        ["scouting_score"]
    ]
    .describe()
    .to_string()
)

print("\nTop 20 scouting scores:")

print(
    eda42[
        [
            "player_name",
            "role_group",
            "scouting_score"
        ]
    ]
    .sort_values(
        "scouting_score",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)

# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.hist(
    eda42["scouting_score"],
    bins=20
)

plt.xlabel("Role-Aware Scouting Score")
plt.ylabel("Number of Players")
plt.title("Distribution of Role-Aware Scouting Scores")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 43 — Top Players by Role
# ============================================================

print("\n" + "=" * 60)
print("EDA 43 — Top Players by Role")
print("=" * 60)

# ------------------------------------------------------------
# Reuse EDA 42 result
# ------------------------------------------------------------

# eda42 contains:
# player_id
# player_name
# role_group
# scouting_score

top_players_by_role = (
    eda42[
        [
            "player_id",
            "player_name",
            "role_group",
            "scouting_score",
            "total_minutes",
            "primary_position",
            "position_share_pct"
        ]
    ]
    .sort_values(
        [
            "role_group",
            "scouting_score"
        ],
        ascending=[
            True,
            False
        ]
    )
    .groupby(
        "role_group",
        as_index=False
    )
    .head(5)
)

# ------------------------------------------------------------
# Rank within role
# ------------------------------------------------------------

top_players_by_role["role_rank"] = (
    top_players_by_role
    .groupby("role_group")["scouting_score"]
    .rank(
        method="first",
        ascending=False
    )
    .astype(int)
)

top_players_by_role = (
    top_players_by_role
    .sort_values(
        [
            "role_group",
            "role_rank"
        ]
    )
)

print(
    top_players_by_role[
        [
            "role_group",
            "role_rank",
            "player_name",
            "scouting_score",
            "total_minutes",
            "primary_position",
            "position_share_pct"
        ]
    ]
    .to_string(index=False)
)

# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------

plt.figure(figsize=(12, 8))

role_labels = (
    top_players_by_role["role_group"]
    + " — "
    + top_players_by_role["player_name"]
)

plt.barh(
    role_labels,
    top_players_by_role["scouting_score"]
)

plt.xlabel("Role-Aware Scouting Score")
plt.ylabel("Player / Role")
plt.title("Top 5 Players by Analytical Role")

plt.tight_layout()
plt.show()

# ============================================================
# EDA 44 — Scouting Score vs Minutes
# ============================================================

print("\n" + "=" * 60)
print("EDA 44 — Scouting Score vs Minutes")
print("=" * 60)

eda44 = eda42[
    [
        "player_id",
        "player_name",
        "role_group",
        "scouting_score",
        "total_minutes"
    ]
].copy()

print("\nTop 20 players by scouting score:")
print(
    eda44
    .sort_values(
        "scouting_score",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)

print("\nScouting score statistics:")
print(
    eda44["scouting_score"]
    .describe()
    .to_string()
)

plt.figure(figsize=(10, 7))

for role in sorted(eda44["role_group"].unique()):

    role_data = eda44[
        eda44["role_group"] == role
    ]

    plt.scatter(
        role_data["total_minutes"],
        role_data["scouting_score"],
        label=role,
        alpha=0.7
    )

plt.xlabel("Total Minutes")
plt.ylabel("Scouting Score")
plt.title("Scouting Score vs Player Exposure")
plt.legend()

plt.tight_layout()
plt.show()


# ============================================================
# EDA 45 — Position Reliability vs Scouting Score
# ============================================================

print("\n" + "=" * 60)
print("EDA 45 — Position Reliability vs Scouting Score")
print("=" * 60)

eda45 = eda42[
    [
        "player_id",
        "player_name",
        "role_group",
        "scouting_score",
        "position_share_pct",
        "primary_position"
    ]
].copy()

print("\nTop 20 players by scouting score:")
print(
    eda45
    .sort_values(
        "scouting_score",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)

print("\nPosition share statistics:")
print(
    eda45["position_share_pct"]
    .describe()
    .to_string()
)

plt.figure(figsize=(10, 7))

for role in sorted(eda45["role_group"].unique()):

    role_data = eda45[
        eda45["role_group"] == role
    ]

    plt.scatter(
        role_data["position_share_pct"],
        role_data["scouting_score"],
        label=role,
        alpha=0.7
    )

plt.xlabel("Primary Position Share (%)")
plt.ylabel("Scouting Score")
plt.title("Position Reliability vs Scouting Score")
plt.legend()

plt.tight_layout()
plt.show()


# ============================================================
# EDA 46 — Player Scouting Profiles
# ============================================================

print("\n" + "=" * 60)
print("EDA 46 — Player Scouting Profiles")
print("=" * 60)

profile_columns = [
    "shooting_profile",
    "chance_creation_profile",
    "passing_profile",
    "defensive_profile",
    "carrying_profile",
    "duel_profile",
    "retention_recovery_profile"
]

profile_labels = [
    "Shooting",
    "Chance Creation",
    "Passing",
    "Defensive",
    "Carrying",
    "Duels",
    "Retention/Recovery"
]

print("\nTop 10 player scouting profiles:")

top_profiles = (
    eda42
    .sort_values(
        "scouting_score",
        ascending=False
    )
    [
        [
            "player_name",
            "role_group",
            "scouting_score"
        ] + profile_columns
    ]
    .head(10)
)

print(
    top_profiles.to_string(index=False)
)

# Average profile across the scouting population
profile_means = eda42[
    profile_columns
].mean()

plt.figure(figsize=(11, 7))

plt.bar(
    profile_labels,
    profile_means.values
)

plt.xlabel("Scouting Profile")
plt.ylabel("Average Percentile Score")
plt.title("Average Player Scouting Profile Across All Roles")

plt.xticks(
    rotation=30
)

plt.tight_layout()
plt.show()


# ============================================================
# EDA 47 — Role-Specific Player Comparisons
# ============================================================

print("\n" + "=" * 60)
print("EDA 47 — Role-Specific Player Comparisons")
print("=" * 60)

top_by_role = (
    eda42
    .sort_values(
        [
            "role_group",
            "scouting_score"
        ],
        ascending=[
            True,
            False
        ]
    )
    .groupby(
        "role_group",
        as_index=False
    )
    .head(3)
)

print("\nTop 3 players by role:")

print(
    top_by_role[
        [
            "role_group",
            "player_name",
            "scouting_score",
            "total_minutes",
            "primary_position",
            "position_share_pct"
        ]
    ]
    .to_string(index=False)
)


# Visualize top 3 players from each role
role_comparison = (
    top_by_role
    .sort_values(
        "scouting_score",
        ascending=True
    )
)

plt.figure(figsize=(14, 9))

labels = (
    role_comparison["role_group"]
    + " — "
    + role_comparison["player_name"]
)

plt.barh(
    labels,
    role_comparison["scouting_score"]
)

plt.xlabel("Scouting Score")
plt.ylabel("Player / Role")
plt.title("Top 3 Players by Analytical Role")

plt.tight_layout()
plt.show()


# ============================================================
# EDA 48 — Scouting Feature Correlation Analysis
# ============================================================

print("\n" + "=" * 60)
print("EDA 48 — Scouting Feature Correlation Analysis")
print("=" * 60)

correlation_features = [
    "shooting_profile",
    "chance_creation_profile",
    "passing_profile",
    "defensive_profile",
    "carrying_profile",
    "duel_profile",
    "retention_recovery_profile",
    "scouting_score"
]

correlation_matrix = (
    eda42[
        correlation_features
    ]
    .corr()
)

print("\nCorrelation matrix:")

print(
    correlation_matrix
    .round(3)
    .to_string()
)

plt.figure(figsize=(11, 9))

plt.imshow(
    correlation_matrix,
    aspect="auto"
)

plt.colorbar(
    label="Correlation"
)

plt.xticks(
    range(len(correlation_features)),
    [
        "Shooting",
        "Chance Creation",
        "Passing",
        "Defensive",
        "Carrying",
        "Duels",
        "Retention/Recovery",
        "Scouting Score"
    ],
    rotation=45,
    ha="right"
)

plt.yticks(
    range(len(correlation_features)),
    [
        "Shooting",
        "Chance Creation",
        "Passing",
        "Defensive",
        "Carrying",
        "Duels",
        "Retention/Recovery",
        "Scouting Score"
    ]
)

plt.title(
    "Correlation Between Scouting Profile Dimensions"
)

plt.tight_layout()
plt.show()


print("\nEDA 44–48 execution complete.")

# ============================================================
# FINAL ANALYTICAL QC
# ============================================================


# ============================================================
# QC 49 — Minutes Distribution
# ============================================================

print("\n" + "=" * 60)
print("QC 49 — Minutes Distribution")
print("=" * 60)

qc_minutes = eda42[
    [
        "player_id",
        "player_name",
        "total_minutes"
    ]
].copy()

print("\nScouting population:")
print("Players:", len(qc_minutes))

print("\nMinutes statistics:")
print(
    qc_minutes["total_minutes"]
    .describe()
    .round(2)
    .to_string()
)

print("\nPlayers by exposure band:")

print(
    pd.cut(
        qc_minutes["total_minutes"],
        bins=[900, 1800, 2700, 3600, float("inf")],
        labels=[
            "900–1799",
            "1800–2699",
            "2700–3599",
            "3600+"
        ],
        right=False
    )
    .value_counts()
    .sort_index()
    .to_string()
)


# ============================================================
# QC 50 — Event Volume Distribution
# ============================================================

print("\n" + "=" * 60)
print("QC 50 — Event Volume Distribution")
print("=" * 60)

event_volume = pd.read_sql_query(
    """
    SELECT
        player_id,
        COUNT(*) AS total_events
    FROM events
    WHERE player_id IS NOT NULL
    GROUP BY player_id
    """,
    connection
)

event_volume = event_volume.merge(
    eda42[
        [
            "player_id",
            "player_name",
            "role_group"
        ]
    ],
    on="player_id",
    how="inner"
)

print("\nEvent volume statistics:")
print(
    event_volume["total_events"]
    .describe()
    .round(2)
    .to_string()
)

print("\nTop 20 players by event volume:")
print(
    event_volume
    .sort_values(
        "total_events",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)


# ============================================================
# QC 51 — Feature Outlier Analysis
# ============================================================

print("\n" + "=" * 60)
print("QC 51 — Feature Outlier Analysis")
print("=" * 60)

feature_columns = [
    "shooting_profile",
    "chance_creation_profile",
    "passing_profile",
    "defensive_profile",
    "carrying_profile",
    "duel_profile",
    "retention_recovery_profile"
]

outlier_summary = []

for feature in feature_columns:

    q1 = eda42[feature].quantile(0.25)
    q3 = eda42[feature].quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = eda42[
        (eda42[feature] < lower_bound)
        |
        (eda42[feature] > upper_bound)
    ]

    outlier_summary.append(
        {
            "feature": feature,
            "q1": q1,
            "q3": q3,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "outlier_count": len(outliers)
        }
    )

outlier_summary = pd.DataFrame(
    outlier_summary
)

print(
    outlier_summary
    .round(2)
    .to_string(index=False)
)


# ============================================================
# QC 52 — Missing Values in ML Features
# ============================================================

print("\n" + "=" * 60)
print("QC 52 — Missing Values in ML Features")
print("=" * 60)

ml_features = eda42[
    feature_columns
].copy()

missing_summary = pd.DataFrame(
    {
        "feature": ml_features.columns,
        "missing_count": ml_features.isna().sum().values,
        "missing_pct": (
            ml_features.isna().mean().values * 100
        )
    }
)

print(
    missing_summary
    .round(2)
    .to_string(index=False)
)

print(
    "\nTotal missing feature values:",
    int(ml_features.isna().sum().sum())
)


# ============================================================
# QC 53 — Role Group Sample Sizes
# ============================================================

print("\n" + "=" * 60)
print("QC 53 — Role Group Sample Sizes")
print("=" * 60)

role_sizes = (
    eda42
    .groupby("role_group")
    .agg(
        players=("player_id", "count")
    )
    .reset_index()
    .sort_values(
        "players",
        ascending=False
    )
)

print(
    role_sizes.to_string(index=False)
)

print(
    "\nTotal players across roles:",
    role_sizes["players"].sum()
)

print(
    "Number of role groups:",
    len(role_sizes)
)


# ============================================================
# QC 54 — Feature Distribution / Scaling Check
# ============================================================

print("\n" + "=" * 60)
print("QC 54 — Feature Distribution / Scaling Check")
print("=" * 60)

scaling_summary = (
    eda42[
        feature_columns
    ]
    .describe()
    .T
)

scaling_summary[
    "range"
] = (
    scaling_summary["max"]
    - scaling_summary["min"]
)

print(
    scaling_summary[
        [
            "count",
            "mean",
            "std",
            "min",
            "25%",
            "50%",
            "75%",
            "max",
            "range"
        ]
    ]
    .round(3)
    .to_string()
)


# ============================================================
# QC 55 — Final Analytics Consistency Check
# ============================================================

print("\n" + "=" * 60)
print("QC 55 — Final Analytics Consistency Check")
print("=" * 60)

# 1. Scouting population
population_count = len(eda42)

print(
    "Scouting population:",
    population_count,
    "expected 316"
)

# 2. Role groups
role_count = eda42["role_group"].nunique()

print(
    "Role groups:",
    role_count,
    "expected 8"
)

# 3. Duplicate players
duplicate_players = eda42["player_id"].duplicated().sum()

print(
    "Duplicate player IDs:",
    duplicate_players,
    "expected 0"
)

# 4. Missing scouting scores
missing_scores = eda42["scouting_score"].isna().sum()

print(
    "Missing scouting scores:",
    missing_scores,
    "expected 0"
)

# 5. Missing role groups
missing_roles = eda42["role_group"].isna().sum()

print(
    "Missing role groups:",
    missing_roles,
    "expected 0"
)

# 6. Invalid scouting scores
invalid_scores = (
    (
        eda42["scouting_score"] < 0
    )
    |
    (
        eda42["scouting_score"] > 100
    )
).sum()

print(
    "Scouting scores outside 0–100:",
    invalid_scores,
    "expected 0"
)

# 7. Role total
role_total = role_sizes["players"].sum()

print(
    "Role population total:",
    role_total,
    "expected 316"
)


# Final pass/fail
qc_passed = (
    population_count == 316
    and role_count == 8
    and duplicate_players == 0
    and missing_scores == 0
    and missing_roles == 0
    and invalid_scores == 0
    and role_total == 316
    and ml_features.isna().sum().sum() == 0
)

print("\n" + "=" * 60)

if qc_passed:
    print("FINAL ANALYTICAL QC: PASSED")
else:
    print("FINAL ANALYTICAL QC: REQUIRES REVIEW")

print("=" * 60)

connection.close()