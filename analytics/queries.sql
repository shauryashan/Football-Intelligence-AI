-- ========================================
-- Query 1: Total goals scored by team
-- ========================================

SELECT
    t.team_name,
    SUM(
        CASE
            WHEN m.home_team_id = t.team_id THEN m.home_score
            WHEN m.away_team_id = t.team_id THEN m.away_score
            ELSE 0
        END
    ) AS goals_scored
FROM teams t
JOIN matches m
    ON t.team_id = m.home_team_id
    OR t.team_id = m.away_team_id
GROUP BY
    t.team_id,
    t.team_name
ORDER BY
    goals_scored DESC;

    -- ========================================
-- Query 2: Total goals conceded by team
-- ========================================

SELECT
    t.team_name,
    SUM(
        CASE
            WHEN m.home_team_id = t.team_id THEN m.away_score
            WHEN m.away_team_id = t.team_id THEN m.home_score
            ELSE 0
        END
    ) AS goals_conceded
FROM teams t
JOIN matches m
    ON t.team_id = m.home_team_id
    OR t.team_id = m.away_team_id
GROUP BY
    t.team_id,
    t.team_name
ORDER BY
    goals_conceded ASC;

-- ========================================
-- Query 3: Wins, draws and losses by team
-- ========================================

SELECT
    t.team_name,

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
    ) AS losses

FROM teams t

JOIN matches m
    ON t.team_id = m.home_team_id
    OR t.team_id = m.away_team_id

GROUP BY
    t.team_id,
    t.team_name

ORDER BY
    wins DESC;

-- ========================================
-- Query 4: League table
-- ========================================

SELECT
    t.team_name,

    SUM(
        CASE
            WHEN (m.home_team_id = t.team_id AND m.home_score > m.away_score)
              OR (m.away_team_id = t.team_id AND m.away_score > m.home_score)
            THEN 3
            WHEN m.home_score = m.away_score
            THEN 1
            ELSE 0
        END
    ) AS points,

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
    ) AS losses

FROM teams t

JOIN matches m
    ON t.team_id = m.home_team_id
    OR t.team_id = m.away_team_id

GROUP BY
    t.team_id,
    t.team_name

ORDER BY
    points DESC;

-- ========================================
-- Query 5: Goal difference by team
-- ========================================

SELECT
    t.team_name,

    SUM(
        CASE
            WHEN m.home_team_id = t.team_id THEN m.home_score
            WHEN m.away_team_id = t.team_id THEN m.away_score
            ELSE 0
        END
    )
    -
    SUM(
        CASE
            WHEN m.home_team_id = t.team_id THEN m.away_score
            WHEN m.away_team_id = t.team_id THEN m.home_score
            ELSE 0
        END
    ) AS goal_difference

FROM teams t

JOIN matches m
    ON t.team_id = m.home_team_id
    OR t.team_id = m.away_team_id

GROUP BY
    t.team_id,
    t.team_name

ORDER BY
    goal_difference DESC;

-- ========================================
-- Query 6: Complete league table
-- ========================================

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
            WHEN m.home_team_id = t.team_id THEN m.home_score - m.away_score
            WHEN m.away_team_id = t.team_id THEN m.away_score - m.home_score
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

-- ========================================
-- Query 7: Player minutes
-- ========================================

SELECT
    p.player_name,
    SUM(pm.minutes_played) AS total_minutes
FROM players p
JOIN player_match pm
    ON p.player_id = pm.player_id
GROUP BY
    p.player_id,
    p.player_name
ORDER BY
    total_minutes DESC;

-- ========================================
-- Query 8: Players with playing time
-- ========================================

SELECT
    p.player_name,
    SUM(pm.minutes_played) AS total_minutes
FROM players p
JOIN player_match pm
    ON p.player_id = pm.player_id
GROUP BY
    p.player_id,
    p.player_name
HAVING
    SUM(pm.minutes_played) > 0
ORDER BY
    total_minutes DESC;

-- ========================================
-- Query 9: Player appearances
-- ========================================

SELECT
    p.player_name,
    COUNT(DISTINCT pm.match_id) AS appearances
FROM players p
JOIN player_match pm
    ON p.player_id = pm.player_id
WHERE
    pm.minutes_played > 0
GROUP BY
    p.player_id,
    p.player_name
ORDER BY
    appearances DESC;

-- ========================================
-- Query 10: Player appearances and minutes
-- ========================================

SELECT
    p.player_name,
    COUNT(DISTINCT pm.match_id) AS appearances,
    ROUND(SUM(pm.minutes_played), 2) AS total_minutes
FROM players p
JOIN player_match pm
    ON p.player_id = pm.player_id
WHERE
    pm.minutes_played > 0
GROUP BY
    p.player_id,
    p.player_name
ORDER BY
    total_minutes DESC;

-- ========================================
-- Query 11: Team shots and expected goals
-- ========================================

SELECT
    t.team_name,

    COUNT(e.event_id) AS shots,

    ROUND(SUM(e.shot_xg), 2) AS total_xg,

    SUM(
        CASE
            WHEN e.shot_outcome = 'Goal'
            THEN 1
            ELSE 0
        END
    ) AS goals

FROM teams t

JOIN events e
    ON t.team_id = e.team_id

WHERE
    e.event_type = 'Shot'

GROUP BY
    t.team_id,
    t.team_name

ORDER BY
    total_xg DESC;

-- ========================================
-- Query 12: Player shots and expected goals
-- ========================================

SELECT
    p.player_name,

    COUNT(e.event_id) AS shots,

    ROUND(SUM(e.shot_xg), 2) AS total_xg,

    SUM(
        CASE
            WHEN e.shot_outcome = 'Goal'
            THEN 1
            ELSE 0
        END
    ) AS goals

FROM players p

JOIN events e
    ON p.player_id = e.player_id

WHERE
    e.event_type = 'Shot'

GROUP BY
    p.player_id,
    p.player_name

ORDER BY
    total_xg DESC;

-- ========================================
-- Query 13: Player shooting efficiency
-- ========================================

SELECT
    p.player_name,

    COUNT(e.event_id) AS shots,

    ROUND(SUM(e.shot_xg), 2) AS total_xg,

    SUM(
        CASE
            WHEN e.shot_outcome = 'Goal'
            THEN 1
            ELSE 0
        END
    ) AS goals,

    ROUND(
        CAST(
            SUM(
                CASE
                    WHEN e.shot_outcome = 'Goal'
                    THEN 1
                    ELSE 0
                END
            ) AS REAL
        ) / COUNT(e.event_id),
        3
    ) AS goal_conversion,

    ROUND(
        SUM(e.shot_xg) / COUNT(e.event_id),
        3
    ) AS xg_per_shot

FROM players p

JOIN events e
    ON p.player_id = e.player_id

WHERE
    e.event_type = 'Shot'

GROUP BY
    p.player_id,
    p.player_name

ORDER BY
    xg_per_shot DESC;

-- ========================================
-- Query 14: Player passing statistics
-- ========================================

SELECT
    p.player_name,

    COUNT(e.event_id) AS passes,

    SUM(
        CASE
            WHEN e.pass_outcome IS NULL
            THEN 1
            ELSE 0
        END
    ) AS completed_passes,

    ROUND(
        CAST(
            SUM(
                CASE
                    WHEN e.pass_outcome IS NULL
                    THEN 1
                    ELSE 0
                END
            ) AS REAL
        ) / COUNT(e.event_id) * 100,
        2
    ) AS pass_completion_pct,

    ROUND(SUM(e.pass_length), 2) AS total_pass_distance

FROM players p

JOIN events e
    ON p.player_id = e.player_id

WHERE
    e.event_type = 'Pass'

GROUP BY
    p.player_id,
    p.player_name

ORDER BY
    passes DESC;

-- ========================================
-- Query 15: Team passing statistics
-- ========================================

SELECT
    t.team_name,

    COUNT(e.event_id) AS passes,

    SUM(
        CASE
            WHEN e.pass_outcome IS NULL
            THEN 1
            ELSE 0
        END
    ) AS completed_passes,

    ROUND(
        CAST(
            SUM(
                CASE
                    WHEN e.pass_outcome IS NULL
                THEN 1
                ELSE 0
                END
            ) AS REAL
        ) / COUNT(e.event_id) * 100,
        2
    ) AS pass_completion_pct,

    ROUND(SUM(e.pass_length), 2) AS total_pass_distance

FROM teams t

JOIN events e
    ON t.team_id = e.team_id

WHERE
    e.event_type = 'Pass'

GROUP BY
    t.team_id,
    t.team_name

ORDER BY
    passes DESC;

-- ========================================
-- Query 16: Team pressure statistics
-- ========================================

SELECT
    t.team_name,

    COUNT(e.event_id) AS pressures

FROM teams t

JOIN events e
    ON t.team_id = e.team_id

WHERE
    e.event_type = 'Pressure'

GROUP BY
    t.team_id,
    t.team_name

ORDER BY
    pressures DESC;

-- ========================================
-- Query 17: Player pressure statistics
-- ========================================

SELECT
    p.player_name,

    COUNT(e.event_id) AS pressures

FROM players p

JOIN events e
    ON p.player_id = e.player_id

WHERE
    e.event_type = 'Pressure'

GROUP BY
    p.player_id,
    p.player_name

ORDER BY
    pressures DESC;

-- ========================================
-- Query 18: Player carries and dribbles
-- ========================================

SELECT
    p.player_name,

    SUM(
        CASE
            WHEN e.event_type = 'Carry'
            THEN 1
            ELSE 0
        END
    ) AS carries,

    SUM(
        CASE
            WHEN e.event_type = 'Dribble'
            THEN 1
            ELSE 0
        END
    ) AS dribbles,

    SUM(
        CASE
            WHEN e.event_type = 'Dribble'
                 AND e.dribble_outcome = 'Complete'
            THEN 1
            ELSE 0
        END
    ) AS successful_dribbles

FROM players p

JOIN events e
    ON p.player_id = e.player_id

WHERE
    e.event_type IN ('Carry', 'Dribble')

GROUP BY
    p.player_id,
    p.player_name

ORDER BY
    carries DESC;

-- ========================================
-- Query 19: Player dribbling efficiency
-- ========================================

SELECT
    p.player_name,

    COUNT(e.event_id) AS dribbles,

    SUM(
        CASE
            WHEN e.dribble_outcome = 'Complete'
            THEN 1
            ELSE 0
        END
    ) AS successful_dribbles,

    ROUND(
        CAST(
            SUM(
                CASE
                    WHEN e.dribble_outcome = 'Complete'
                    THEN 1
                    ELSE 0
                END
            ) AS REAL
        ) / COUNT(e.event_id) * 100,
        2
    ) AS dribble_success_pct

FROM players p

JOIN events e
    ON p.player_id = e.player_id

WHERE
    e.event_type = 'Dribble'

GROUP BY
    p.player_id,
    p.player_name

ORDER BY
    dribble_success_pct DESC;

-- ========================================
-- Query 20: Player duel statistics
-- ========================================

SELECT
    p.player_name,

    COUNT(e.event_id) AS duels,

    SUM(
        CASE
            WHEN e.duel_type = 'Tackle'
            THEN 1
            ELSE 0
        END
    ) AS tackles,

    SUM(
        CASE
            WHEN e.duel_type = 'Aerial Lost'
            THEN 1
            ELSE 0
        END
    ) AS aerial_lost

FROM players p

JOIN events e
    ON p.player_id = e.player_id

WHERE
    e.event_type = 'Duel'

GROUP BY
    p.player_id,
    p.player_name

ORDER BY
    duels DESC;

-- ========================================
-- Query 21: Player key passes
-- ========================================

SELECT
    p.player_name,
    COUNT(*) AS key_passes

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

ORDER BY
    key_passes DESC;

-- ========================================
-- Query 22: Player assists
-- ========================================

SELECT
    p.player_name,
    COUNT(*) AS assists

FROM events shot

JOIN events pass_event
    ON shot.shot_key_pass_id = pass_event.event_id
   AND pass_event.event_type = 'Pass'

JOIN players p
    ON pass_event.player_id = p.player_id

WHERE
    shot.event_type = 'Shot'
    AND shot.shot_key_pass_id IS NOT NULL
    AND shot.shot_outcome = 'Goal'

GROUP BY
    p.player_id,
    p.player_name

ORDER BY
    assists DESC;

-- ========================================
-- Query 23: Player goal contributions
-- ========================================

WITH player_goals AS (

    SELECT
        p.player_id,
        p.player_name,
        COUNT(*) AS goals

    FROM players p

    JOIN events e
        ON p.player_id = e.player_id

    WHERE
        e.event_type = 'Shot'
        AND e.shot_outcome = 'Goal'

    GROUP BY
        p.player_id,
        p.player_name
),

