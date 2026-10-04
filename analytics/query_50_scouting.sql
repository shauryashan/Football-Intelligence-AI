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