player_assists AS (

    SELECT
        p.player_id,
        COUNT(*) AS assists

    FROM events shot

    JOIN events pass_event
        ON shot.shot_key_pass_id = pass_event.event_id
       AND pass_event.event_type = 'Pass'

    JOIN players p
        ON pass_event.player_id = p.player_id

    WHERE
        shot.event_type = 'Shot'
        AND shot.shot_key_pass_id IS NOT NULL
        AND shot.shot_outcome = 'Goal'

    GROUP BY
        p.player_id
)

SELECT
    g.player_name,
    g.goals,
    COALESCE(a.assists, 0) AS assists,
    g.goals + COALESCE(a.assists, 0) AS goal_contributions

FROM player_goals g

LEFT JOIN player_assists a
    ON g.player_id = a.player_id

ORDER BY
    goal_contributions DESC;

-- ========================================
-- Query 24: Player progressive passing
-- ========================================

SELECT
    p.player_name,

    COUNT(e.event_id) AS progressive_passes,

    ROUND(
        SUM(e.pass_end_x - e.location_x),
        2
    ) AS progressive_pass_distance

FROM players p

JOIN events e
    ON p.player_id = e.player_id

WHERE
    e.event_type = 'Pass'
    AND e.pass_end_x IS NOT NULL
    AND e.location_x IS NOT NULL
    AND (e.pass_end_x - e.location_x) >= 10

GROUP BY
    p.player_id,
    p.player_name

ORDER BY
    progressive_passes DESC;

-- ========================================
-- Query 25: Inspect team attacking direction
-- ========================================

SELECT
    period,
    team_id,
    COUNT(*) AS pass_count,
    ROUND(AVG(location_x), 2) AS avg_start_x,
    ROUND(AVG(pass_end_x), 2) AS avg_end_x
FROM events
WHERE
    event_type = 'Pass'
    AND location_x IS NOT NULL
    AND pass_end_x IS NOT NULL
GROUP BY
    period,
    team_id
ORDER BY
    period,
    team_id;

-- ========================================
-- Query 26: Inspect pitch coordinates by period
-- ========================================

SELECT
    period,

    COUNT(*) AS passes,

    ROUND(MIN(location_x), 2) AS min_start_x,
    ROUND(MAX(location_x), 2) AS max_start_x,

    ROUND(MIN(pass_end_x), 2) AS min_end_x,
    ROUND(MAX(pass_end_x), 2) AS max_end_x,

    ROUND(AVG(location_x), 2) AS avg_start_x,
    ROUND(AVG(pass_end_x), 2) AS avg_end_x

FROM events

WHERE
    event_type = 'Pass'
    AND location_x IS NOT NULL
    AND pass_end_x IS NOT NULL

GROUP BY
    period

ORDER BY
    period;

-- ========================================
-- Query 27: Player minutes exposure distribution
-- ========================================

WITH player_minutes AS (
    SELECT
        p.player_id,
        p.player_name,
        SUM(pm.minutes_played) AS total_minutes
    FROM players p
    JOIN player_match pm
        ON p.player_id = pm.player_id
    GROUP BY
        p.player_id,
        p.player_name
)

SELECT
    CASE
        WHEN total_minutes = 0 THEN '0 minutes'
        WHEN total_minutes < 450 THEN '<450 minutes'
        WHEN total_minutes < 900 THEN '450-899 minutes'
        WHEN total_minutes < 1800 THEN '900-1799 minutes'
        ELSE '1800+ minutes'
    END AS minutes_band,
    COUNT(*) AS player_count
FROM player_minutes
GROUP BY
    minutes_band
ORDER BY
    CASE minutes_band
        WHEN '0 minutes' THEN 1
        WHEN '<450 minutes' THEN 2
        WHEN '450-899 minutes' THEN 3
        WHEN '900-1799 minutes' THEN 4
        WHEN '1800+ minutes' THEN 5
    END;

-- ========================================
-- Query 28: Player attacking output per 90
-- Minimum 900 minutes
-- ========================================

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
),

player_shots AS (
    SELECT
        player_id,

        COUNT(*) AS shots,

        ROUND(SUM(shot_xg), 2) AS xg,

        SUM(
            CASE
                WHEN shot_outcome = 'Goal'
                THEN 1
                ELSE 0
            END
        ) AS goals

    FROM events
    WHERE
        event_type = 'Shot'
    GROUP BY
        player_id
)

SELECT
    p.player_name,

    ROUND(pm.total_minutes, 2) AS total_minutes,

    COALESCE(ps.shots, 0) AS shots,

    COALESCE(ps.xg, 0) AS xg,

    COALESCE(ps.goals, 0) AS goals,

    ROUND(
        COALESCE(ps.shots, 0) / (pm.total_minutes / 90.0),
        2
    ) AS shots_per_90,

    ROUND(
        COALESCE(ps.xg, 0) / (pm.total_minutes / 90.0),
        2
    ) AS xg_per_90,

    ROUND(
        COALESCE(ps.goals, 0) / (pm.total_minutes / 90.0),
        2
    ) AS goals_per_90

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

LEFT JOIN player_shots ps
    ON pm.player_id = ps.player_id

WHERE
    pm.total_minutes >= 900

ORDER BY
    goals_per_90 DESC;

-- ========================================
-- Query 29: Player chance creation per 90
-- Minimum 900 minutes
-- ========================================

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
),

player_chances AS (
    SELECT
        p.player_id,

        COUNT(*) AS key_passes,

        SUM(
            CASE
                WHEN e.shot_outcome = 'Goal'
                THEN 1
                ELSE 0
            END
        ) AS assists

    FROM players p

    JOIN events pass_event
        ON p.player_id = pass_event.player_id
       AND pass_event.event_type = 'Pass'

    JOIN events e
        ON pass_event.event_id = e.shot_key_pass_id
       AND e.event_type = 'Shot'

    WHERE
        e.shot_key_pass_id IS NOT NULL

    GROUP BY
        p.player_id
)

SELECT
    p.player_name,

    ROUND(pm.total_minutes, 2) AS total_minutes,

    COALESCE(pc.key_passes, 0) AS key_passes,

    COALESCE(pc.assists, 0) AS assists,

    ROUND(
        COALESCE(pc.key_passes, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS key_passes_per_90,

    ROUND(
        COALESCE(pc.assists, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS assists_per_90

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

LEFT JOIN player_chances pc
    ON pm.player_id = pc.player_id

WHERE
    pm.total_minutes >= 900

ORDER BY
    key_passes_per_90 DESC;

-- ========================================
-- Query 30: Player passing output per 90
-- Minimum 900 minutes
-- ========================================

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
),

player_passing AS (
    SELECT
        player_id,

        COUNT(*) AS total_passes,

        SUM(
            CASE
                WHEN pass_outcome IS NULL
                THEN 1
                ELSE 0
            END
        ) AS completed_passes,

        SUM(
            CASE
                WHEN pass_length IS NOT NULL
                THEN pass_length
                ELSE 0
            END
        ) AS total_pass_distance

    FROM events
    WHERE
        event_type = 'Pass'
    GROUP BY
        player_id
)

SELECT
    p.player_name,

    ROUND(pm.total_minutes, 2) AS total_minutes,

    COALESCE(pp.total_passes, 0) AS total_passes,

    COALESCE(pp.completed_passes, 0) AS completed_passes,

    ROUND(
        COALESCE(pp.total_passes, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS passes_per_90,

    ROUND(
        COALESCE(pp.completed_passes, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS completed_passes_per_90,

    ROUND(
        COALESCE(pp.total_pass_distance, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS pass_distance_per_90

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

LEFT JOIN player_passing pp
    ON pm.player_id = pp.player_id

WHERE
    pm.total_minutes >= 900

ORDER BY
    passes_per_90 DESC;

-- ========================================
-- Query 31: Player defensive activity per 90
-- Minimum 900 minutes
-- ========================================

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
),

player_defensive AS (
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
        ) AS interceptions,

        SUM(
            CASE
                WHEN event_type = 'Clearance'
                THEN 1
                ELSE 0
            END
        ) AS clearances

    FROM events
    WHERE
        event_type IN (
            'Pressure',
            'Duel',
            'Interception',
            'Clearance'
        )
    GROUP BY
        player_id
)

SELECT
    p.player_name,

    ROUND(pm.total_minutes, 2) AS total_minutes,

    COALESCE(pd.pressures, 0) AS pressures,

    COALESCE(pd.tackles, 0) AS tackles,

    COALESCE(pd.interceptions, 0) AS interceptions,

    COALESCE(pd.clearances, 0) AS clearances,

    ROUND(
        COALESCE(pd.pressures, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS pressures_per_90,

    ROUND(
        COALESCE(pd.tackles, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS tackles_per_90,

    ROUND(
        COALESCE(pd.interceptions, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS interceptions_per_90,

    ROUND(
        COALESCE(pd.clearances, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS clearances_per_90

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

LEFT JOIN player_defensive pd
    ON pm.player_id = pd.player_id

WHERE
    pm.total_minutes >= 900

ORDER BY
    pressures_per_90 DESC;

-- ========================================
-- Query 32: Player ball-carrying output per 90
-- Minimum 900 minutes
-- ========================================

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
),

player_carrying AS (
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
    WHERE
        event_type IN ('Carry', 'Dribble')
    GROUP BY
        player_id
)

SELECT
    p.player_name,

    ROUND(pm.total_minutes, 2) AS total_minutes,

    COALESCE(pc.carries, 0) AS carries,

    COALESCE(pc.dribbles, 0) AS dribbles,

    COALESCE(pc.successful_dribbles, 0) AS successful_dribbles,

    ROUND(
        COALESCE(pc.carries, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS carries_per_90,

    ROUND(
        COALESCE(pc.dribbles, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS dribbles_per_90,

    ROUND(
        COALESCE(pc.successful_dribbles, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS successful_dribbles_per_90,

    ROUND(
        CASE
            WHEN pc.dribbles > 0
            THEN 100.0 * pc.successful_dribbles / pc.dribbles
            ELSE 0
        END,
        2
    ) AS dribble_success_pct

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

LEFT JOIN player_carrying pc
    ON pm.player_id = pc.player_id

WHERE
    pm.total_minutes >= 900

ORDER BY
    carries_per_90 DESC;

-- ========================================
-- Query 33: Player defensive duels per 90
-- Minimum 900 minutes
-- ========================================

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
),

player_duels AS (
    SELECT
        player_id,

        COUNT(*) AS duels,

        SUM(
            CASE
                WHEN duel_type = 'Tackle'
                THEN 1
                ELSE 0
            END
        ) AS tackles,

        SUM(
            CASE
                WHEN duel_type = 'Aerial'
                THEN 1
                ELSE 0
            END
        ) AS aerial_duels

    FROM events
    WHERE
        event_type = 'Duel'
    GROUP BY
        player_id
)

SELECT
    p.player_name,

    ROUND(pm.total_minutes, 2) AS total_minutes,

    COALESCE(pd.duels, 0) AS duels,

    COALESCE(pd.tackles, 0) AS tackles,

    COALESCE(pd.aerial_duels, 0) AS aerial_duels,

    ROUND(
        COALESCE(pd.duels, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS duels_per_90,

    ROUND(
        COALESCE(pd.tackles, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS tackles_per_90,

    ROUND(
        COALESCE(pd.aerial_duels, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS aerial_duels_per_90

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

LEFT JOIN player_duels pd
    ON pm.player_id = pd.player_id

WHERE
    pm.total_minutes >= 900

ORDER BY
    duels_per_90 DESC;

-- ========================================
-- Query 34: Inspect StatsBomb duel types
-- Diagnostic query
-- ========================================

SELECT
    duel_type,
    COUNT(*) AS duel_events
FROM events
WHERE
    event_type = 'Duel'
GROUP BY
    duel_type
ORDER BY
    duel_events DESC;

-- ========================================
-- Query 35: Defensive duel metrics per 90
-- Minimum 900 minutes
-- ========================================

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
),

player_duels AS (
    SELECT
        player_id,

        COUNT(*) AS duels,

        SUM(
            CASE
                WHEN duel_type = 'Tackle'
                THEN 1
                ELSE 0
            END
        ) AS tackles,

        SUM(
            CASE
                WHEN duel_type = 'Aerial Lost'
                THEN 1
                ELSE 0
            END
        ) AS aerial_duels_lost

    FROM events
    WHERE
        event_type = 'Duel'
    GROUP BY
        player_id
)

SELECT
    p.player_name,

    ROUND(pm.total_minutes, 2) AS total_minutes,

    COALESCE(pd.duels, 0) AS duels,

    COALESCE(pd.tackles, 0) AS tackles,

    COALESCE(pd.aerial_duels_lost, 0) AS aerial_duels_lost,

    ROUND(
        COALESCE(pd.duels, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS duels_per_90,

    ROUND(
        COALESCE(pd.tackles, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS tackles_per_90,

    ROUND(
        COALESCE(pd.aerial_duels_lost, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS aerial_duels_lost_per_90

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

LEFT JOIN player_duels pd
    ON pm.player_id = pd.player_id

WHERE
    pm.total_minutes >= 900

ORDER BY
    duels_per_90 DESC;

-- ========================================
-- Query 36: Player ball retention/recovery per 90
-- Minimum 900 minutes
-- ========================================

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
),

player_possession AS (
    SELECT
        player_id,

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
                WHEN event_type = 'Ball Recovery'
                THEN 1
                ELSE 0
            END
        ) AS ball_recoveries

    FROM events
    WHERE
        event_type IN (
            'Miscontrol',
            'Dispossessed',
            'Ball Recovery'
        )
    GROUP BY
        player_id
)

SELECT
    p.player_name,

    ROUND(pm.total_minutes, 2) AS total_minutes,

    COALESCE(pp.miscontrols, 0) AS miscontrols,

    COALESCE(pp.dispossessed, 0) AS dispossessed,

    COALESCE(pp.ball_recoveries, 0) AS ball_recoveries,

    ROUND(
        COALESCE(pp.miscontrols, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS miscontrols_per_90,

    ROUND(
        COALESCE(pp.dispossessed, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS dispossessed_per_90,

    ROUND(
        COALESCE(pp.ball_recoveries, 0) /
        (pm.total_minutes / 90.0),
        2
    ) AS ball_recoveries_per_90

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

LEFT JOIN player_possession pp
    ON pm.player_id = pp.player_id

WHERE
    pm.total_minutes >= 900

ORDER BY
    ball_recoveries_per_90 DESC;

-- ========================================
-- Query 37: Player position distribution
-- ========================================

SELECT
    position_id,
    position,
    COUNT(*) AS player_match_records,
    COUNT(DISTINCT player_id) AS unique_players
FROM player_match
WHERE
    position IS NOT NULL
GROUP BY
    position_id,
    position
ORDER BY
    unique_players DESC;

-- ========================================
-- Query 38: Player primary position
-- Based on minutes played
-- Minimum 900 total minutes
-- ========================================

WITH position_minutes AS (
    SELECT
        player_id,
        position_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE
        position IS NOT NULL
    GROUP BY
        player_id,
        position_id,
        position
),

ranked_positions AS (
    SELECT
        player_id,
        position_id,
        position,
        position_minutes,
        ROW_NUMBER() OVER (
            PARTITION BY player_id
            ORDER BY
                position_minutes DESC,
                position_id
        ) AS position_rank
    FROM position_minutes
),

total_player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
)

SELECT
    p.player_name,
    ROUND(tm.total_minutes, 2) AS total_minutes,
    rp.position_id,
    rp.position AS primary_position,
    ROUND(rp.position_minutes, 2) AS position_minutes,
    ROUND(
        100.0 * rp.position_minutes / tm.total_minutes,
        2
    ) AS position_share_pct

FROM ranked_positions rp

JOIN total_player_minutes tm
    ON rp.player_id = tm.player_id

JOIN players p
    ON rp.player_id = p.player_id

WHERE
    rp.position_rank = 1
    AND tm.total_minutes >= 900

ORDER BY
    tm.total_minutes DESC;

-- ========================================
-- Query 39: Primary position reliability
-- Minimum 900 total minutes
-- ========================================

WITH position_minutes AS (
    SELECT
        player_id,
        position_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE
        position IS NOT NULL
    GROUP BY
        player_id,
        position_id,
        position
),

ranked_positions AS (
    SELECT
        player_id,
        position_id,
        position,
        position_minutes,
        ROW_NUMBER() OVER (
            PARTITION BY player_id
            ORDER BY
                position_minutes DESC,
                position_id
        ) AS position_rank
    FROM position_minutes
),

total_player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
)

SELECT
    CASE
        WHEN 100.0 * rp.position_minutes / tm.total_minutes >= 75
            THEN '75%+'
        WHEN 100.0 * rp.position_minutes / tm.total_minutes >= 50
            THEN '50-74%'
        WHEN 100.0 * rp.position_minutes / tm.total_minutes >= 25
            THEN '25-49%'
        ELSE '<25%'
    END AS position_share_band,

    COUNT(*) AS players

FROM ranked_positions rp

JOIN total_player_minutes tm
    ON rp.player_id = tm.player_id

WHERE
    rp.position_rank = 1
    AND tm.total_minutes >= 900

GROUP BY
    position_share_band

ORDER BY
    CASE position_share_band
        WHEN '75%+' THEN 1
        WHEN '50-74%' THEN 2
        WHEN '25-49%' THEN 3
        WHEN '<25%' THEN 4
    END;

-- ========================================
-- Query 40: Primary position distribution
-- Minimum 900 total minutes
-- ========================================

WITH position_minutes AS (
    SELECT
        player_id,
        position_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE
        position IS NOT NULL
    GROUP BY
        player_id,
        position_id,
        position
),

ranked_positions AS (
    SELECT
        player_id,
        position_id,
        position,
        position_minutes,
        ROW_NUMBER() OVER (
            PARTITION BY player_id
            ORDER BY
                position_minutes DESC,
                position_id
        ) AS position_rank
    FROM position_minutes
),

total_player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
)

SELECT
    rp.position_id,
    rp.position AS primary_position,
    COUNT(*) AS players
FROM ranked_positions rp

JOIN total_player_minutes tm
    ON rp.player_id = tm.player_id

WHERE
    rp.position_rank = 1
    AND tm.total_minutes >= 900

GROUP BY
    rp.position_id,
    rp.position

ORDER BY
    players DESC;

-- ========================================
-- Query 41: Analytical role-group distribution
-- Minimum 900 total minutes
-- ========================================

WITH position_minutes AS (
    SELECT
        player_id,
        position_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE
        position IS NOT NULL
    GROUP BY
        player_id,
        position_id,
        position
),

ranked_positions AS (
    SELECT
        player_id,
        position_id,
        position,
        position_minutes,
        ROW_NUMBER() OVER (
            PARTITION BY player_id
            ORDER BY
                position_minutes DESC,
                position_id
        ) AS position_rank
    FROM position_minutes
),

total_player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
)

SELECT
    CASE
        WHEN rp.position_id = 1
            THEN 'Goalkeeper'

        WHEN rp.position_id IN (3, 4, 5)
            THEN 'Centre Back'

        WHEN rp.position_id IN (2, 6)
            THEN 'Full Back'

        WHEN rp.position_id IN (7, 8)
            THEN 'Wing Back'

        WHEN rp.position_id IN (9, 10, 11)
            THEN 'Defensive Midfielder'

        WHEN rp.position_id IN (12, 13, 15, 16)
            THEN 'Central Midfielder'

        WHEN rp.position_id IN (18, 19, 20)
            THEN 'Attacking Midfielder'

        WHEN rp.position_id IN (17, 21)
            THEN 'Winger'

        WHEN rp.position_id IN (22, 23, 24)
            THEN 'Forward'

        ELSE 'Other'
    END AS role_group,

    COUNT(*) AS players

FROM ranked_positions rp

JOIN total_player_minutes tm
    ON rp.player_id = tm.player_id

WHERE
    rp.position_rank = 1
    AND tm.total_minutes >= 900

GROUP BY
    role_group

ORDER BY
    players DESC;

-- ========================================
-- Query 42: Role-group performance profile
-- Minimum 900 minutes
-- ========================================

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
),

player_events AS (
    SELECT
        player_id,

        SUM(CASE WHEN event_type = 'Shot' THEN 1 ELSE 0 END) AS shots,

        SUM(CASE
            WHEN event_type = 'Shot'
            THEN COALESCE(shot_xg, 0)
            ELSE 0
        END) AS xg,

        SUM(CASE
            WHEN event_type = 'Shot'
                 AND shot_outcome = 'Goal'
            THEN 1
            ELSE 0
        END) AS goals,

        SUM(CASE
            WHEN event_type = 'Pass'
            THEN 1
            ELSE 0
        END) AS passes,

        SUM(CASE
            WHEN event_type = 'Pass'
                 AND pass_outcome IS NULL
            THEN 1
            WHEN event_type = 'Pass'
                 AND pass_outcome = 'Complete'
            THEN 1
            ELSE 0
        END) AS completed_passes,

        SUM(CASE WHEN event_type = 'Pressure' THEN 1 ELSE 0 END) AS pressures,

        SUM(CASE
            WHEN event_type = 'Tackle'
            THEN 1
            ELSE 0
        END) AS tackles,

        SUM(CASE
            WHEN event_type = 'Interception'
            THEN 1
            ELSE 0
        END) AS interceptions,

        SUM(CASE
            WHEN event_type = 'Clearance'
            THEN 1
            ELSE 0
        END) AS clearances,

        SUM(CASE WHEN event_type = 'Carry' THEN 1 ELSE 0 END) AS carries,

        SUM(CASE
            WHEN event_type = 'Dribble'
            THEN 1
            ELSE 0
        END) AS dribbles,

        SUM(CASE
            WHEN event_type = 'Dribble'
                 AND dribble_outcome = 'Complete'
            THEN 1
            ELSE 0
        END) AS successful_dribbles,

        SUM(CASE
            WHEN event_type = 'Miscontrol'
            THEN 1
            ELSE 0
        END) AS miscontrols,

        SUM(CASE
            WHEN event_type = 'Dispossessed'
            THEN 1
            ELSE 0
        END) AS dispossessed,

        SUM(CASE
            WHEN event_type = 'Ball Recovery'
            THEN 1
            ELSE 0
        END) AS ball_recoveries,

        SUM(CASE
            WHEN event_type = 'Duel'
            THEN 1
            ELSE 0
        END) AS duels,

        SUM(CASE
            WHEN event_type = 'Aerial Lost'
            THEN 1
            ELSE 0
        END) AS aerial_duels_lost

    FROM events

    GROUP BY
        player_id
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
    GROUP BY
        pass_event.player_id
),

primary_positions AS (
    SELECT
        player_id,
        position_id,
        position,
        position_minutes
    FROM (
        SELECT
            player_id,
            position_id,
            position,
            SUM(minutes_played) AS position_minutes,

            ROW_NUMBER() OVER (
                PARTITION BY player_id
                ORDER BY
                    SUM(minutes_played) DESC,
                    position_id
            ) AS position_rank

        FROM player_match

        WHERE
            position IS NOT NULL

        GROUP BY
            player_id,
            position_id,
            position
    )

    WHERE
        position_rank = 1
)

SELECT
    CASE
        WHEN pp.position_id = 1
            THEN 'Goalkeeper'

        WHEN pp.position_id IN (3, 4, 5)
            THEN 'Centre Back'

        WHEN pp.position_id IN (2, 6)
            THEN 'Full Back'

        WHEN pp.position_id IN (7, 8)
            THEN 'Wing Back'

        WHEN pp.position_id IN (9, 10, 11)
            THEN 'Defensive Midfielder'

        WHEN pp.position_id IN (12, 13, 15, 16)
            THEN 'Central Midfielder'

        WHEN pp.position_id IN (18, 19, 20)
            THEN 'Attacking Midfielder'

        WHEN pp.position_id IN (17, 21)
            THEN 'Winger'

        WHEN pp.position_id IN (22, 23, 24)
            THEN 'Forward'

        ELSE 'Other'
    END AS role_group,

    COUNT(*) AS players,

    ROUND(AVG(
        COALESCE(pe.shots, 0) /
        (pm.total_minutes / 90.0)
    ), 2) AS avg_shots_per_90,

    ROUND(AVG(
        COALESCE(pe.xg, 0) /
        (pm.total_minutes / 90.0)
    ), 2) AS avg_xg_per_90,

    ROUND(AVG(
        COALESCE(pe.goals, 0) /
        (pm.total_minutes / 90.0)
    ), 2) AS avg_goals_per_90,

    ROUND(AVG(
        COALESCE(kp.key_passes, 0) /
        (pm.total_minutes / 90.0)
    ), 2) AS avg_key_passes_per_90,

    ROUND(AVG(
        COALESCE(pe.passes, 0) /
        (pm.total_minutes / 90.0)
    ), 2) AS avg_passes_per_90,

    ROUND(AVG(
        COALESCE(pe.pressures, 0) /
        (pm.total_minutes / 90.0)
    ), 2) AS avg_pressures_per_90,

    ROUND(AVG(
        COALESCE(pe.tackles, 0) /
        (pm.total_minutes / 90.0)
    ), 2) AS avg_tackles_per_90,

    ROUND(AVG(
        COALESCE(pe.interceptions, 0) /
        (pm.total_minutes / 90.0)
    ), 2) AS avg_interceptions_per_90,

    ROUND(AVG(
        COALESCE(pe.carries, 0) /
        (pm.total_minutes / 90.0)
    ), 2) AS avg_carries_per_90,

    ROUND(AVG(
        COALESCE(pe.dribbles, 0) /
        (pm.total_minutes / 90.0)
    ), 2) AS avg_dribbles_per_90,

    ROUND(AVG(
        COALESCE(pe.ball_recoveries, 0) /
        (pm.total_minutes / 90.0)
    ), 2) AS avg_ball_recoveries_per_90

FROM primary_positions pp

JOIN player_minutes pm
    ON pp.player_id = pm.player_id

LEFT JOIN player_events pe
    ON pp.player_id = pe.player_id

LEFT JOIN key_passes kp
    ON pp.player_id = kp.player_id

WHERE
    pm.total_minutes >= 900

GROUP BY
    role_group

ORDER BY
    players DESC;

-- ========================================
-- Query 43: Role-group aggregate event rates
-- Minimum 900 total minutes
-- ========================================

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
),

primary_positions AS (
    SELECT
        player_id,
        position_id,
        position,
        position_minutes
    FROM (
        SELECT
            player_id,
            position_id,
            position,
            SUM(minutes_played) AS position_minutes,

            ROW_NUMBER() OVER (
                PARTITION BY player_id
                ORDER BY
                    SUM(minutes_played) DESC,
                    position_id
            ) AS position_rank

        FROM player_match

        WHERE
            position IS NOT NULL

        GROUP BY
            player_id,
            position_id,
            position
    )

    WHERE
        position_rank = 1
),

player_events AS (
    SELECT
        player_id,

        SUM(CASE WHEN event_type = 'Shot' THEN 1 ELSE 0 END) AS shots,

        SUM(
            CASE
                WHEN event_type = 'Shot'
                THEN COALESCE(shot_xg, 0)
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

        SUM(CASE WHEN event_type = 'Pass' THEN 1 ELSE 0 END) AS passes,

        SUM(
            CASE
                WHEN event_type = 'Pass'
                     AND (
                         pass_outcome IS NULL
                         OR pass_outcome = 'Complete'
                     )
                THEN 1
                ELSE 0
            END
        ) AS completed_passes,

        SUM(CASE WHEN event_type = 'Pressure' THEN 1 ELSE 0 END) AS pressures,

        SUM(CASE WHEN event_type = 'Tackle' THEN 1 ELSE 0 END) AS tackles,

        SUM(
            CASE
                WHEN event_type = 'Interception'
                THEN 1
                ELSE 0
            END
        ) AS interceptions,

        SUM(
            CASE
                WHEN event_type = 'Clearance'
                THEN 1
                ELSE 0
            END
        ) AS clearances,

        SUM(CASE WHEN event_type = 'Carry' THEN 1 ELSE 0 END) AS carries,

        SUM(CASE WHEN event_type = 'Dribble' THEN 1 ELSE 0 END) AS dribbles,

        SUM(
            CASE
                WHEN event_type = 'Ball Recovery'
                THEN 1
                ELSE 0
            END
        ) AS ball_recoveries

    FROM events

    GROUP BY
        player_id
)

SELECT
    CASE
        WHEN pp.position_id = 1
            THEN 'Goalkeeper'

        WHEN pp.position_id IN (3, 4, 5)
            THEN 'Centre Back'

        WHEN pp.position_id IN (2, 6)
            THEN 'Full Back'

        WHEN pp.position_id IN (7, 8)
            THEN 'Wing Back'

        WHEN pp.position_id IN (9, 10, 11)
            THEN 'Defensive Midfielder'

        WHEN pp.position_id IN (12, 13, 15, 16)
            THEN 'Central Midfielder'

        WHEN pp.position_id IN (18, 19, 20)
            THEN 'Attacking Midfielder'

        WHEN pp.position_id IN (17, 21)
            THEN 'Winger'

        WHEN pp.position_id IN (22, 23, 24)
            THEN 'Forward'

        ELSE 'Other'
    END AS role_group,

    COUNT(*) AS players,

    ROUND(
        SUM(COALESCE(pe.shots, 0))
        / (SUM(pm.total_minutes) / 90.0),
        2
    ) AS shots_per_90,

    ROUND(
        SUM(COALESCE(pe.xg, 0))
        / (SUM(pm.total_minutes) / 90.0),
        2
    ) AS xg_per_90,

    ROUND(
        SUM(COALESCE(pe.goals, 0))
        / (SUM(pm.total_minutes) / 90.0),
        2
    ) AS goals_per_90,

    ROUND(
        SUM(COALESCE(pe.passes, 0))
        / (SUM(pm.total_minutes) / 90.0),
        2
    ) AS passes_per_90,

    ROUND(
        SUM(COALESCE(pe.completed_passes, 0))
        / (SUM(pm.total_minutes) / 90.0),
        2
    ) AS completed_passes_per_90,

    ROUND(
        SUM(COALESCE(pe.pressures, 0))
        / (SUM(pm.total_minutes) / 90.0),
        2
    ) AS pressures_per_90,

    ROUND(
        SUM(COALESCE(pe.tackles, 0))
        / (SUM(pm.total_minutes) / 90.0),
        2
    ) AS tackles_per_90,

    ROUND(
        SUM(COALESCE(pe.interceptions, 0))
        / (SUM(pm.total_minutes) / 90.0),
        2
    ) AS interceptions_per_90,

    ROUND(
        SUM(COALESCE(pe.clearances, 0))
        / (SUM(pm.total_minutes) / 90.0),
        2
    ) AS clearances_per_90,

    ROUND(
        SUM(COALESCE(pe.carries, 0))
        / (SUM(pm.total_minutes) / 90.0),
        2
    ) AS carries_per_90,

    ROUND(
        SUM(COALESCE(pe.dribbles, 0))
        / (SUM(pm.total_minutes) / 90.0),
        2
    ) AS dribbles_per_90,

    ROUND(
        SUM(COALESCE(pe.ball_recoveries, 0))
        / (SUM(pm.total_minutes) / 90.0),
        2
    ) AS ball_recoveries_per_90

FROM primary_positions pp

JOIN player_minutes pm
    ON pp.player_id = pm.player_id

LEFT JOIN player_events pe
    ON pp.player_id = pe.player_id

WHERE
    pm.total_minutes >= 900

GROUP BY
    role_group

ORDER BY
    players DESC;

-- ========================================
-- Query 44: Role-group exposure profile
-- ========================================

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
),

primary_positions AS (
    SELECT
        player_id,
        position_id,
        position,
        position_minutes
    FROM (
        SELECT
            player_id,
            position_id,
            position,
            SUM(minutes_played) AS position_minutes,

            ROW_NUMBER() OVER (
                PARTITION BY player_id
                ORDER BY
                    SUM(minutes_played) DESC,
                    position_id
            ) AS position_rank

        FROM player_match

        WHERE
            position IS NOT NULL

        GROUP BY
            player_id,
            position_id,
            position
    )

    WHERE
        position_rank = 1
)

SELECT
    CASE
        WHEN pp.position_id = 1
            THEN 'Goalkeeper'

        WHEN pp.position_id IN (3, 4, 5)
            THEN 'Centre Back'

        WHEN pp.position_id IN (2, 6)
            THEN 'Full Back'

        WHEN pp.position_id IN (7, 8)
            THEN 'Wing Back'

        WHEN pp.position_id IN (9, 10, 11)
            THEN 'Defensive Midfielder'

        WHEN pp.position_id IN (12, 13, 15, 16)
            THEN 'Central Midfielder'

        WHEN pp.position_id IN (18, 19, 20)
            THEN 'Attacking Midfielder'

        WHEN pp.position_id IN (17, 21)
            THEN 'Winger'

        WHEN pp.position_id IN (22, 23, 24)
            THEN 'Forward'

        ELSE 'Other'
    END AS role_group,

    COUNT(*) AS players,

    ROUND(AVG(pm.total_minutes), 2) AS avg_minutes,

    ROUND(MIN(pm.total_minutes), 2) AS min_minutes,

    ROUND(MAX(pm.total_minutes), 2) AS max_minutes

FROM primary_positions pp

JOIN player_minutes pm
    ON pp.player_id = pm.player_id

WHERE
    pm.total_minutes >= 900

GROUP BY
    role_group

ORDER BY
    players DESC;

-- ========================================
-- Query 45: Player scouting feature base
-- Minimum 900 minutes
-- ========================================

WITH position_minutes AS (
    SELECT
        player_id,
        position_id,
        position,
        SUM(minutes_played) AS position_minutes
    FROM player_match
    WHERE
        position IS NOT NULL
    GROUP BY
        player_id,
        position_id,
        position
),

ranked_positions AS (
    SELECT
        player_id,
        position_id,
        position,
        position_minutes,
        ROW_NUMBER() OVER (
            PARTITION BY player_id
            ORDER BY
                position_minutes DESC,
                position_id
        ) AS position_rank
    FROM position_minutes
),

player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY
        player_id
)

SELECT
    p.player_id,
    p.player_name,

    pm.total_minutes,

    rp.position_id,
    rp.position AS primary_position,

    ROUND(
        100.0 * rp.position_minutes / pm.total_minutes,
        2
    ) AS position_share_pct,

    CASE
        WHEN rp.position_id = 1
            THEN 'Goalkeeper'

        WHEN rp.position_id IN (3, 4, 5)
            THEN 'Centre Back'

        WHEN rp.position_id IN (2, 6)
            THEN 'Full Back'

        WHEN rp.position_id IN (7, 8)
            THEN 'Wing Back'

        WHEN rp.position_id IN (9, 10, 11)
            THEN 'Defensive Midfielder'

        WHEN rp.position_id IN (12, 13, 15, 16)
            THEN 'Central Midfielder'

        WHEN rp.position_id IN (18, 19, 20)
            THEN 'Attacking Midfielder'

        WHEN rp.position_id IN (17, 21)
            THEN 'Winger'

        WHEN rp.position_id IN (22, 23, 24)
            THEN 'Forward'

        ELSE 'Other'
    END AS role_group

FROM ranked_positions rp

JOIN player_minutes pm
    ON rp.player_id = pm.player_id

JOIN players p
    ON rp.player_id = p.player_id

WHERE
    rp.position_rank = 1
    AND pm.total_minutes >= 900

ORDER BY
    role_group,
    pm.total_minutes DESC;

-- Query 46: Unified Player Scouting Feature Table

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
),

attacking AS (
    SELECT
        player_id,
        COUNT(*) AS shots,
        SUM(COALESCE(shot_xg, 0)) AS total_xg,
        SUM(CASE WHEN shot_outcome = 'Goal' THEN 1 ELSE 0 END) AS goals
    FROM events
    WHERE event_type = 'Shot'
    GROUP BY player_id
),

chance_creation AS (
    SELECT
        pass_event.player_id,
        COUNT(*) AS key_passes,
        SUM(
            CASE
                WHEN shot.shot_outcome = 'Goal' THEN 1
                ELSE 0
            END
        ) AS assists
    FROM events shot
    JOIN events pass_event
        ON shot.shot_key_pass_id = pass_event.event_id
       AND pass_event.event_type = 'Pass'
    WHERE
        shot.event_type = 'Shot'
        AND shot.shot_key_pass_id IS NOT NULL
    GROUP BY pass_event.player_id
),

passing AS (
    SELECT
        player_id,
        COUNT(*) AS passes,
        SUM(
            CASE
                WHEN pass_outcome IS NULL
                     OR pass_outcome = 'Complete'
                THEN 1
                ELSE 0
            END
        ) AS completed_passes,
        SUM(COALESCE(pass_length, 0)) AS pass_distance
    FROM events
    WHERE event_type = 'Pass'
    GROUP BY player_id
),

defensive AS (
    SELECT
        player_id,
        SUM(CASE WHEN event_type = 'Pressure' THEN 1 ELSE 0 END) AS pressures,
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
                WHEN event_type = 'Clearance'
                THEN 1
                ELSE 0
            END
        ) AS clearances
    FROM events
    WHERE event_type IN (
        'Pressure',
        'Duel',
        'Interception',
        'Clearance'
    )
    GROUP BY player_id
),

carrying AS (
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
    WHERE event_type IN ('Carry', 'Dribble')
    GROUP BY player_id
),

duels AS (
    SELECT
        player_id,
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
    WHERE event_type = 'Duel'
    GROUP BY player_id
),

retention AS (
    SELECT
        player_id,
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
                WHEN event_type = 'Ball Recovery'
                THEN 1
                ELSE 0
            END
        ) AS ball_recoveries
    FROM events
    WHERE event_type IN (
        'Miscontrol',
        'Dispossessed',
        'Ball Recovery'
    )
    GROUP BY player_id
),

position_data AS (
    SELECT
        player_id,
        position AS primary_position,
        position_share_pct,
        role_group
    FROM (
        SELECT
            player_id,
            position,
            role_group,
            position_share_pct,
            ROW_NUMBER() OVER (
                PARTITION BY player_id
                ORDER BY position_minutes DESC
            ) AS rn
        FROM (
            SELECT
                pm.player_id,
                pm.position,
                pm.role_group,
                pm.position_minutes,
                pm.position_minutes * 100.0
                    / SUM(pm.position_minutes) OVER (
                        PARTITION BY pm.player_id
                    ) AS position_share_pct
            FROM (
                SELECT
                    player_match.player_id,
                    player_match.position,
                    SUM(player_match.minutes_played) AS position_minutes,

                    CASE
                        WHEN player_match.position IN (
                            'Goalkeeper'
                        )
                            THEN 'Goalkeeper'

                        WHEN player_match.position IN (
                            'Left Center Back',
                            'Center Back',
                            'Right Center Back'
                        )
                            THEN 'Centre Back'

                        WHEN player_match.position IN (
                            'Left Back',
                            'Right Back',
                            'Left Wing Back',
                            'Right Wing Back'
                        )
                            THEN 'Full Back'

                        WHEN player_match.position IN (
                            'Left Defensive Midfield',
                            'Right Defensive Midfield',
                            'Center Defensive Midfield'
                        )
                            THEN 'Defensive Midfielder'

                        WHEN player_match.position IN (
                            'Left Center Midfield',
                            'Center Midfield',
                            'Right Center Midfield'
                        )
                            THEN 'Central Midfielder'

                        WHEN player_match.position IN (
                            'Left Attacking Midfield',
                            'Center Attacking Midfield',
                            'Right Attacking Midfield'
                        )
                            THEN 'Attacking Midfielder'

                        WHEN player_match.position IN (
                            'Left Wing',
                            'Right Wing'
                        )
                            THEN 'Winger'

                        WHEN player_match.position IN (
                            'Center Forward',
                            'Left Center Forward',
                            'Right Center Forward'
                        )
                            THEN 'Forward'

                        ELSE 'Other'
                    END AS role_group

                FROM player_match
                WHERE
                    player_match.position IS NOT NULL
                GROUP BY
                    player_match.player_id,
                    player_match.position
            ) pm
        )
    )
    WHERE rn = 1
)

SELECT
    p.player_id,
    p.player_name,

    ROUND(pm.total_minutes, 2) AS total_minutes,

    pd.primary_position,
    ROUND(pd.position_share_pct, 2) AS position_share_pct,
    pd.role_group,

    -- Attacking
    COALESCE(a.shots, 0) AS shots,
    ROUND(
        COALESCE(a.shots, 0) / (pm.total_minutes / 90.0),
        2
    ) AS shots_per_90,

    ROUND(
        COALESCE(a.total_xg, 0) / (pm.total_minutes / 90.0),
        2
    ) AS xg_per_90,

    COALESCE(a.goals, 0) AS goals,

    ROUND(
        COALESCE(a.goals, 0) / (pm.total_minutes / 90.0),
        2
    ) AS goals_per_90,

    -- Chance creation
    COALESCE(cc.key_passes, 0) AS key_passes,

    ROUND(
        COALESCE(cc.key_passes, 0) / (pm.total_minutes / 90.0),
        2
    ) AS key_passes_per_90,

    COALESCE(cc.assists, 0) AS assists,

    ROUND(
        COALESCE(cc.assists, 0) / (pm.total_minutes / 90.0),
        2
    ) AS assists_per_90,

    -- Passing
    COALESCE(pa.passes, 0) AS passes,

    ROUND(
        COALESCE(pa.passes, 0) / (pm.total_minutes / 90.0),
        2
    ) AS passes_per_90,

    COALESCE(pa.completed_passes, 0) AS completed_passes,

    ROUND(
        COALESCE(pa.completed_passes, 0)
        / (pm.total_minutes / 90.0),
        2
    ) AS completed_passes_per_90,

    ROUND(
        COALESCE(pa.pass_distance, 0)
        / (pm.total_minutes / 90.0),
        2
    ) AS pass_distance_per_90,

    -- Defensive activity
    COALESCE(d.pressures, 0) AS pressures,

    ROUND(
        COALESCE(d.pressures, 0) / (pm.total_minutes / 90.0),
        2
    ) AS pressures_per_90,

    COALESCE(d.tackles, 0) AS tackles,

    ROUND(
        COALESCE(d.tackles, 0) / (pm.total_minutes / 90.0),
        2
    ) AS tackles_per_90,

    COALESCE(d.interceptions, 0) AS interceptions,

    ROUND(
        COALESCE(d.interceptions, 0) / (pm.total_minutes / 90.0),
        2
    ) AS interceptions_per_90,

    COALESCE(d.clearances, 0) AS clearances,

    ROUND(
        COALESCE(d.clearances, 0) / (pm.total_minutes / 90.0),
        2
    ) AS clearances_per_90,

    -- Carrying / dribbling
    COALESCE(c.carries, 0) AS carries,

    ROUND(
        COALESCE(c.carries, 0) / (pm.total_minutes / 90.0),
        2
    ) AS carries_per_90,

    COALESCE(c.dribbles, 0) AS dribbles,

    ROUND(
        COALESCE(c.dribbles, 0) / (pm.total_minutes / 90.0),
        2
    ) AS dribbles_per_90,

    COALESCE(c.successful_dribbles, 0) AS successful_dribbles,

    ROUND(
        COALESCE(c.successful_dribbles, 0)
        / (pm.total_minutes / 90.0),
        2
    ) AS successful_dribbles_per_90,

    ROUND(
        CASE
            WHEN COALESCE(c.dribbles, 0) > 0
            THEN c.successful_dribbles * 100.0 / c.dribbles
            ELSE 0
        END,
        2
    ) AS dribble_success_pct,

    -- Duels
    COALESCE(du.duels, 0) AS duels,

    ROUND(
        COALESCE(du.duels, 0) / (pm.total_minutes / 90.0),
        2
    ) AS duels_per_90,

    COALESCE(du.aerial_duels_lost, 0) AS aerial_duels_lost,

    ROUND(
        COALESCE(du.aerial_duels_lost, 0)
        / (pm.total_minutes / 90.0),
        2
    ) AS aerial_duels_lost_per_90,

    -- Ball retention / recovery
    COALESCE(r.miscontrols, 0) AS miscontrols,

    ROUND(
        COALESCE(r.miscontrols, 0) / (pm.total_minutes / 90.0),
        2
    ) AS miscontrols_per_90,

    COALESCE(r.dispossessed, 0) AS dispossessed,

    ROUND(
        COALESCE(r.dispossessed, 0) / (pm.total_minutes / 90.0),
        2
    ) AS dispossessed_per_90,

    COALESCE(r.ball_recoveries, 0) AS ball_recoveries,

    ROUND(
        COALESCE(r.ball_recoveries, 0)
        / (pm.total_minutes / 90.0),
        2
    ) AS ball_recoveries_per_90

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

LEFT JOIN attacking a
    ON pm.player_id = a.player_id

LEFT JOIN chance_creation cc
    ON pm.player_id = cc.player_id

LEFT JOIN passing pa
    ON pm.player_id = pa.player_id

LEFT JOIN defensive d
    ON pm.player_id = d.player_id

LEFT JOIN carrying c
    ON pm.player_id = c.player_id

LEFT JOIN duels du
    ON pm.player_id = du.player_id

LEFT JOIN retention r
    ON pm.player_id = r.player_id

LEFT JOIN position_data pd
    ON pm.player_id = pd.player_id

WHERE
    pm.total_minutes >= 900

ORDER BY
    pm.total_minutes DESC;

-- Query 47: Role-Specific Scouting Feature Selection

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
    GROUP BY
        player_id,
        position
),

position_classified AS (
    SELECT
        player_id,
        position,
        position_minutes,

        CASE
            WHEN position = 'Goalkeeper'
                THEN 'Goalkeeper'

            WHEN position IN (
                'Left Center Back',
                'Center Back',
                'Right Center Back'
            )
                THEN 'Centre Back'

            WHEN position IN (
                'Left Back',
                'Right Back',
                'Left Wing Back',
                'Right Wing Back'
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
                'Center Midfield',
                'Right Center Midfield'
            )
                THEN 'Central Midfielder'

            WHEN position IN (
                'Left Attacking Midfield',
                'Center Attacking Midfield',
                'Right Attacking Midfield'
            )
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

    FROM position_minutes
),

primary_position AS (
    SELECT
        player_id,
        position AS primary_position,
        role_group,
        position_minutes,

        position_minutes * 100.0
            / SUM(position_minutes) OVER (
                PARTITION BY player_id
            ) AS position_share_pct,

        ROW_NUMBER() OVER (
            PARTITION BY player_id
            ORDER BY position_minutes DESC
        ) AS rn

    FROM position_classified
)

SELECT
    p.player_id,
    p.player_name,

    ROUND(pm.total_minutes, 2) AS total_minutes,

    pp.primary_position,

    ROUND(pp.position_share_pct, 2) AS position_share_pct,

    pp.role_group,

    CASE
        WHEN pp.role_group = 'Goalkeeper'
            THEN 'pressures_per_90,passes_per_90,completed_passes_per_90,clearances_per_90,ball_recoveries_per_90'

        WHEN pp.role_group = 'Centre Back'
            THEN 'passes_per_90,completed_passes_per_90,pressures_per_90,tackles_per_90,interceptions_per_90,clearances_per_90,duels_per_90,aerial_duels_lost_per_90'

        WHEN pp.role_group = 'Full Back'
            THEN 'passes_per_90,completed_passes_per_90,pressures_per_90,tackles_per_90,interceptions_per_90,carries_per_90,dribbles_per_90,successful_dribbles_per_90'

        WHEN pp.role_group = 'Defensive Midfielder'
            THEN 'passes_per_90,completed_passes_per_90,pressures_per_90,tackles_per_90,interceptions_per_90,duels_per_90,ball_recoveries_per_90'

        WHEN pp.role_group = 'Central Midfielder'
            THEN 'passes_per_90,completed_passes_per_90,pass_distance_per_90,key_passes_per_90,carries_per_90,pressures_per_90,interceptions_per_90,ball_recoveries_per_90'

        WHEN pp.role_group = 'Attacking Midfielder'
            THEN 'xg_per_90,goals_per_90,shots_per_90,key_passes_per_90,assists_per_90,passes_per_90,carries_per_90,dribbles_per_90'

        WHEN pp.role_group = 'Winger'
            THEN 'xg_per_90,goals_per_90,shots_per_90,key_passes_per_90,assists_per_90,carries_per_90,dribbles_per_90,successful_dribbles_per_90'

        WHEN pp.role_group = 'Forward'
            THEN 'xg_per_90,goals_per_90,shots_per_90,key_passes_per_90,assists_per_90,duels_per_90,dispossessed_per_90'

        ELSE ''
    END AS recommended_features

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

JOIN primary_position pp
    ON pm.player_id = pp.player_id
    AND pp.rn = 1

WHERE
    pm.total_minutes >= 900

ORDER BY
    pp.role_group,
    p.player_name;

-- Query 48: Role-Specific Percentile Scores

WITH player_features AS (

    /*
        This CTE reproduces the validated Query 46
        player-level feature table.

        We keep the 900-minute threshold because
        this is our established scouting population.
    */

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

    primary_positions AS (
        SELECT
            player_id,
            position AS primary_position,
            position_minutes * 100.0
                / SUM(position_minutes) OVER (
                    PARTITION BY player_id
                ) AS position_share_pct,

            CASE
                WHEN position = 'Goalkeeper'
                    THEN 'Goalkeeper'

                WHEN position IN (
                    'Left Center Back',
                    'Center Back',
                    'Right Center Back'
                )
                    THEN 'Centre Back'

                WHEN position IN (
                    'Left Back',
                    'Right Back',
                    'Left Wing Back',
                    'Right Wing Back'
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
                    'Center Midfield',
                    'Right Center Midfield'
                )
                    THEN 'Central Midfielder'

                WHEN position IN (
                    'Left Attacking Midfield',
                    'Center Attacking Midfield',
                    'Right Attacking Midfield'
                )
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
            END AS role_group,

            ROW_NUMBER() OVER (
                PARTITION BY player_id
                ORDER BY position_minutes DESC
            ) AS rn

        FROM position_minutes
    ),

    player_roles AS (
        SELECT
            player_id,
            primary_position,
            position_share_pct,
            role_group
        FROM primary_positions
        WHERE rn = 1
    ),

    attacking AS (
        SELECT
            e.player_id,

            COUNT(*) / (
                pm.total_minutes / 90.0
            ) AS shots_per_90,

            SUM(COALESCE(e.shot_xg, 0)) / (
                pm.total_minutes / 90.0
            ) AS xg_per_90,

            SUM(
                CASE
                    WHEN e.shot_outcome = 'Goal'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS goals_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type = 'Shot'

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    chance_creation AS (
        SELECT
            pass_event.player_id,

            COUNT(*) / (
                pm.total_minutes / 90.0
            ) AS key_passes_per_90,

            SUM(
                CASE
                    WHEN shot.shot_outcome = 'Goal'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS assists_per_90

        FROM events shot

        JOIN events pass_event
            ON shot.shot_key_pass_id = pass_event.event_id
            AND pass_event.event_type = 'Pass'

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON pass_event.player_id = pm.player_id

        WHERE
            shot.event_type = 'Shot'
            AND shot.shot_key_pass_id IS NOT NULL

        GROUP BY
            pass_event.player_id,
            pm.total_minutes
    ),

    passing AS (
        SELECT
            e.player_id,

            COUNT(*) / (
                pm.total_minutes / 90.0
            ) AS passes_per_90,

            SUM(
                CASE
                    WHEN e.pass_outcome IS NULL
                         OR e.pass_outcome = 'Complete'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS completed_passes_per_90,

            SUM(COALESCE(e.pass_length, 0)) / (
                pm.total_minutes / 90.0
            ) AS pass_distance_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type = 'Pass'

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    defensive AS (
        SELECT
            e.player_id,

            SUM(
                CASE
                    WHEN e.event_type = 'Pressure'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS pressures_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Duel'
                         AND e.duel_type = 'Tackle'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS tackles_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Interception'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS interceptions_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Clearance'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS clearances_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type IN (
            'Pressure',
            'Duel',
            'Interception',
            'Clearance'
        )

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    carrying AS (
        SELECT
            e.player_id,

            SUM(
                CASE
                    WHEN e.event_type = 'Carry'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS carries_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Dribble'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS dribbles_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Dribble'
                         AND e.dribble_outcome = 'Complete'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS successful_dribbles_per_90,

            CASE
                WHEN SUM(
                    CASE
                        WHEN e.event_type = 'Dribble'
                        THEN 1
                        ELSE 0
                    END
                ) > 0
                THEN
                    SUM(
                        CASE
                            WHEN e.event_type = 'Dribble'
                                 AND e.dribble_outcome = 'Complete'
                            THEN 1
                            ELSE 0
                        END
                    ) * 100.0
                    /
                    SUM(
                        CASE
                            WHEN e.event_type = 'Dribble'
                            THEN 1
                            ELSE 0
                        END
                    )
                ELSE 0
            END AS dribble_success_pct

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type IN (
            'Carry',
            'Dribble'
        )

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    duels AS (
        SELECT
            e.player_id,

            SUM(
                CASE
                    WHEN e.event_type = 'Duel'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS duels_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Duel'
                         AND e.duel_type = 'Aerial Lost'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS aerial_duels_lost_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type = 'Duel'

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    retention AS (
        SELECT
            e.player_id,

            SUM(
                CASE
                    WHEN e.event_type = 'Miscontrol'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS miscontrols_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Dispossessed'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS dispossessed_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Ball Recovery'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS ball_recoveries_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type IN (
            'Miscontrol',
            'Dispossessed',
            'Ball Recovery'
        )

        GROUP BY
            e.player_id,
            pm.total_minutes
    )

    SELECT
        p.player_id,
        p.player_name,
        pm.total_minutes,

        pr.primary_position,
        pr.position_share_pct,
        pr.role_group,

        COALESCE(a.shots_per_90, 0) AS shots_per_90,
        COALESCE(a.xg_per_90, 0) AS xg_per_90,
        COALESCE(a.goals_per_90, 0) AS goals_per_90,

        COALESCE(cc.key_passes_per_90, 0) AS key_passes_per_90,
        COALESCE(cc.assists_per_90, 0) AS assists_per_90,

        COALESCE(pa.passes_per_90, 0) AS passes_per_90,
        COALESCE(pa.completed_passes_per_90, 0) AS completed_passes_per_90,
        COALESCE(pa.pass_distance_per_90, 0) AS pass_distance_per_90,

        COALESCE(d.pressures_per_90, 0) AS pressures_per_90,
        COALESCE(d.tackles_per_90, 0) AS tackles_per_90,
        COALESCE(d.interceptions_per_90, 0) AS interceptions_per_90,
        COALESCE(d.clearances_per_90, 0) AS clearances_per_90,

        COALESCE(c.carries_per_90, 0) AS carries_per_90,
        COALESCE(c.dribbles_per_90, 0) AS dribbles_per_90,
        COALESCE(c.successful_dribbles_per_90, 0) AS successful_dribbles_per_90,
        COALESCE(c.dribble_success_pct, 0) AS dribble_success_pct,

        COALESCE(du.duels_per_90, 0) AS duels_per_90,
        COALESCE(du.aerial_duels_lost_per_90, 0)
            AS aerial_duels_lost_per_90,

        COALESCE(r.miscontrols_per_90, 0) AS miscontrols_per_90,
        COALESCE(r.dispossessed_per_90, 0) AS dispossessed_per_90,
        COALESCE(r.ball_recoveries_per_90, 0)
            AS ball_recoveries_per_90

    FROM player_minutes pm

    JOIN players p
        ON pm.player_id = p.player_id

    JOIN player_roles pr
        ON pm.player_id = pr.player_id

    LEFT JOIN attacking a
        ON pm.player_id = a.player_id

    LEFT JOIN chance_creation cc
        ON pm.player_id = cc.player_id

    LEFT JOIN passing pa
        ON pm.player_id = pa.player_id

    LEFT JOIN defensive d
        ON pm.player_id = d.player_id

    LEFT JOIN carrying c
        ON pm.player_id = c.player_id

    LEFT JOIN duels du
        ON pm.player_id = du.player_id

    LEFT JOIN retention r
        ON pm.player_id = r.player_id

    WHERE pm.total_minutes >= 900
),

percentiles AS (

    SELECT
        *,

        -- Higher is better
        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY xg_per_90
            ) * 100,
            2
        ) AS xg_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY goals_per_90
            ) * 100,
            2
        ) AS goals_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY shots_per_90
            ) * 100,
            2
        ) AS shots_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY key_passes_per_90
            ) * 100,
            2
        ) AS key_passes_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY assists_per_90
            ) * 100,
            2
        ) AS assists_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY passes_per_90
            ) * 100,
            2
        ) AS passes_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY completed_passes_per_90
            ) * 100,
            2
        ) AS completed_passes_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY pass_distance_per_90
            ) * 100,
            2
        ) AS pass_distance_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY pressures_per_90
            ) * 100,
            2
        ) AS pressures_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY tackles_per_90
            ) * 100,
            2
        ) AS tackles_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY interceptions_per_90
            ) * 100,
            2
        ) AS interceptions_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY clearances_per_90
            ) * 100,
            2
        ) AS clearances_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY carries_per_90
            ) * 100,
            2
        ) AS carries_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY dribbles_per_90
            ) * 100,
            2
        ) AS dribbles_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY successful_dribbles_per_90
            ) * 100,
            2
        ) AS successful_dribbles_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY dribble_success_pct
            ) * 100,
            2
        ) AS dribble_success_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY duels_per_90
            ) * 100,
            2
        ) AS duels_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY aerial_duels_lost_per_90 DESC
            ) * 100,
            2
        ) AS aerial_duels_lost_percentile,

        -- Lower is better, so reverse the ranking.
        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY miscontrols_per_90 DESC
            ) * 100,
            2
        ) AS miscontrols_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY dispossessed_per_90 DESC
            ) * 100,
            2
        ) AS dispossessed_percentile,

        ROUND(
            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY ball_recoveries_per_90
            ) * 100,
            2
        ) AS ball_recoveries_percentile

    FROM player_features
)

SELECT
    player_id,
    player_name,
    ROUND(total_minutes, 2) AS total_minutes,
    primary_position,
    ROUND(position_share_pct, 2) AS position_share_pct,
    role_group,

    xg_percentile,
    goals_percentile,
    shots_percentile,
    key_passes_percentile,
    assists_percentile,

    passes_percentile,
    completed_passes_percentile,
    pass_distance_percentile,

    pressures_percentile,
    tackles_percentile,
    interceptions_percentile,
    clearances_percentile,

    carries_percentile,
    dribbles_percentile,
    successful_dribbles_percentile,
    dribble_success_percentile,

    duels_percentile,
    aerial_duels_lost_percentile,

    miscontrols_percentile,
    dispossessed_percentile,
    ball_recoveries_percentile

FROM percentiles

ORDER BY
    role_group,
    player_name;

-- Query 49: Role-Aware Scouting Profile

WITH player_percentiles AS (

    /*
        Recreate the percentile layer from Query 48.
        Each metric is ranked against players in the
        same analytical role.
    */

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
        GROUP BY
            player_id,
            position
    ),

    primary_positions AS (
        SELECT
            player_id,
            position AS primary_position,
            position_minutes,

            position_minutes * 100.0
                / SUM(position_minutes) OVER (
                    PARTITION BY player_id
                ) AS position_share_pct,

            CASE
                WHEN position = 'Goalkeeper'
                    THEN 'Goalkeeper'

                WHEN position IN (
                    'Left Center Back',
                    'Center Back',
                    'Right Center Back'
                )
                    THEN 'Centre Back'

                WHEN position IN (
                    'Left Back',
                    'Right Back',
                    'Left Wing Back',
                    'Right Wing Back'
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
                    'Center Midfield',
                    'Right Center Midfield'
                )
                    THEN 'Central Midfielder'

                WHEN position IN (
                    'Left Attacking Midfield',
                    'Center Attacking Midfield',
                    'Right Attacking Midfield'
                )
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
            END AS role_group,

            ROW_NUMBER() OVER (
                PARTITION BY player_id
                ORDER BY position_minutes DESC
            ) AS rn

        FROM position_minutes
    ),

    player_roles AS (
        SELECT
            player_id,
            primary_position,
            position_share_pct,
            role_group
        FROM primary_positions
        WHERE rn = 1
    ),

    attacking AS (
        SELECT
            e.player_id,

            COUNT(*) / (
                pm.total_minutes / 90.0
            ) AS shots_per_90,

            SUM(COALESCE(e.shot_xg, 0)) / (
                pm.total_minutes / 90.0
            ) AS xg_per_90,

            SUM(
                CASE
                    WHEN e.shot_outcome = 'Goal'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS goals_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type = 'Shot'

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    chance_creation AS (
        SELECT
            pass_event.player_id,

            COUNT(*) / (
                pm.total_minutes / 90.0
            ) AS key_passes_per_90,

            SUM(
                CASE
                    WHEN shot.shot_outcome = 'Goal'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS assists_per_90

        FROM events shot

        JOIN events pass_event
            ON shot.shot_key_pass_id = pass_event.event_id
            AND pass_event.event_type = 'Pass'

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON pass_event.player_id = pm.player_id

        WHERE
            shot.event_type = 'Shot'
            AND shot.shot_key_pass_id IS NOT NULL

        GROUP BY
            pass_event.player_id,
            pm.total_minutes
    ),

    passing AS (
        SELECT
            e.player_id,

            COUNT(*) / (
                pm.total_minutes / 90.0
            ) AS passes_per_90,

            SUM(
                CASE
                    WHEN e.pass_outcome IS NULL
                         OR e.pass_outcome = 'Complete'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS completed_passes_per_90,

            SUM(COALESCE(e.pass_length, 0)) / (
                pm.total_minutes / 90.0
            ) AS pass_distance_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type = 'Pass'

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    defensive AS (
        SELECT
            e.player_id,

            SUM(
                CASE
                    WHEN e.event_type = 'Pressure'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS pressures_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Duel'
                         AND e.duel_type = 'Tackle'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS tackles_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Interception'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS interceptions_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Clearance'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS clearances_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type IN (
            'Pressure',
            'Duel',
            'Interception',
            'Clearance'
        )

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    carrying AS (
        SELECT
            e.player_id,

            SUM(
                CASE
                    WHEN e.event_type = 'Carry'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS carries_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Dribble'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS dribbles_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Dribble'
                         AND e.dribble_outcome = 'Complete'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS successful_dribbles_per_90,

            CASE
                WHEN SUM(
                    CASE
                        WHEN e.event_type = 'Dribble'
                        THEN 1
                        ELSE 0
                    END
                ) > 0
                THEN
                    SUM(
                        CASE
                            WHEN e.event_type = 'Dribble'
                                 AND e.dribble_outcome = 'Complete'
                            THEN 1
                            ELSE 0
                        END
                    ) * 100.0
                    /
                    SUM(
                        CASE
                            WHEN e.event_type = 'Dribble'
                            THEN 1
                            ELSE 0
                        END
                    )
                ELSE 0
            END AS dribble_success_pct

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type IN (
            'Carry',
            'Dribble'
        )

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    duels AS (
        SELECT
            e.player_id,

            SUM(
                CASE
                    WHEN e.event_type = 'Duel'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS duels_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Duel'
                         AND e.duel_type = 'Aerial Lost'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS aerial_duels_lost_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type = 'Duel'

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    retention AS (
        SELECT
            e.player_id,

            SUM(
                CASE
                    WHEN e.event_type = 'Miscontrol'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS miscontrols_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Dispossessed'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS dispossessed_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Ball Recovery'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS ball_recoveries_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type IN (
            'Miscontrol',
            'Dispossessed',
            'Ball Recovery'
        )

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    raw_features AS (

        SELECT
            p.player_id,
            p.player_name,
            pm.total_minutes,

            pr.primary_position,
            pr.position_share_pct,
            pr.role_group,

            COALESCE(a.shots_per_90, 0) AS shots_per_90,
            COALESCE(a.xg_per_90, 0) AS xg_per_90,
            COALESCE(a.goals_per_90, 0) AS goals_per_90,

            COALESCE(cc.key_passes_per_90, 0)
                AS key_passes_per_90,

            COALESCE(cc.assists_per_90, 0)
                AS assists_per_90,

            COALESCE(pa.passes_per_90, 0)
                AS passes_per_90,

            COALESCE(pa.completed_passes_per_90, 0)
                AS completed_passes_per_90,

            COALESCE(pa.pass_distance_per_90, 0)
                AS pass_distance_per_90,

            COALESCE(d.pressures_per_90, 0)
                AS pressures_per_90,

            COALESCE(d.tackles_per_90, 0)
                AS tackles_per_90,

            COALESCE(d.interceptions_per_90, 0)
                AS interceptions_per_90,

            COALESCE(d.clearances_per_90, 0)
                AS clearances_per_90,

            COALESCE(c.carries_per_90, 0)
                AS carries_per_90,

            COALESCE(c.dribbles_per_90, 0)
                AS dribbles_per_90,

            COALESCE(c.successful_dribbles_per_90, 0)
                AS successful_dribbles_per_90,

            COALESCE(c.dribble_success_pct, 0)
                AS dribble_success_pct,

            COALESCE(du.duels_per_90, 0)
                AS duels_per_90,

            COALESCE(du.aerial_duels_lost_per_90, 0)
                AS aerial_duels_lost_per_90,

            COALESCE(r.miscontrols_per_90, 0)
                AS miscontrols_per_90,

            COALESCE(r.dispossessed_per_90, 0)
                AS dispossessed_per_90,

            COALESCE(r.ball_recoveries_per_90, 0)
                AS ball_recoveries_per_90

        FROM player_minutes pm

        JOIN players p
            ON pm.player_id = p.player_id

        JOIN player_roles pr
            ON pm.player_id = pr.player_id

        LEFT JOIN attacking a
            ON pm.player_id = a.player_id

        LEFT JOIN chance_creation cc
            ON pm.player_id = cc.player_id

        LEFT JOIN passing pa
            ON pm.player_id = pa.player_id

        LEFT JOIN defensive d
            ON pm.player_id = d.player_id

        LEFT JOIN carrying c
            ON pm.player_id = c.player_id

        LEFT JOIN duels du
            ON pm.player_id = du.player_id

        LEFT JOIN retention r
            ON pm.player_id = r.player_id

        WHERE pm.total_minutes >= 900
    )

    SELECT
        *,
        
        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY xg_per_90
        ) * 100 AS xg_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY goals_per_90
        ) * 100 AS goals_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY shots_per_90
        ) * 100 AS shots_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY key_passes_per_90
        ) * 100 AS key_passes_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY assists_per_90
        ) * 100 AS assists_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY passes_per_90
        ) * 100 AS passes_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY completed_passes_per_90
        ) * 100 AS completed_passes_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY pass_distance_per_90
        ) * 100 AS pass_distance_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY pressures_per_90
        ) * 100 AS pressures_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY tackles_per_90
        ) * 100 AS tackles_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY interceptions_per_90
        ) * 100 AS interceptions_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY clearances_per_90
        ) * 100 AS clearances_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY carries_per_90
        ) * 100 AS carries_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY dribbles_per_90
        ) * 100 AS dribbles_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY successful_dribbles_per_90
        ) * 100 AS successful_dribbles_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY dribble_success_pct
        ) * 100 AS dribble_success_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY duels_per_90
        ) * 100 AS duels_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY aerial_duels_lost_per_90 DESC
        ) * 100 AS aerial_duels_lost_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY miscontrols_per_90 DESC
        ) * 100 AS miscontrols_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY dispossessed_per_90 DESC
        ) * 100 AS dispossessed_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY role_group
            ORDER BY ball_recoveries_per_90
        ) * 100 AS ball_recoveries_percentile

    FROM raw_features
)

SELECT
    player_id,
    player_name,
    ROUND(total_minutes, 2) AS total_minutes,
    primary_position,
    ROUND(position_share_pct, 2) AS position_share_pct,
    role_group,

    -- Shooting profile
    ROUND(
        (xg_percentile
        + goals_percentile
        + shots_percentile) / 3.0,
        2
    ) AS shooting_profile,

    -- Chance creation profile
    ROUND(
        (key_passes_percentile
        + assists_percentile) / 2.0,
        2
    ) AS chance_creation_profile,

    -- Passing profile
    ROUND(
        (passes_percentile
        + completed_passes_percentile
        + pass_distance_percentile) / 3.0,
        2
    ) AS passing_profile,

    -- Defensive profile
    ROUND(
        (pressures_percentile
        + tackles_percentile
        + interceptions_percentile
        + clearances_percentile) / 4.0,
        2
    ) AS defensive_profile,

    -- Carrying / dribbling profile
    ROUND(
        (carries_percentile
        + dribbles_percentile
        + successful_dribbles_percentile
        + dribble_success_percentile) / 4.0,
        2
    ) AS carrying_profile,

    -- Duel profile
    ROUND(
        (duels_percentile
        + aerial_duels_lost_percentile) / 2.0,
        2
    ) AS duel_profile,

    -- Ball retention / recovery profile
    ROUND(
        (miscontrols_percentile
        + dispossessed_percentile
        + ball_recoveries_percentile) / 3.0,
        2
    ) AS retention_recovery_profile

FROM player_percentiles

ORDER BY
    role_group,
    player_name;

-- Query 50: Role-Aware Scouting Score and Ranking

WITH scouting_profiles AS (

    /*
        Query 49 profile layer.

        Each profile is already expressed as a
        within-role percentile-based score.
    */

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
        GROUP BY
            player_id,
            position
    ),

    primary_positions AS (
        SELECT
            player_id,
            position AS primary_position,
            position_minutes,

            position_minutes * 100.0
                / SUM(position_minutes) OVER (
                    PARTITION BY player_id
                ) AS position_share_pct,

            CASE
                WHEN position = 'Goalkeeper'
                    THEN 'Goalkeeper'

                WHEN position IN (
                    'Left Center Back',
                    'Center Back',
                    'Right Center Back'
                )
                    THEN 'Centre Back'

                WHEN position IN (
                    'Left Back',
                    'Right Back',
                    'Left Wing Back',
                    'Right Wing Back'
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
                    'Center Midfield',
                    'Right Center Midfield'
                )
                    THEN 'Central Midfielder'

                WHEN position IN (
                    'Left Attacking Midfield',
                    'Center Attacking Midfield',
                    'Right Attacking Midfield'
                )
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
            END AS role_group,

            ROW_NUMBER() OVER (
                PARTITION BY player_id
                ORDER BY position_minutes DESC
            ) AS rn

        FROM position_minutes
    ),

    player_roles AS (
        SELECT
            player_id,
            primary_position,
            position_share_pct,
            role_group
        FROM primary_positions
        WHERE rn = 1
    ),

    attacking AS (
        SELECT
            e.player_id,

            COUNT(*) / (
                pm.total_minutes / 90.0
            ) AS shots_per_90,

            SUM(COALESCE(e.shot_xg, 0)) / (
                pm.total_minutes / 90.0
            ) AS xg_per_90,

            SUM(
                CASE
                    WHEN e.shot_outcome = 'Goal'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS goals_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type = 'Shot'

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    chance_creation AS (
        SELECT
            pass_event.player_id,

            COUNT(*) / (
                pm.total_minutes / 90.0
            ) AS key_passes_per_90,

            SUM(
                CASE
                    WHEN shot.shot_outcome = 'Goal'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS assists_per_90

        FROM events shot

        JOIN events pass_event
            ON shot.shot_key_pass_id = pass_event.event_id
            AND pass_event.event_type = 'Pass'

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON pass_event.player_id = pm.player_id

        WHERE
            shot.event_type = 'Shot'
            AND shot.shot_key_pass_id IS NOT NULL

        GROUP BY
            pass_event.player_id,
            pm.total_minutes
    ),

    passing AS (
        SELECT
            e.player_id,

            COUNT(*) / (
                pm.total_minutes / 90.0
            ) AS passes_per_90,

            SUM(
                CASE
                    WHEN e.pass_outcome IS NULL
                         OR e.pass_outcome = 'Complete'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS completed_passes_per_90,

            SUM(COALESCE(e.pass_length, 0)) / (
                pm.total_minutes / 90.0
            ) AS pass_distance_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type = 'Pass'

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    defensive AS (
        SELECT
            e.player_id,

            SUM(
                CASE
                    WHEN e.event_type = 'Pressure'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS pressures_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Duel'
                         AND e.duel_type = 'Tackle'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS tackles_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Interception'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS interceptions_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Clearance'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS clearances_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type IN (
            'Pressure',
            'Duel',
            'Interception',
            'Clearance'
        )

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    carrying AS (
        SELECT
            e.player_id,

            SUM(
                CASE
                    WHEN e.event_type = 'Carry'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS carries_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Dribble'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS dribbles_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Dribble'
                         AND e.dribble_outcome = 'Complete'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS successful_dribbles_per_90,

            CASE
                WHEN SUM(
                    CASE
                        WHEN e.event_type = 'Dribble'
                        THEN 1
                        ELSE 0
                    END
                ) > 0
                THEN
                    SUM(
                        CASE
                            WHEN e.event_type = 'Dribble'
                                 AND e.dribble_outcome = 'Complete'
                            THEN 1
                            ELSE 0
                        END
                    ) * 100.0
                    /
                    SUM(
                        CASE
                            WHEN e.event_type = 'Dribble'
                            THEN 1
                            ELSE 0
                        END
                    )
                ELSE 0
            END AS dribble_success_pct

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type IN (
            'Carry',
            'Dribble'
        )

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    duels AS (
        SELECT
            e.player_id,

            SUM(
                CASE
                    WHEN e.event_type = 'Duel'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS duels_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Duel'
                         AND e.duel_type = 'Aerial Lost'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS aerial_duels_lost_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type = 'Duel'

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    retention AS (
        SELECT
            e.player_id,

            SUM(
                CASE
                    WHEN e.event_type = 'Miscontrol'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS miscontrols_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Dispossessed'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS dispossessed_per_90,

            SUM(
                CASE
                    WHEN e.event_type = 'Ball Recovery'
                    THEN 1
                    ELSE 0
                END
            ) / (
                pm.total_minutes / 90.0
            ) AS ball_recoveries_per_90

        FROM events e

        JOIN (
            SELECT
                player_id,
                SUM(minutes_played) AS total_minutes
            FROM player_match
            GROUP BY player_id
        ) pm
            ON e.player_id = pm.player_id

        WHERE e.event_type IN (
            'Miscontrol',
            'Dispossessed',
            'Ball Recovery'
        )

        GROUP BY
            e.player_id,
            pm.total_minutes
    ),

    raw_features AS (

        SELECT
            p.player_id,
            p.player_name,
            pm.total_minutes,

            pr.primary_position,
            pr.position_share_pct,
            pr.role_group,

            COALESCE(a.shots_per_90, 0) AS shots_per_90,
            COALESCE(a.xg_per_90, 0) AS xg_per_90,
            COALESCE(a.goals_per_90, 0) AS goals_per_90,

            COALESCE(cc.key_passes_per_90, 0)
                AS key_passes_per_90,

            COALESCE(cc.assists_per_90, 0)
                AS assists_per_90,

            COALESCE(pa.passes_per_90, 0)
                AS passes_per_90,

            COALESCE(pa.completed_passes_per_90, 0)
                AS completed_passes_per_90,

            COALESCE(pa.pass_distance_per_90, 0)
                AS pass_distance_per_90,

            COALESCE(d.pressures_per_90, 0)
                AS pressures_per_90,

            COALESCE(d.tackles_per_90, 0)
                AS tackles_per_90,

            COALESCE(d.interceptions_per_90, 0)
                AS interceptions_per_90,

            COALESCE(d.clearances_per_90, 0)
                AS clearances_per_90,

            COALESCE(c.carries_per_90, 0)
                AS carries_per_90,

            COALESCE(c.dribbles_per_90, 0)
                AS dribbles_per_90,

            COALESCE(c.successful_dribbles_per_90, 0)
                AS successful_dribbles_per_90,

            COALESCE(c.dribble_success_pct, 0)
                AS dribble_success_pct,

            COALESCE(du.duels_per_90, 0)
                AS duels_per_90,

            COALESCE(du.aerial_duels_lost_per_90, 0)
                AS aerial_duels_lost_per_90,

            COALESCE(r.miscontrols_per_90, 0)
                AS miscontrols_per_90,

            COALESCE(r.dispossessed_per_90, 0)
                AS dispossessed_per_90,

            COALESCE(r.ball_recoveries_per_90, 0)
                AS ball_recoveries_per_90

        FROM player_minutes pm

        JOIN players p
            ON pm.player_id = p.player_id

        JOIN player_roles pr
            ON pm.player_id = pr.player_id

        LEFT JOIN attacking a
            ON pm.player_id = a.player_id

        LEFT JOIN chance_creation cc
            ON pm.player_id = cc.player_id

        LEFT JOIN passing pa
            ON pm.player_id = pa.player_id

        LEFT JOIN defensive d
            ON pm.player_id = d.player_id

        LEFT JOIN carrying c
            ON pm.player_id = c.player_id

        LEFT JOIN duels du
            ON pm.player_id = du.player_id

        LEFT JOIN retention r
            ON pm.player_id = r.player_id

        WHERE pm.total_minutes >= 900
    ),

    percentiles AS (

        SELECT
            *,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY xg_per_90
            ) * 100 AS xg_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY goals_per_90
            ) * 100 AS goals_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY shots_per_90
            ) * 100 AS shots_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY key_passes_per_90
            ) * 100 AS key_passes_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY assists_per_90
            ) * 100 AS assists_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY passes_per_90
            ) * 100 AS passes_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY completed_passes_per_90
            ) * 100 AS completed_passes_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY pass_distance_per_90
            ) * 100 AS pass_distance_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY pressures_per_90
            ) * 100 AS pressures_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY tackles_per_90
            ) * 100 AS tackles_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY interceptions_per_90
            ) * 100 AS interceptions_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY clearances_per_90
            ) * 100 AS clearances_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY carries_per_90
            ) * 100 AS carries_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY dribbles_per_90
            ) * 100 AS dribbles_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY successful_dribbles_per_90
            ) * 100 AS successful_dribbles_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY dribble_success_pct
            ) * 100 AS dribble_success_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY duels_per_90
            ) * 100 AS duels_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY aerial_duels_lost_per_90 DESC
            ) * 100 AS aerial_duels_lost_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY miscontrols_per_90 DESC
            ) * 100 AS miscontrols_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY dispossessed_per_90 DESC
            ) * 100 AS dispossessed_percentile,

            PERCENT_RANK() OVER (
                PARTITION BY role_group
                ORDER BY ball_recoveries_per_90
            ) * 100 AS ball_recoveries_percentile

        FROM raw_features
    ),

    profiles AS (

        SELECT
            *,

            (
                xg_percentile
                + goals_percentile
                + shots_percentile
            ) / 3.0 AS shooting_profile,

            (
                key_passes_percentile
                + assists_percentile
            ) / 2.0 AS chance_creation_profile,

            (
                passes_percentile
                + completed_passes_percentile
                + pass_distance_percentile
            ) / 3.0 AS passing_profile,

            (
                pressures_percentile
                + tackles_percentile
                + interceptions_percentile
                + clearances_percentile
            ) / 4.0 AS defensive_profile,

            (
                carries_percentile
                + dribbles_percentile
                + successful_dribbles_percentile
                + dribble_success_percentile
            ) / 4.0 AS carrying_profile,

            (
                duels_percentile
                + aerial_duels_lost_percentile
            ) / 2.0 AS duel_profile,

            (
                miscontrols_percentile
                + dispossessed_percentile
                + ball_recoveries_percentile
            ) / 3.0 AS retention_recovery_profile

        FROM percentiles
    )

    SELECT *
    FROM profiles
),

scored AS (

    SELECT
        *,

        CASE

            /*
                Goalkeeper
                Emphasis:
                - Defensive activity
                - Passing
                - Recovery
            */
            WHEN role_group = 'Goalkeeper'
                THEN
                    defensive_profile * 0.40
                    + passing_profile * 0.30
                    + retention_recovery_profile * 0.30

            /*
                Centre Back
                Emphasis:
                - Defensive work
                - Duels
                - Passing
            */
            WHEN role_group = 'Centre Back'
                THEN
                    defensive_profile * 0.40
                    + duel_profile * 0.30
                    + passing_profile * 0.30

            /*
                Full Back
                Balanced defensive and attacking/carrying profile.
            */
            WHEN role_group = 'Full Back'
                THEN
                    defensive_profile * 0.30
                    + passing_profile * 0.20
                    + carrying_profile * 0.25
                    + chance_creation_profile * 0.15
                    + retention_recovery_profile * 0.10

            /*
                Defensive Midfielder
                Emphasis:
                - Defensive activity
                - Passing
                - Recovery
            */
            WHEN role_group = 'Defensive Midfielder'
                THEN
                    defensive_profile * 0.35
                    + passing_profile * 0.30
                    + retention_recovery_profile * 0.20
                    + duel_profile * 0.15

            /*
                Central Midfielder
                Emphasis:
                - Passing
                - Carrying
                - Chance creation
                - Defensive contribution
            */
            WHEN role_group = 'Central Midfielder'
                THEN
                    passing_profile * 0.30
                    + carrying_profile * 0.20
                    + chance_creation_profile * 0.20
                    + defensive_profile * 0.20
                    + retention_recovery_profile * 0.10

            /*
                Attacking Midfielder
                Emphasis:
                - Chance creation
                - Shooting
                - Passing
                - Carrying
            */
            WHEN role_group = 'Attacking Midfielder'
                THEN
                    chance_creation_profile * 0.35
                    + shooting_profile * 0.30
                    + passing_profile * 0.20
                    + carrying_profile * 0.15

            /*
                Winger
                Emphasis:
                - Attacking output
                - Chance creation
                - Carrying
            */
            WHEN role_group = 'Winger'
                THEN
                    shooting_profile * 0.30
                    + chance_creation_profile * 0.30
                    + carrying_profile * 0.30
                    + passing_profile * 0.10

            /*
                Forward
                Emphasis:
                - Shooting
                - Chance creation
                - Duels
            */
            WHEN role_group = 'Forward'
                THEN
                    shooting_profile * 0.50
                    + chance_creation_profile * 0.20
                    + duel_profile * 0.20
                    + retention_recovery_profile * 0.10

            ELSE NULL

        END AS scouting_score

    FROM scouting_profiles
)

SELECT
    player_id,
    player_name,
    ROUND(total_minutes, 2) AS total_minutes,
    primary_position,
    ROUND(position_share_pct, 2) AS position_share_pct,
    role_group,

    ROUND(shooting_profile, 2) AS shooting_profile,
    ROUND(chance_creation_profile, 2) AS chance_creation_profile,
    ROUND(passing_profile, 2) AS passing_profile,
    ROUND(defensive_profile, 2) AS defensive_profile,
    ROUND(carrying_profile, 2) AS carrying_profile,
    ROUND(duel_profile, 2) AS duel_profile,
    ROUND(retention_recovery_profile, 2)
        AS retention_recovery_profile,

    ROUND(scouting_score, 2) AS scouting_score,

    RANK() OVER (
        PARTITION BY role_group
        ORDER BY scouting_score DESC
    ) AS role_rank

FROM scored

ORDER BY
    role_group,
    role_rank;

-- ============================================================
-- QUERY 51 — Player Similarity Feature Matrix
-- ============================================================

WITH player_minutes AS (
    SELECT
        player_id,
        SUM(minutes_played) AS total_minutes
    FROM player_match
    GROUP BY player_id
),

player_events AS (
    SELECT
        player_id,

        -- Attacking
        SUM(CASE WHEN event_type = 'Shot' THEN 1 ELSE 0 END) AS shots,
        SUM(CASE WHEN event_type = 'Shot'
                 THEN COALESCE(shot_xg, 0)
                 ELSE 0 END) AS expected_goals,
        SUM(CASE WHEN event_type = 'Shot'
                  AND shot_outcome = 'Goal'
                 THEN 1 ELSE 0 END) AS goals,

        -- Passing
        SUM(CASE WHEN event_type = 'Pass' THEN 1 ELSE 0 END) AS passes,

        SUM(
            CASE
                WHEN event_type = 'Pass'
                 AND (pass_outcome IS NULL OR pass_outcome = '')
                THEN 1

                WHEN event_type = 'Pass'
                 AND pass_outcome IS NOT NULL
                 AND pass_outcome NOT IN (
                     'Incomplete',
                     'Out',
                     'Unknown',
                     'Injury Clearance'
                 )
                THEN 1

                ELSE 0
            END
        ) AS completed_passes,

        SUM(
            CASE
                WHEN event_type = 'Pass'
                THEN COALESCE(pass_length, 0)
                ELSE 0
            END
        ) AS pass_distance,

        -- Defensive activity
        SUM(CASE WHEN event_type = 'Pressure' THEN 1 ELSE 0 END) AS pressures,

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
                WHEN event_type = 'Clearance'
                THEN 1
                ELSE 0
            END
        ) AS clearances,

        -- Carrying / dribbling
        SUM(CASE WHEN event_type = 'Carry' THEN 1 ELSE 0 END) AS carries,

        SUM(CASE WHEN event_type = 'Dribble' THEN 1 ELSE 0 END) AS dribbles,

        SUM(
            CASE
                WHEN event_type = 'Dribble'
                 AND dribble_outcome = 'Complete'
                THEN 1
                ELSE 0
            END
        ) AS successful_dribbles,

        -- Duels
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
        ) AS aerial_duels_lost,

        -- Retention / recovery
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
                WHEN event_type = 'Ball Recovery'
                THEN 1
                ELSE 0
            END
        ) AS ball_recoveries,

        -- Key passes
        SUM(
            CASE
                WHEN event_type = 'Shot'
                 AND shot_key_pass_id IS NOT NULL
                THEN 1
                ELSE 0
            END
        ) AS key_pass_events
    FROM events
    WHERE player_id IS NOT NULL
    GROUP BY player_id
),

player_key_passes AS (
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
        AND pass_event.player_id IS NOT NULL
    GROUP BY
        pass_event.player_id
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
        AND pass_event.player_id IS NOT NULL
    GROUP BY
        pass_event.player_id
)

SELECT
    p.player_id,
    p.player_name,
    ROUND(pm.total_minutes, 2) AS total_minutes,

    -- Attacking
    ROUND(
        COALESCE(pe.shots, 0) / (pm.total_minutes / 90.0),
        4
    ) AS shots_per_90,

    ROUND(
        COALESCE(pe.expected_goals, 0) / (pm.total_minutes / 90.0),
        4
    ) AS xg_per_90,

    ROUND(
        COALESCE(pe.goals, 0) / (pm.total_minutes / 90.0),
        4
    ) AS goals_per_90,

    -- Chance creation
    ROUND(
        COALESCE(pk.key_passes, 0) / (pm.total_minutes / 90.0),
        4
    ) AS key_passes_per_90,

    ROUND(
        COALESCE(pa.assists, 0) / (pm.total_minutes / 90.0),
        4
    ) AS assists_per_90,

    -- Passing
    ROUND(
        COALESCE(pe.passes, 0) / (pm.total_minutes / 90.0),
        4
    ) AS passes_per_90,

    ROUND(
        COALESCE(pe.completed_passes, 0) / (pm.total_minutes / 90.0),
        4
    ) AS completed_passes_per_90,

    ROUND(
        COALESCE(pe.pass_distance, 0) / (pm.total_minutes / 90.0),
        4
    ) AS pass_distance_per_90,

    -- Defensive
    ROUND(
        COALESCE(pe.pressures, 0) / (pm.total_minutes / 90.0),
        4
    ) AS pressures_per_90,

    ROUND(
        COALESCE(pe.tackles, 0) / (pm.total_minutes / 90.0),
        4
    ) AS tackles_per_90,

    ROUND(
        COALESCE(pe.interceptions, 0) / (pm.total_minutes / 90.0),
        4
    ) AS interceptions_per_90,

    ROUND(
        COALESCE(pe.clearances, 0) / (pm.total_minutes / 90.0),
        4
    ) AS clearances_per_90,

    -- Carrying
    ROUND(
        COALESCE(pe.carries, 0) / (pm.total_minutes / 90.0),
        4
    ) AS carries_per_90,

    ROUND(
        COALESCE(pe.dribbles, 0) / (pm.total_minutes / 90.0),
        4
    ) AS dribbles_per_90,

    ROUND(
        COALESCE(pe.successful_dribbles, 0) / (pm.total_minutes / 90.0),
        4
    ) AS successful_dribbles_per_90,

    -- Duels
    ROUND(
        COALESCE(pe.duels, 0) / (pm.total_minutes / 90.0),
        4
    ) AS duels_per_90,

    ROUND(
        COALESCE(pe.aerial_duels_lost, 0) / (pm.total_minutes / 90.0),
        4
    ) AS aerial_duels_lost_per_90,

    -- Retention / recovery
    ROUND(
        COALESCE(pe.miscontrols, 0) / (pm.total_minutes / 90.0),
        4
    ) AS miscontrols_per_90,

    ROUND(
        COALESCE(pe.dispossessed, 0) / (pm.total_minutes / 90.0),
        4
    ) AS dispossessed_per_90,

    ROUND(
        COALESCE(pe.ball_recoveries, 0) / (pm.total_minutes / 90.0),
        4
    ) AS ball_recoveries_per_90

FROM player_minutes pm

JOIN players p
    ON pm.player_id = p.player_id

LEFT JOIN player_events pe
    ON pm.player_id = pe.player_id

LEFT JOIN player_key_passes pk
    ON pm.player_id = pk.player_id

LEFT JOIN player_assists pa
    ON pm.player_id = pa.player_id

WHERE
    pm.total_minutes >= 900

ORDER BY
    p.player_name;