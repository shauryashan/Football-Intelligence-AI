import sys
import sqlite3
from pathlib import Path
from textwrap import dedent

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Football Intelligence AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATABASE_FILE = (
    PROJECT_ROOT
    / "database"
    / "football.db"
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       GLOBAL
    -------------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at 85% 5%,
                rgba(30, 90, 70, 0.18),
                transparent 30%
            ),
            radial-gradient(
                circle at 10% 30%,
                rgba(20, 70, 90, 0.12),
                transparent 25%
            ),
            #070b0f;
        color: #f4f7f8;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }


    /* --------------------------------------------------------
       SIDEBAR
    -------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background: #080d12;
        border-right: 1px solid rgba(255,255,255,0.07);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }

    .sidebar-brand {
        padding: 0 0.5rem 1.8rem 0.5rem;
    }

    .sidebar-logo {
        font-size: 1.9rem;
        font-weight: 800;
        letter-spacing: -0.05em;
    }

    .sidebar-subtitle {
        color: #7f8b94;
        font-size: 0.78rem;
        margin-top: 0.25rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }


    /* --------------------------------------------------------
       HERO
    -------------------------------------------------------- */

    .hero {
        position: relative;
        overflow: hidden;
        min-height: 330px;
        padding: 3.2rem 3.5rem;
        border-radius: 28px;
        border: 1px solid rgba(255,255,255,0.08);

        background:
            linear-gradient(
                115deg,
                rgba(12, 27, 25, 0.98),
                rgba(8, 17, 23, 0.96)
            );

        box-shadow:
            0 25px 80px rgba(0,0,0,0.35);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 420px;
        height: 420px;
        right: -100px;
        top: -150px;
        border-radius: 50%;
        background:
            radial-gradient(
                circle,
                rgba(70, 170, 120, 0.18),
                transparent 65%
            );
    }

    .hero-eyebrow {
        position: relative;
        z-index: 2;
        color: #65d6a0;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    .hero-title {
        position: relative;
        z-index: 2;
        font-size: clamp(2.5rem, 5vw, 5rem);
        line-height: 0.95;
        font-weight: 900;
        letter-spacing: -0.065em;
        margin: 0;
        max-width: 850px;
    }

    .hero-title span {
        color: #65d6a0;
    }

    .hero-description {
        position: relative;
        z-index: 2;
        color: #aab5bc;
        font-size: 1rem;
        line-height: 1.7;
        max-width: 650px;
        margin-top: 1.5rem;
    }

    .hero-badge {
        position: relative;
        z-index: 2;
        display: inline-block;
        margin-top: 1.5rem;
        padding: 0.55rem 0.9rem;
        border-radius: 999px;
        background: rgba(101,214,160,0.09);
        border: 1px solid rgba(101,214,160,0.18);
        color: #8ce2ba;
        font-size: 0.76rem;
        font-weight: 700;
    }


    /* --------------------------------------------------------
       SECTION HEADERS
    -------------------------------------------------------- */

    .section-label {
        color: #65d6a0;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-top: 3rem;
        margin-bottom: 0.4rem;
    }

    .section-title {
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -0.035em;
        margin-bottom: 1.4rem;
    }


    /* --------------------------------------------------------
       KPI CARDS
    -------------------------------------------------------- */

    .kpi-card {
        min-height: 145px;
        padding: 1.45rem;
        border-radius: 20px;
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.07);
        transition: transform 0.2s ease,
                    border-color 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(101,214,160,0.28);
    }

    .kpi-label {
        color: #7f8b94;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .kpi-value {
        font-size: 2.25rem;
        font-weight: 850;
        letter-spacing: -0.05em;
        margin-top: 0.55rem;
    }

    .kpi-note {
        color: #68757e;
        font-size: 0.76rem;
        margin-top: 0.35rem;
    }


    /* --------------------------------------------------------
       FEATURE CARDS
    -------------------------------------------------------- */

    .feature-card {
        min-height: 185px;
        padding: 1.7rem;
        border-radius: 22px;
        background: linear-gradient(
            145deg,
            rgba(255,255,255,0.045),
            rgba(255,255,255,0.018)
        );
        border: 1px solid rgba(255,255,255,0.07);
    }

    .feature-icon {
        font-size: 1.65rem;
        margin-bottom: 1rem;
    }

    .feature-title {
        font-size: 1.05rem;
        font-weight: 800;
        margin-bottom: 0.55rem;
    }

    .feature-description {
        color: #7f8b94;
        font-size: 0.82rem;
        line-height: 1.55;
    }


    /* --------------------------------------------------------
       TABLE
    -------------------------------------------------------- */

    .scout-table {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.07);
    }


    /* --------------------------------------------------------
       FOOTER
    -------------------------------------------------------- */

    .footer {
        margin-top: 5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255,255,255,0.07);
        color: #59656d;
        font-size: 0.72rem;
        text-align: center;
    }


    /* --------------------------------------------------------
       BUTTONS
    -------------------------------------------------------- */

    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        background: rgba(255,255,255,0.045);
        color: #f4f7f8;
        font-weight: 700;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: rgba(101,214,160,0.4);
        color: #65d6a0;
    }


    /* --------------------------------------------------------
       INPUTS
    -------------------------------------------------------- */

    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.035);
        border-color: rgba(255,255,255,0.08);
        border-radius: 12px;
    }

    /* --------------------------------------------------------
   PLAYER SCOUT
-------------------------------------------------------- */

.player-header {
    position: relative;
    overflow: hidden;
    padding: 2.5rem;
    border-radius: 26px;
    background:
        linear-gradient(
            135deg,
            rgba(17, 34, 31, 0.98),
            rgba(9, 17, 23, 0.98)
        );
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 1.5rem;
}

.player-header::after {
    content: "";
    position: absolute;
    width: 360px;
    height: 360px;
    right: -100px;
    top: -180px;
    border-radius: 50%;
    background:
        radial-gradient(
            circle,
            rgba(101,214,160,0.16),
            transparent 68%
        );
}

.player-kicker {
    position: relative;
    z-index: 2;
    color: #65d6a0;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.player-name {
    position: relative;
    z-index: 2;
    font-size: clamp(2.4rem, 5vw, 4.5rem);
    line-height: 1;
    font-weight: 900;
    letter-spacing: -0.065em;
    margin-top: 0.7rem;
}

.player-meta {
    position: relative;
    z-index: 2;
    color: #89969e;
    margin-top: 0.8rem;
    font-size: 0.9rem;
}

.player-stat-card {
    min-height: 135px;
    padding: 1.4rem;
    border-radius: 19px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
}

.player-stat-label {
    color: #77848c;
    font-size: 0.68rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.player-stat-value {
    font-size: 2rem;
    font-weight: 850;
    letter-spacing: -0.05em;
    margin-top: 0.45rem;
}

.player-stat-note {
    color: #68757e;
    font-size: 0.72rem;
    margin-top: 0.25rem;
}

.role-pill {
    display: inline-block;
    padding: 0.45rem 0.75rem;
    border-radius: 999px;
    background: rgba(101,214,160,0.1);
    border: 1px solid rgba(101,214,160,0.2);
    color: #8ce2ba;
    font-size: 0.7rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.scout-section {
    margin-top: 2.5rem;
}

.similar-card {
    padding: 1.3rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
}

.similar-name {
    font-weight: 800;
    font-size: 0.95rem;
}

.similar-role {
    color: #68757e;
    font-size: 0.7rem;
    margin-top: 0.25rem;
}

.similar-score {
    color: #65d6a0;
    font-size: 1.35rem;
    font-weight: 850;
    margin-top: 0.8rem;
}

.ai-result-card {
    padding: 1.5rem;
    border-radius: 20px;
    background:
        linear-gradient(
            135deg,
            rgba(101,214,160,0.07),
            rgba(255,255,255,0.025)
        );
    border: 1px solid rgba(101,214,160,0.14);
}

.similarity-hero {
    padding: 2rem;
    border-radius: 24px;
    background:
        linear-gradient(
            135deg,
            rgba(17, 34, 31, 0.98),
            rgba(9, 17, 23, 0.98)
        );
    border: 1px solid rgba(101,214,160,0.12);
    margin-bottom: 1.5rem;
}

.similarity-player {
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: -0.05em;
    margin-top: 0.4rem;
}

.similarity-description {
    color: #7f8b94;
    font-size: 0.85rem;
    margin-top: 0.5rem;
}

.similarity-rank-card {
    padding: 1.4rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
    min-height: 155px;
}

.similarity-rank {
    color: #59656d;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.1em;
}

.similarity-player-name {
    font-size: 1rem;
    font-weight: 850;
    margin-top: 0.6rem;
}

.similarity-role-text {
    color: #68757e;
    font-size: 0.7rem;
    margin-top: 0.3rem;
}

.similarity-percentage {
    color: #65d6a0;
    font-size: 1.65rem;
    font-weight: 900;
    margin-top: 0.8rem;
}

.similarity-note {
    color: #59656d;
    font-size: 0.68rem;
    margin-top: 0.25rem;
}

.archetype-hero {
    padding: 2rem;
    border-radius: 24px;
    background:
        linear-gradient(
            135deg,
            rgba(17, 34, 31, 0.98),
            rgba(9, 17, 23, 0.98)
        );
    border: 1px solid rgba(101,214,160,0.12);
    margin-bottom: 1.5rem;
}

.archetype-name {
    font-size: 2.4rem;
    font-weight: 900;
    letter-spacing: -0.05em;
    margin-top: 0.5rem;
}

.archetype-description {
    color: #7f8b94;
    font-size: 0.85rem;
    line-height: 1.6;
    max-width: 750px;
    margin-top: 0.7rem;
}

.prediction-hero {
    padding: 2.2rem;
    border-radius: 24px;
    background:
        linear-gradient(
            135deg,
            rgba(17, 34, 31, 0.98),
            rgba(9, 17, 23, 0.98)
        );
    border: 1px solid rgba(101,214,160,0.14);
    margin-bottom: 1.5rem;
}

.prediction-value {
    font-size: 4.5rem;
    line-height: 1;
    font-weight: 900;
    letter-spacing: -0.07em;
    margin-top: 0.5rem;
    color: #65d6a0;
}

.prediction-unit {
    color: #7f8b94;
    font-size: 0.85rem;
    margin-top: 0.7rem;
}

.prediction-model-card {
    padding: 1.5rem;
    border-radius: 20px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
    min-height: 150px;
}

.prediction-model-title {
    font-size: 0.9rem;
    font-weight: 850;
}

.prediction-model-text {
    color: #7f8b94;
    font-size: 0.76rem;
    line-height: 1.6;
    margin-top: 0.5rem;
}

.ai-analyst-hero {
    padding: 2.2rem;
    border-radius: 24px;
    background:
        linear-gradient(
            135deg,
            rgba(17, 34, 31, 0.98),
            rgba(9, 17, 23, 0.98)
        );
    border: 1px solid rgba(101,214,160,0.14);
    margin-bottom: 1.5rem;
}

.ai-analyst-title {
    font-size: 2.3rem;
    font-weight: 900;
    letter-spacing: -0.05em;
    margin-top: 0.4rem;
}

.ai-analyst-description {
    color: #7f8b94;
    font-size: 0.85rem;
    line-height: 1.6;
    max-width: 750px;
    margin-top: 0.7rem;
}

.chat-user {
    padding: 1rem 1.2rem;
    border-radius: 16px;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.07);
    margin: 0.8rem 0;
}

.chat-assistant {
    padding: 1.2rem;
    border-radius: 18px;
    background:
        linear-gradient(
            135deg,
            rgba(101,214,160,0.07),
            rgba(255,255,255,0.025)
        );
    border: 1px solid rgba(101,214,160,0.12);
    margin: 0.8rem 0;
}

.match-hero {
    padding: 2.2rem;
    border-radius: 24px;
    background:
        linear-gradient(
            135deg,
            rgba(17, 34, 31, 0.98),
            rgba(9, 17, 23, 0.98)
        );
    border: 1px solid rgba(101,214,160,0.14);
    margin-bottom: 1.5rem;
}

.match-result {
    font-size: 2.5rem;
    font-weight: 900;
    letter-spacing: -0.05em;
    margin-top: 0.5rem;
}

.probability-card {
    padding: 1.5rem;
    border-radius: 20px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
    text-align: center;
}

.probability-value {
    font-size: 2rem;
    font-weight: 900;
    margin-top: 0.5rem;
}

.probability-label {
    color: #7f8b94;
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.archetype-cluster {
    color: #65d6a0;
    font-size: 0.8rem;
    font-weight: 800;
    margin-top: 1rem;
}

/* --------------------------------------------------------
   AI ANALYST MARKDOWN RESPONSE
-------------------------------------------------------- */

.ai-analyst-response {
    color: #dce4e8;
    font-size: 0.95rem;
    line-height: 1.75;
}

.ai-analyst-response h1,
.ai-analyst-response h2,
.ai-analyst-response h3 {
    color: #f4f7f8;
    margin-top: 1.2rem;
    margin-bottom: 0.5rem;
}

.ai-analyst-response strong {
    color: #ffffff;
}

.ai-analyst-response ol,
.ai-analyst-response ul {
    margin-top: 0.4rem;
    margin-bottom: 0.8rem;
    padding-left: 1.5rem;
}

.ai-analyst-response li {
    margin-bottom: 0.35rem;
}

    /* --------------------------------------------------------
       SCOUTING SCORE
    -------------------------------------------------------- */

    .score-card {
        min-height: 190px;
        padding: 1.6rem;
        border-radius: 22px;
        background: linear-gradient(
            145deg,
            rgba(101,214,160,0.10),
            rgba(255,255,255,0.025)
        );
        border: 1px solid rgba(101,214,160,0.18);
    }

    .score-value {
        font-size: 4rem;
        line-height: 0.95;
        font-weight: 900;
        letter-spacing: -0.07em;
        margin-top: 0.6rem;
    }

    .score-rank {
        color: #8ce2ba;
        font-size: 0.82rem;
        font-weight: 700;
        margin-top: 0.55rem;
    }

    .profile-card {
        padding: 1.25rem 1.35rem;
        margin-bottom: 0.75rem;
        border-radius: 16px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
    }

    .profile-card-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
    }

    .profile-name {
        font-size: 0.82rem;
        font-weight: 800;
        color: #dce4e8;
    }

    .profile-value {
        font-size: 0.82rem;
        font-weight: 800;
        color: #65d6a0;
    }

    .profile-track {
        height: 7px;
        margin-top: 0.7rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.07);
        overflow: hidden;
    }

    .profile-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #2d8f69, #65d6a0);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HTML HELPER
# ============================================================

def render_html(html):
    st.html(dedent(html))


# ============================================================
# DATABASE HELPERS
# ============================================================

@st.cache_resource
def get_connection():

    return sqlite3.connect(
        DATABASE_FILE,
        check_same_thread=False
    )


@st.cache_data
def get_dataset_stats():

    connection = get_connection()

    stats = {}

    stats["players"] = pd.read_sql_query(
        """
        SELECT COUNT(*) AS count
        FROM players
        """,
        connection
    ).iloc[0]["count"]

    stats["teams"] = pd.read_sql_query(
        """
        SELECT COUNT(*) AS count
        FROM teams
        """,
        connection
    ).iloc[0]["count"]

    stats["matches"] = pd.read_sql_query(
        """
        SELECT COUNT(*) AS count
        FROM matches
        """,
        connection
    ).iloc[0]["count"]

    stats["events"] = pd.read_sql_query(
        """
        SELECT COUNT(*) AS count
        FROM events
        """,
        connection
    ).iloc[0]["count"]

    return stats


@st.cache_data
def get_top_scouting_players():

    connection = get_connection()

    query = """
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

            SUM(
                CASE
                    WHEN event_type = 'Shot'
                    THEN 1 ELSE 0
                END
            ) AS shots,

            SUM(
                CASE
                    WHEN event_type = 'Shot'
                    THEN COALESCE(shot_xg, 0)
                    ELSE 0
                END
            ) AS xg,

            SUM(
                CASE
                    WHEN event_type = 'Pass'
                    THEN 1 ELSE 0
                END
            ) AS passes,

            SUM(
                CASE
                    WHEN event_type = 'Pressure'
                    THEN 1 ELSE 0
                END
            ) AS pressures

        FROM events

        WHERE player_id IS NOT NULL

        GROUP BY player_id
    )

    SELECT
        p.player_name,
        pm.total_minutes,
        pe.shots,
        pe.xg,
        pe.passes,
        pe.pressures

    FROM players p

    JOIN player_minutes pm
        ON p.player_id = pm.player_id

    LEFT JOIN player_events pe
        ON p.player_id = pe.player_id

    WHERE pm.total_minutes >= 900

    ORDER BY
        pe.xg DESC

    LIMIT 10;
    """

    return pd.read_sql_query(
        query,
        connection
    )

@st.cache_data
def get_player_list():

    connection = get_connection()

    return pd.read_sql_query(
        """
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

        HAVING
            SUM(pm.minutes_played) >= 900

        ORDER BY
            p.player_name
        """,
        connection
    )


@st.cache_data
def get_player_profile(player_name):

    connection = get_connection()

    query = """
    WITH player_minutes AS (

        SELECT
            player_id,
            SUM(minutes_played) AS total_minutes
        FROM player_match
        WHERE minutes_played > 0
        GROUP BY player_id
    ),

    primary_position AS (

        SELECT
            player_id,
            position,
            SUM(minutes_played) AS position_minutes,

            ROW_NUMBER() OVER (
                PARTITION BY player_id
                ORDER BY
                    SUM(minutes_played) DESC
            ) AS rn

        FROM player_match

        WHERE
            minutes_played > 0
            AND position IS NOT NULL

        GROUP BY
            player_id,
            position
    ),

    event_stats AS (

        SELECT
            player_id,

            SUM(
                CASE
                    WHEN event_type = 'Shot'
                    THEN 1 ELSE 0
                END
            ) AS shots,

            SUM(
                CASE
                    WHEN event_type = 'Shot'
                    THEN COALESCE(shot_xg, 0)
                    ELSE 0
                END
            ) AS xg,

            SUM(
                CASE
                    WHEN event_type = 'Pass'
                    THEN 1 ELSE 0
                END
            ) AS passes,

            SUM(
                CASE
                    WHEN event_type = 'Pressure'
                    THEN 1 ELSE 0
                END
            ) AS pressures,

            SUM(
                CASE
                    WHEN event_type = 'Carry'
                    THEN 1 ELSE 0
                END
            ) AS carries,

            SUM(
                CASE
                    WHEN event_type = 'Dribble'
                    THEN 1 ELSE 0
                END
            ) AS dribbles,

            SUM(
                CASE
                    WHEN event_type = 'Interception'
                    THEN 1 ELSE 0
                END
            ) AS interceptions,

            SUM(
                CASE
                    WHEN event_type = 'Clearance'
                    THEN 1 ELSE 0
                END
            ) AS clearances,

            SUM(
                CASE
                    WHEN event_type = 'Ball Recovery'
                    THEN 1 ELSE 0
                END
            ) AS ball_recoveries

        FROM events

        WHERE player_id IS NOT NULL

        GROUP BY player_id
    )

    SELECT

        p.player_id,
        p.player_name,
        p.country,

        pm.total_minutes,

        pp.position AS primary_position,

        es.shots,
        es.xg,
        es.passes,
        es.pressures,
        es.carries,
        es.dribbles,
        es.interceptions,
        es.clearances,
        es.ball_recoveries

    FROM players p

    JOIN player_minutes pm
        ON p.player_id = pm.player_id

    LEFT JOIN primary_position pp
        ON p.player_id = pp.player_id
        AND pp.rn = 1

    LEFT JOIN event_stats es
        ON p.player_id = es.player_id

    WHERE
        LOWER(p.player_name) = LOWER(?)
    """

    result = pd.read_sql_query(
        query,
        connection,
        params=[player_name]
    )

    if result.empty:
        return None

    return result.iloc[0].to_dict()


@st.cache_data
def get_scouting_profiles():
    """Load the authoritative Query 50 scouting profiles."""

    sql_file = (
        PROJECT_ROOT
        / "analytics"
        / "query_50_scouting.sql"
    )

    if not sql_file.exists():
        raise FileNotFoundError(
            f"Scouting SQL file not found: {sql_file}"
        )

    query_text = sql_file.read_text(
        encoding="utf-8"
    ).strip()

    # Remove a trailing semicolon if present.
    query_text = query_text.rstrip(";").strip()

    connection = get_connection()

    return pd.read_sql_query(
        query_text,
        connection
    )

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">⚽ FIA</div>
            <div class="sidebar-subtitle">
                Football Intelligence AI
            </div>
        </div>
        """
    )

    page = st.radio(
        "Navigate",
        [
            "Dashboard",
            "Player Scout",
            "Similar Players",
            "Player Archetype",
            "Performance Prediction",
            "Match Intelligence",
            "AI Analyst",
            "Knowledge Base",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    st.caption(
        "DATASET"
    )

    st.markdown(
        "**Premier League 2015/16**"
    )

    st.caption(
        "StatsBomb Open Data"
    )

    st.markdown("---")

    st.caption(
        "SYSTEM"
    )

    st.caption(
        "Analytics • ML • RAG • Agentic AI"
    )


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    stats = get_dataset_stats()


    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    render_html(
        """
        <div class="hero">

            <div class="hero-eyebrow">
                FOOTBALL INTELLIGENCE PLATFORM
            </div>

            <h1 class="hero-title">
                See the game<br>
                <span>through data.</span>
            </h1>

            <div class="hero-description">
                A football analytics and AI platform combining
                event-level data, statistical scouting,
                machine learning, retrieval-augmented generation,
                and agentic AI.
            </div>

            <div class="hero-badge">
                PREMIER LEAGUE • 2015/16 • STATSBOMB
            </div>

        </div>
        """
    )


    # --------------------------------------------------------
    # DATASET OVERVIEW
    # --------------------------------------------------------

    render_html(
        """
        <div class="section-label">
            DATASET
        </div>
        """
    )

    render_html(
        """
        <div class="section-title">
            The numbers behind the platform
        </div>
        """
    )


    kpi_columns = st.columns(4)


    kpis = [
        (
            "Players",
            f"{int(stats['players']):,}",
            "Scouting population: 644"
        ),
        (
            "Teams",
            f"{int(stats['teams']):,}",
            "Premier League clubs"
        ),
        (
            "Matches",
            f"{int(stats['matches']):,}",
            "2015/16 season"
        ),
        (
            "Events",
            f"{int(stats['events']):,}",
            "StatsBomb event records"
        ),
    ]


    for column, (
        label,
        value,
        note
    ) in zip(
        kpi_columns,
        kpis
    ):

        with column:

            render_html(
                f"""
                <div class="kpi-card">

                    <div class="kpi-label">
                        {label}
                    </div>

                    <div class="kpi-value">
                        {value}
                    </div>

                    <div class="kpi-note">
                        {note}
                    </div>

                </div>
                """
            )


    # --------------------------------------------------------
    # PLATFORM FEATURES
    # --------------------------------------------------------

    render_html(
        """
        <div class="section-label">
            PLATFORM
        </div>
        """
    )

    render_html(
        """
        <div class="section-title">
            Football intelligence, end to end.
        </div>
        """
    )


    feature_columns = st.columns(3)


    features = [
        (
            "🔎",
            "Player Scout",
            "Explore role-aware scouting profiles, performance metrics and statistical rankings."
        ),
        (
            "🧬",
            "Player Similarity",
            "Discover players with similar statistical profiles using a 15-feature ML representation."
        ),
        (
            "🧠",
            "Player Archetypes",
            "Explore unsupervised player clusters and statistical football archetypes."
        ),
        (
            "📈",
            "Performance AI",
            "Forecast a player's total xG across their next five appearances."
        ),
        (
            "⚽",
            "Match Intelligence",
            "Evaluate historical match outcomes using the ML5 Random Forest model."
        ),
        (
            "🤖",
            "AI Analyst",
            "Ask natural-language football questions and let the agent orchestrate specialized tools."
        ),
    ]


    for column, feature in zip(
        feature_columns,
        features[:3]
    ):

        with column:

            icon, title, description = feature

            render_html(
                f"""
                <div class="feature-card">

                    <div class="feature-icon">
                        {icon}
                    </div>

                    <div class="feature-title">
                        {title}
                    </div>

                    <div class="feature-description">
                        {description}
                    </div>

                </div>
                """
            )


    feature_columns_2 = st.columns(3)


    for column, feature in zip(
        feature_columns_2,
        features[3:]
    ):

        with column:

            icon, title, description = feature

            render_html(
                f"""
                <div class="feature-card">

                    <div class="feature-icon">
                        {icon}
                    </div>

                    <div class="feature-title">
                        {title}
                    </div>

                    <div class="feature-description">
                        {description}
                    </div>

                </div>
                """
            )


    # --------------------------------------------------------
    # TOP SCOUTING PROFILES
    # --------------------------------------------------------

    render_html(
        """
        <div class="section-label">
            SCOUTING
        </div>
        """
    )

    render_html(
        """
        <div class="section-title">
            Featured statistical profiles
        </div>
        """
    )


    top_players = get_top_scouting_players()


    display_df = top_players.copy()

    display_df.columns = [
        "Player",
        "Minutes",
        "Shots",
        "xG",
        "Passes",
        "Pressures"
    ]

    display_df["Minutes"] = (
        display_df["Minutes"]
        .round(0)
        .astype(int)
    )

    display_df["xG"] = (
        display_df["xG"]
        .round(2)
    )


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # DATASET NOTE
    # --------------------------------------------------------

    render_html(
        """
        <div class="footer">
            Football Intelligence AI · Premier League 2015/16 ·
            StatsBomb Open Data · Analytics + ML + RAG + Agentic AI
        </div>
        """
    )


# ============================================================
# PLACEHOLDER PAGES
# ============================================================

elif page == "Player Scout":

    # ========================================================
    # PLAYER SCOUT
    # ========================================================

    render_html(
        """
        <div class="section-label">
            SCOUTING INTELLIGENCE
        </div>

        <div class="section-title">
            Player Scout
        </div>
        """
    )

    st.caption(
    "Explore validated 900+ minute scouting profiles, "
    "statistical similarity, player archetypes and ML projections."
    )


    # --------------------------------------------------------
    # PLAYER SEARCH
    # --------------------------------------------------------

    players = get_player_list()

    player_names = players["player_name"].tolist()

    selected_player = st.selectbox(
        "Search scouting profile",
        player_names,
        index=(
            player_names.index("Kevin De Bruyne")
            if "Kevin De Bruyne" in player_names
            else 0
        )
    )


    profile = get_player_profile(
        selected_player
    )

    try:
        scouting_profiles = get_scouting_profiles()
        scouting_row = scouting_profiles[
            scouting_profiles["player_id"] == profile["player_id"]
        ]
        scouting_data = (
            scouting_row.iloc[0].to_dict()
            if not scouting_row.empty
            else None
        )
    except Exception as error:
        scouting_data = None
        st.error(f"Scouting score unavailable: {error}")


    if profile is None:

        st.error(
            "Player profile could not be found."
        )

    else:

        # ----------------------------------------------------
        # PLAYER HEADER
        # ----------------------------------------------------

        render_html(
            f"""
            <div class="player-header">

                <div class="player-kicker">
                    PLAYER PROFILE
                </div>

                <div class="player-name">
                    {profile["player_name"]}
                </div>

                <div class="player-meta">
                    {profile["country"] or "Country unavailable"}
                    &nbsp; • &nbsp;
                    Premier League 2015/16
                </div>

            </div>
            """
        )


        # ----------------------------------------------------
        # AUTHORITATIVE SCOUTING SCORE
        # ----------------------------------------------------

        if scouting_data is not None:

            render_html(
                f"""
                <div class="scout-section">
                    <div class="section-label">ROLE-AWARE EVALUATION</div>
                </div>
                """
            )

            score_columns = st.columns(4)

            score_cards = [
                (
                    "Scouting Score",
                    f"{float(scouting_data['scouting_score']):.2f}",
                    "Role-aware composite"
                ),
                (
                    "Role Rank",
                    f"#{int(scouting_data['role_rank'])}",
                    f"Within {scouting_data['role_group']}"
                ),
                (
                    "Role",
                    str(scouting_data['role_group']),
                    "Analytical role"
                ),
                (
                    "Position Share",
                    f"{float(scouting_data['position_share_pct']):.1f}%",
                    "Primary-position exposure"
                ),
            ]

            for column, (label, value, note) in zip(score_columns, score_cards):
                with column:
                    render_html(
                        f"""
                        <div class="player-stat-card">
                            <div class="player-stat-label">{label}</div>
                            <div class="player-stat-value">{value}</div>
                            <div class="player-stat-note">{note}</div>
                        </div>
                        """
                    )

            render_html(
                f"""
                <div class="score-card">
                    <div class="player-kicker">SCOUTING SCORE</div>
                    <div class="score-value">{float(scouting_data['scouting_score']):.2f}</div>
                    <div class="score-rank">
                        #{int(scouting_data['role_rank'])} ranked in {scouting_data['role_group']}
                    </div>
                </div>
                """
            )

            render_html(
                """
                <div class="scout-section">
                    <div class="section-label">SCOUTING PROFILE</div>
                    <div class="section-title">Seven dimensions of performance</div>
                </div>
                """
            )

            dimensions = [
                ("Shooting", "shooting_profile"),
                ("Chance Creation", "chance_creation_profile"),
                ("Passing", "passing_profile"),
                ("Defensive", "defensive_profile"),
                ("Carrying", "carrying_profile"),
                ("Duels", "duel_profile"),
                ("Retention / Recovery", "retention_recovery_profile"),
            ]

            left, right = st.columns(2)

            for index, (label, key) in enumerate(dimensions):
                value = max(0.0, min(100.0, float(scouting_data[key])))
                column = left if index % 2 == 0 else right

                with column:
                    render_html(
                        f"""
                        <div class="profile-card">
                            <div class="profile-card-top">
                                <div class="profile-name">{label}</div>
                                <div class="profile-value">{value:.1f}</div>
                            </div>
                            <div class="profile-track">
                                <div class="profile-fill" style="width:{value:.1f}%"></div>
                            </div>
                        </div>
                        """
                    )

            st.caption(
                "Profile values are percentile-based comparisons within the player's analytical role."
            )


        # ----------------------------------------------------
        # BASIC PROFILE STATS
        # ----------------------------------------------------

        stat_columns = st.columns(4)

        profile_stats = [
            (
                "Primary Position",
                profile["primary_position"]
                or "Unknown",
                "Minutes-based"
            ),
            (
                "Minutes",
                f"{profile['total_minutes']:,.0f}",
                "Total exposure"
            ),
            (
                "Shots",
                f"{int(profile['shots'] or 0):,}",
                "Event volume"
            ),
            (
                "xG",
                f"{profile['xg'] or 0:.2f}",
                "Expected goals"
            ),
        ]


        for column, stat in zip(
            stat_columns,
            profile_stats
        ):

            with column:

                label, value, note = stat

                render_html(
                    f"""
                    <div class="player-stat-card">

                        <div class="player-stat-label">
                            {label}
                        </div>

                        <div class="player-stat-value">
                            {value}
                        </div>

                        <div class="player-stat-note">
                            {note}
                        </div>

                    </div>
                    """
                )


        # ----------------------------------------------------
        # EVENT PROFILE
        # ----------------------------------------------------

        render_html(
            """
            <div class="scout-section">

                <div class="section-label">
                    PERFORMANCE PROFILE
                </div>

                <div class="section-title">
                    Event activity
                </div>

            </div>
            """
        )


        event_df = pd.DataFrame(
            {
                "Metric": [
                    "Passes",
                    "Pressures",
                    "Carries",
                    "Dribbles",
                    "Interceptions",
                    "Clearances",
                    "Ball Recoveries",
                ],
                "Volume": [
                    profile["passes"] or 0,
                    profile["pressures"] or 0,
                    profile["carries"] or 0,
                    profile["dribbles"] or 0,
                    profile["interceptions"] or 0,
                    profile["clearances"] or 0,
                    profile["ball_recoveries"] or 0,
                ],
            }
        )


        st.bar_chart(
            event_df.set_index("Metric")
        )


        # ----------------------------------------------------
        # ML INTELLIGENCE
        # ----------------------------------------------------

        render_html(
            """
            <div class="scout-section">

                <div class="section-label">
                    MACHINE LEARNING
                </div>

                <div class="section-title">
                    What does the model see?
                </div>

            </div>
            """
        )


        ml_col1, ml_col2 = st.columns(2)


        # ----------------------------------------------------
        # ARCHETYPE
        # ----------------------------------------------------

        with ml_col1:

            try:

                from agent.tools.player_clustering_tool import (
                    player_clustering_tool
                )

                archetype = player_clustering_tool(
                    selected_player
                )

                if "error" not in archetype:

                    render_html(
                        f"""
                        <div class="ai-result-card">

                            <div class="player-kicker">
                                STATISTICAL ARCHETYPE
                            </div>

                            <h2>
                                {archetype["archetype"]}
                            </h2>

                            <p style="color:#7f8b94;">
                                Cluster {archetype["cluster"]}
                                from the project's
                                unsupervised K-Means model.
                            </p>

                        </div>
                        """
                    )

                else:

                    st.warning(
                        archetype["error"]
                    )

            except Exception as error:

                st.error(
                    f"Archetype unavailable: {error}"
                )


        # ----------------------------------------------------
        # FUTURE xG
        # ----------------------------------------------------

        with ml_col2:

            try:

                from agent.tools.player_performance_tool import (
                    predict_player_future_xg
                )

                prediction = predict_player_future_xg(
                    selected_player
                )

                if "prediction" in prediction:

                    render_html(
                        f"""
                        <div class="ai-result-card">

                            <div class="player-kicker">
                                PERFORMANCE AI
                            </div>

                            <div
                                style="
                                    font-size:2.8rem;
                                    font-weight:900;
                                    margin-top:0.4rem;
                                "
                            >
                                {prediction["prediction"]:.2f}
                            </div>

                            <div
                                style="
                                    color:#7f8b94;
                                    margin-top:0.2rem;
                                "
                            >
                                predicted total xG
                                across next 5 appearances
                            </div>

                        </div>
                        """
                    )

                else:

                    st.warning(
                        prediction.get(
                            "error",
                            "Prediction unavailable."
                        )
                    )

            except Exception as error:

                st.error(
                    f"Performance prediction unavailable: {error}"
                )


        # ----------------------------------------------------
        # SIMILAR PLAYERS
        # ----------------------------------------------------

        render_html(
            """
            <div class="scout-section">

                <div class="section-label">
                    PLAYER DISCOVERY
                </div>

                <div class="section-title">
                    Statistically similar players
                </div>

            </div>
            """
        )


        try:

            from agent.tools.player_similarity_tool import (
                find_similar_players_for_agent
            )

            similarity = find_similar_players_for_agent(
                selected_player,
                top_n=5
            )


            if "error" in similarity:

                st.warning(
                    similarity["error"]
                )

            else:

                similar_columns = st.columns(
                    len(similarity["results"])
                )


                for column, player in zip(
                    similar_columns,
                    similarity["results"]
                ):

                    with column:

                        render_html(
                            f"""
                            <div class="similar-card">

                                <div class="similar-name">
                                    {player["player_name"]}
                                </div>

                                <div class="similar-role">
                                    {player["role_group"]}
                                </div>

                                <div class="similar-score">
                                    {player["similarity"] * 100:.1f}%
                                </div>

                                <div class="similar-role">
                                    statistical similarity
                                </div>

                            </div>
                            """
                        )


        except Exception as error:

            st.error(
                f"Similarity analysis unavailable: {error}"
            )


        # ----------------------------------------------------
        # METHODOLOGY NOTE
        # ----------------------------------------------------

        st.markdown("")


        with st.expander(
            "How to interpret this profile"
        ):

            st.write(
                """
                This page combines observed historical event data
                with outputs from the project's machine-learning
                models.

                Statistical similarity represents similarity in
                the project's feature space, not identical playing
                style or tactical role.

                The archetype is an unsupervised statistical cluster,
                not a definitive tactical classification.

                Performance AI is a model prediction of total xG
                across the next five appearances and is not a
                guaranteed forecast.
                """
            )


elif page == "Similar Players":

    # ========================================================
    # SIMILAR PLAYERS
    # ========================================================

    render_html(
        """
        <div class="section-label">
            PLAYER DISCOVERY
        </div>

        <div class="section-title">
            Find statistically similar players
        </div>
        """
    )

    st.caption(
        "Compare players using the project's validated "
        "15-feature role-aware similarity model."
    )


    # --------------------------------------------------------
    # PLAYER SELECTION
    # --------------------------------------------------------

    players = get_player_list()

    player_names = players["player_name"].tolist()

    selected_player = st.selectbox(
        "Select a player",
        player_names,
        index=(
            player_names.index("Kevin De Bruyne")
            if "Kevin De Bruyne" in player_names
            else 0
        ),
        key="similarity_player_selector",
    )


    # --------------------------------------------------------
    # RUN SIMILARITY MODEL
    # --------------------------------------------------------

    try:

        from agent.tools.player_similarity_tool import (
            find_similar_players_for_agent
        )

        similarity = find_similar_players_for_agent(
            selected_player,
            top_n=5
        )


        if "error" in similarity:

            st.warning(
                similarity["error"]
            )

        else:

            player_name = similarity["player"]

            results = similarity["results"]

            # ------------------------------------------------
            # HERO
            # ------------------------------------------------

            render_html(
                f"""
                <div class="similarity-hero">

                    <div class="player-kicker">
                        ROLE-AWARE SIMILARITY
                    </div>

                    <div class="similarity-player">
                        {player_name}
                    </div>

                    <div class="similarity-description">
                        Statistical similarity is evaluated
                        against players in the same analytical
                        role using the project's 15-feature
                        ML representation.
                    </div>

                </div>
                """
            )


            # ------------------------------------------------
            # RESULTS
            # ------------------------------------------------

            render_html(
                """
                <div class="scout-section">

                    <div class="section-label">
                        RECOMMENDATIONS
                    </div>

                    <div class="section-title">
                        Top statistical matches
                    </div>

                </div>
                """
            )


            result_columns = st.columns(
                len(results)
            )


            for index, (
                column,
                player
            ) in enumerate(
                zip(
                    result_columns,
                    results
                )
            ):

                with column:

                    render_html(
                        f"""
                        <div class="similarity-rank-card">

                            <div class="similarity-rank">
                                MATCH #{index + 1}
                            </div>

                            <div class="similarity-player-name">
                                {player["player_name"]}
                            </div>

                            <div class="similarity-role-text">
                                {player["role_group"]}
                            </div>

                            <div class="similarity-percentage">
                                {player["similarity"] * 100:.1f}%
                            </div>

                            <div class="similarity-note">
                                cosine similarity
                            </div>

                        </div>
                        """
                    )


            # ------------------------------------------------
            # INTERPRETATION
            # ------------------------------------------------

            st.markdown("")

            with st.expander(
                "How to interpret similarity"
            ):

                st.write(
                    """
                    The model represents each player using
                    15 football performance features expressed
                    per 90 minutes.

                    Features are standardized before cosine
                    similarity is calculated.

                    Candidates are restricted to the same
                    analytical role as the selected player.

                    A higher similarity score means the player's
                    statistical feature vector is closer to the
                    selected player's vector.

                    This does not mean the players have identical
                    playing styles, tactical roles, or quality.
                    """
                )


    except Exception as error:

        st.error(
            f"Similarity analysis unavailable: {error}"
        )


elif page == "Player Archetype":

    # ========================================================
    # PLAYER ARCHETYPE
    # ========================================================

    render_html(
        """
        <div class="section-label">
            PLAYER INTELLIGENCE
        </div>

        <div class="section-title">
            Statistical Player Archetypes
        </div>
        """
    )

    st.caption(
        "Explore the statistical archetypes produced by the "
        "project's validated K-Means clustering model."
    )


    # --------------------------------------------------------
    # PLAYER SELECTION
    # --------------------------------------------------------

    players = get_player_list()

    player_names = players["player_name"].tolist()

    selected_player = st.selectbox(
        "Select a player",
        player_names,
        index=(
            player_names.index("Kevin De Bruyne")
            if "Kevin De Bruyne" in player_names
            else 0
        ),
        key="archetype_player_selector",
    )


    # --------------------------------------------------------
    # CLUSTER RESULT
    # --------------------------------------------------------

    try:

        from agent.tools.player_clustering_tool import (
            player_clustering_tool
        )

        archetype = player_clustering_tool(
            selected_player
        )


        if "error" in archetype:

            st.warning(
                archetype["error"]
            )

        else:

            cluster = archetype["cluster"]
            archetype_name = archetype["archetype"]


            # ------------------------------------------------
            # HERO
            # ------------------------------------------------

            render_html(
                f"""
                <div class="archetype-hero">

                    <div class="player-kicker">
                        UNSUPERVISED CLASSIFICATION
                    </div>

                    <div class="archetype-name">
                        {archetype_name}
                    </div>

                    <div class="archetype-cluster">
                        CLUSTER {cluster}
                    </div>

                    <div class="archetype-description">
                        {selected_player} is assigned to this
                        statistical archetype by the project's
                        K-Means clustering model based on their
                        15-feature performance representation.
                    </div>

                </div>
                """
            )


            # ------------------------------------------------
            # INTERPRETATION
            # ------------------------------------------------

            render_html(
                """
                <div class="scout-section">

                    <div class="section-label">
                        MODEL INTERPRETATION
                    </div>

                    <div class="section-title">
                        What this classification means
                    </div>

                </div>
                """
            )


            interpretation = {
                "Goalkeeper":
                    "A statistical cluster dominated by "
                    "goalkeepers, reflecting their distinct "
                    "event profile relative to outfield players.",

                "Finishing Forward":
                    "A cluster characterized by stronger "
                    "finishing and attacking-output features.",

                "Creative Attacker":
                    "A cluster characterized by stronger "
                    "chance creation, attacking involvement "
                    "and ball progression.",

                "Defensive Player":
                    "A cluster characterized by stronger "
                    "defensive activity, duels and defensive "
                    "event involvement.",

                "Two-Way / High-Volume":
                    "A cluster characterized by broad, "
                    "high-volume involvement across multiple "
                    "areas of the game.",
            }


            description = interpretation.get(
                archetype_name,
                "A statistical cluster identified from the "
                "player feature space."
            )


            render_html(
                f"""
                <div class="ai-result-card">

                    <div class="feature-title">
                        {archetype_name}
                    </div>

                    <div class="feature-description">
                        {description}
                    </div>

                </div>
                """
            )


            # ------------------------------------------------
            # METHODOLOGY
            # ------------------------------------------------

            st.markdown("")

            with st.expander(
                "How the archetype model works"
            ):

                st.write(
                    """
                    The clustering model uses the project's
                    validated 15-feature player representation.

                    Features are standardized before K-Means
                    clustering.

                    Multiple values of K were evaluated using
                    silhouette scores. K=5 was selected because
                    it provided strong quantitative separation
                    while also producing interpretable football
                    archetypes.

                    The resulting archetype labels are human-
                    readable interpretations of the clusters.
                    They were not learned as supervised labels.

                    Therefore, an archetype describes statistical
                    similarity within this dataset rather than
                    a definitive tactical role, player quality,
                    or playing style.
                    """
                )


    except Exception as error:

        st.error(
            f"Archetype analysis unavailable: {error}"
        )


elif page == "Performance Prediction":

    # ========================================================
    # PERFORMANCE PREDICTION
    # ========================================================

    render_html(
        """
        <div class="section-label">
            PERFORMANCE AI
        </div>

        <div class="section-title">
            Player Performance Prediction
        </div>
        """
    )

    st.caption(
        "Forecast a player's total expected goals across "
        "their next five appearances."
    )


    # --------------------------------------------------------
    # PLAYER SELECTION
    # --------------------------------------------------------

    players = get_player_list()

    player_names = players["player_name"].tolist()

    selected_player = st.selectbox(
        "Select a player",
        player_names,
        index=(
            player_names.index("Kevin De Bruyne")
            if "Kevin De Bruyne" in player_names
            else 0
        ),
        key="performance_player_selector",
    )


    # --------------------------------------------------------
    # MODEL PREDICTION
    # --------------------------------------------------------

    try:

        from agent.tools.player_performance_tool import (
            predict_player_future_xg
        )

        prediction = predict_player_future_xg(
            selected_player
        )


        if "prediction" not in prediction:

            st.warning(
                prediction.get(
                    "error",
                    "Prediction unavailable."
                )
            )

        else:

            predicted_xg = float(
                prediction["prediction"]
            )


            # ------------------------------------------------
            # PREDICTION HERO
            # ------------------------------------------------

            render_html(
                f"""
                <div class="prediction-hero">

                    <div class="player-kicker">
                        RANDOM FOREST PREDICTION
                    </div>

                    <div class="prediction-value">
                        {predicted_xg:.2f}
                    </div>

                    <div class="prediction-unit">
                        predicted total xG across the
                        next 5 appearances
                    </div>

                </div>
                """
            )


            # ------------------------------------------------
            # MODEL DETAILS
            # ------------------------------------------------

            render_html(
                """
                <div class="scout-section">

                    <div class="section-label">
                        MODEL DETAILS
                    </div>

                    <div class="section-title">
                        How the prediction is generated
                    </div>

                </div>
                """
            )


            model_columns = st.columns(3)


            model_cards = [
                (
                    "Historical Window",
                    "Previous 5 appearances",
                    "The model uses the player's recent performance history."
                ),
                (
                    "Prediction Target",
                    "Next 5 appearances",
                    "The target is total xG accumulated across the future window."
                ),
                (
                    "Model",
                    "Random Forest",
                    "300 trees with constrained depth and minimum leaf size."
                ),
            ]


            for column, card in zip(
                model_columns,
                model_cards
            ):

                with column:

                    title, value, description = card

                    render_html(
                        f"""
                        <div class="prediction-model-card">

                            <div class="prediction-model-title">
                                {title}
                            </div>

                            <div
                                style="
                                    font-size:1.35rem;
                                    font-weight:850;
                                    margin-top:0.6rem;
                                "
                            >
                                {value}
                            </div>

                            <div class="prediction-model-text">
                                {description}
                            </div>

                        </div>
                        """
                    )


            # ------------------------------------------------
            # MODEL CONFIGURATION
            # ------------------------------------------------

            render_html(
                """
                <div class="scout-section">

                    <div class="section-label">
                        MODEL CONFIGURATION
                    </div>

                    <div class="section-title">
                        Random Forest parameters
                    </div>

                </div>
                """
            )


            config_columns = st.columns(4)


            config = [
                ("Trees", "300"),
                ("Max Depth", "8"),
                ("Min Leaf Size", "10"),
                ("Random State", "42"),
            ]


            for column, (label, value) in zip(
                config_columns,
                config
            ):

                with column:

                    render_html(
                        f"""
                        <div class="player-stat-card">

                            <div class="player-stat-label">
                                {label}
                            </div>

                            <div class="player-stat-value">
                                {value}
                            </div>

                        </div>
                        """
                    )


            # ------------------------------------------------
            # INTERPRETATION
            # ------------------------------------------------

            st.markdown("")

            with st.expander(
                "How to interpret this prediction"
            ):

                st.write(
                    """
                    This model predicts a player's total xG
                    across their next five appearances using
                    performance information from their previous
                    five appearances.

                    The validated ML4 benchmark used chronological
                    validation to avoid using future information
                    when constructing historical features.

                    In that benchmark, the Random Forest achieved
                    an MAE of 0.3271 and RMSE of 0.5352, compared
                    with 0.4748 MAE and 0.6793 RMSE for the mean
                    baseline.

                    The prediction is probabilistic and should
                    not be interpreted as a guaranteed outcome.

                    Future playing time and opportunity can also
                    affect a player's total xG.
                    """
                )


    except Exception as error:

        st.error(
            f"Performance prediction unavailable: {error}"
        )


elif page == "Match Intelligence":

    # ========================================================
    # MATCH INTELLIGENCE
    # ========================================================

    render_html(
        """
        <div class="section-label">
            MATCH INTELLIGENCE
        </div>

        <div class="section-title">
            Historical Match Prediction
        </div>
        """
    )

    st.caption(
        "Evaluate historical Premier League matches using "
        "the project's pre-match Random Forest model."
    )

    st.info(
        "This model is validated on historical 2015/16 matches. "
        "It is not a live fixture prediction system."
    )


    # --------------------------------------------------------
    # MATCH SELECTION
    # --------------------------------------------------------

    connection = get_connection()

    matches = pd.read_sql_query(
        """
        SELECT
            match_id,
            match_date,
            home_team_id,
            away_team_id,
            home_score,
            away_score
        FROM matches
        ORDER BY match_date
        """,
        connection
    )


    teams = pd.read_sql_query(
        """
        SELECT
            team_id,
            team_name
        FROM teams
        """,
        connection
    )


    matches = matches.merge(
        teams.rename(
            columns={
                "team_id": "home_team_id",
                "team_name": "home_team"
            }
        ),
        on="home_team_id",
        how="left"
    )


    matches = matches.merge(
        teams.rename(
            columns={
                "team_id": "away_team_id",
                "team_name": "away_team"
            }
        ),
        on="away_team_id",
        how="left"
    )


    matches["match_label"] = (
        matches["home_team"]
        + " vs "
        + matches["away_team"]
        + " • "
        + matches["match_date"]
    )


    selected_label = st.selectbox(
        "Select historical match",
        matches["match_label"].tolist(),
        index=len(matches) - 1,
        key="match_prediction_selector",
    )


    selected_match = matches[
        matches["match_label"] == selected_label
    ].iloc[0]


    match_id = int(
        selected_match["match_id"]
    )


    # --------------------------------------------------------
    # RUN MODEL
    # --------------------------------------------------------

    try:

        from agent.tools.match_outcome_tool import (
            predict_match_outcome
        )

        prediction = predict_match_outcome(
            match_id
        )


        if "error" in prediction:

            st.warning(
                prediction["error"]
            )

        else:

            predicted_result = prediction[
                "predicted_result"
            ]

            probabilities = prediction[
                "probabilities"
            ]


            # ------------------------------------------------
            # MATCH HERO
            # ------------------------------------------------

            render_html(
                f"""
                <div class="match-hero">

                    <div class="player-kicker">
                        ML5 MATCH PREDICTION
                    </div>

                    <div class="match-result">
                        {selected_match["home_team"]}
                        &nbsp; vs &nbsp;
                        {selected_match["away_team"]}
                    </div>

                    <div class="similarity-description">
                        Historical match ID {match_id}
                    </div>

                    <div
                        style="
                            margin-top:1.2rem;
                            color:#65d6a0;
                            font-size:1rem;
                            font-weight:800;
                        "
                    >
                        Predicted result:
                        {predicted_result}
                    </div>

                </div>
                """
            )


            # ------------------------------------------------
            # PROBABILITIES
            # ------------------------------------------------

            render_html(
                """
                <div class="scout-section">

                    <div class="section-label">
                        MODEL PROBABILITIES
                    </div>

                    <div class="section-title">
                        Predicted outcome distribution
                    </div>

                </div>
                """
            )


            probability_columns = st.columns(3)


            probability_data = [
                (
                    "HOME WIN",
                    probabilities.get(
                        "HOME_WIN",
                        0
                    )
                ),
                (
                    "DRAW",
                    probabilities.get(
                        "DRAW",
                        0
                    )
                ),
                (
                    "AWAY WIN",
                    probabilities.get(
                        "AWAY_WIN",
                        0
                    )
                ),
            ]


            for column, (
                label,
                probability
            ) in zip(
                probability_columns,
                probability_data
            ):

                with column:

                    render_html(
                        f"""
                        <div class="probability-card">

                            <div class="probability-label">
                                {label}
                            </div>

                            <div class="probability-value">
                                {float(probability) * 100:.1f}%
                            </div>

                        </div>
                        """
                    )


            # ------------------------------------------------
            # ACTUAL RESULT
            # ------------------------------------------------

            actual_result = (
                "HOME_WIN"
                if selected_match["home_score"]
                > selected_match["away_score"]
                else
                "AWAY_WIN"
                if selected_match["home_score"]
                < selected_match["away_score"]
                else
                "DRAW"
            )


            st.markdown("")


            actual_col, prediction_col = st.columns(2)


            with actual_col:

                render_html(
                    f"""
                    <div class="prediction-model-card">

                        <div class="prediction-model-title">
                            Actual Result
                        </div>

                        <div
                            style="
                                font-size:1.5rem;
                                font-weight:850;
                                margin-top:0.5rem;
                            "
                        >
                            {actual_result}
                        </div>

                        <div class="prediction-model-text">
                            Final score:
                            {int(selected_match["home_score"])}
                            -
                            {int(selected_match["away_score"])}
                        </div>

                    </div>
                    """
                )


            with prediction_col:

                is_correct = (
                    predicted_result == actual_result
                )

                render_html(
                    f"""
                    <div class="prediction-model-card">

                        <div class="prediction-model-title">
                            Model Assessment
                        </div>

                        <div
                            style="
                                font-size:1.5rem;
                                font-weight:850;
                                margin-top:0.5rem;
                            "
                        >
                            {"CORRECT" if is_correct else "INCORRECT"}
                        </div>

                        <div class="prediction-model-text">
                            Compared with the actual historical
                            result.
                        </div>

                    </div>
                    """
                )


            # ------------------------------------------------
            # MODEL METHODOLOGY
            # ------------------------------------------------

            render_html(
                """
                <div class="scout-section">

                    <div class="section-label">
                        MODEL METHODOLOGY
                    </div>

                    <div class="section-title">
                        Pre-match information only
                    </div>

                </div>
                """
            )


            method_columns = st.columns(3)


            method_cards = [
                (
                    "Historical Form",
                    "Previous 5 matches",
                    "Team form is calculated from matches completed before the prediction."
                ),
                (
                    "Feature Set",
                    "12 features",
                    "Includes form, goals, shots, xG, passing, pressure, carrying, duels and defensive activity."
                ),
                (
                    "Model",
                    "Random Forest",
                    "A multiclass classifier predicts HOME_WIN, DRAW or AWAY_WIN."
                ),
            ]


            for column, card in zip(
                method_columns,
                method_cards
            ):

                with column:

                    title, value, description = card

                    render_html(
                        f"""
                        <div class="prediction-model-card">

                            <div class="prediction-model-title">
                                {title}
                            </div>

                            <div
                                style="
                                    font-size:1.3rem;
                                    font-weight:850;
                                    margin-top:0.5rem;
                                "
                            >
                                {value}
                            </div>

                            <div class="prediction-model-text">
                                {description}
                            </div>

                        </div>
                        """
                    )


            # ------------------------------------------------
            # BENCHMARK
            # ------------------------------------------------

            st.markdown("")

            with st.expander(
                "Model benchmark and limitations"
            ):

                st.write(
                    """
                    The compact 12-feature Random Forest achieved
                    51.79% accuracy and 0.4535 Macro F1 on the
                    held-out chronological test period.

                    Its test Log Loss was 1.0641 and multiclass
                    Brier score was 0.6363.

                    These results indicate useful predictive signal,
                    but the model is not highly accurate enough to
                    treat individual predictions as certain.

                    The model was trained and evaluated on historical
                    Premier League 2015/16 data. It should therefore
                    not be presented as a current or live football
                    prediction system.
                    """
                )


    except Exception as error:

        st.error(
            f"Match prediction unavailable: {error}"
        )


elif page == "AI Analyst":

    # ========================================================
    # AI ANALYST
    # ========================================================

    render_html(
        """
        <div class="section-label">
            AGENTIC FOOTBALL INTELLIGENCE
        </div>

        <div class="section-title">
            AI Analyst
        </div>
        """
    )

    render_html(
        """
        <div class="ai-analyst-hero">

            <div class="player-kicker">
                FOOTBALL INTELLIGENCE AGENT
            </div>

            <div class="ai-analyst-title">
                Ask the football data anything.
            </div>

            <div class="ai-analyst-description">
                The AI Analyst can route questions to the
                project's SQL, player similarity, clustering,
                performance prediction and match intelligence
                tools, then synthesize the results into a
                natural-language answer.
            </div>

        </div>
        """
    )


    # --------------------------------------------------------
    # QUESTION INPUT
    # --------------------------------------------------------

    question = st.text_area(
        "Ask a football question",
        placeholder=(
            "Examples:\n"
            "• Who scored the most goals in the dataset?\n"
            "• Who is statistically similar to Kevin De Bruyne?\n"
            "• What archetype does Kevin De Bruyne belong to?\n"
            "• What is Kevin De Bruyne's predicted xG over his next five appearances?"
        ),
        height=130,
        key="ai_analyst_question",
    )


    # --------------------------------------------------------
    # ANALYZE BUTTON
    # --------------------------------------------------------

    analyze = st.button(
        "Run Analysis",
        use_container_width=True,
        type="primary",
    )


    if analyze:

        if not question.strip():

            st.warning(
                "Enter a football question first."
            )

        else:

            with st.spinner(
                "Analyzing the question..."
            ):

                try:

                    from agent.agent import (
                        ask_agent
                    )

                    answer = ask_agent(
                        question.strip()
                    )


                    # ----------------------------------------
                    # RESPONSE
                    # ----------------------------------------

                    render_html(
                        """
                        <div class="scout-section">

                            <div class="section-label">
                                ANALYST RESPONSE
                            </div>

                            <div class="section-title">
                                Intelligence result
                            </div>

                        </div>
                        """
                    )


                    render_html(
                        """
                        <div class="chat-assistant">
                            <div class="player-kicker">
                                FIA ANALYST
                            </div>
                        </div>
                        """
                    )

                    st.markdown(answer)
                    


                except Exception as error:

                    import traceback

                    st.error(
                        f"AI Analyst unavailable: {type(error).__name__}: {error}"
                    )

                    with st.expander("Technical error details"):
                        st.code(
                            traceback.format_exc()
                        )


    # --------------------------------------------------------
    # AVAILABLE CAPABILITIES
    # --------------------------------------------------------

    render_html(
        """
        <div class="scout-section">

            <div class="section-label">
                AGENT CAPABILITIES
            </div>

            <div class="section-title">
                What the analyst can use
            </div>

        </div>
        """
    )


    capability_columns = st.columns(4)


    capabilities = [
        (
            "SQL",
            "Exact structured football statistics "
            "from the project database."
        ),
        (
            "Similarity",
            "Find statistically similar players "
            "using the validated ML2 model."
        ),
        (
            "Archetypes",
            "Identify statistical player clusters "
            "from the ML3 K-Means model."
        ),
        (
            "Performance AI",
            "Forecast player xG across the next "
            "five appearances."
        ),
    ]


    for column, (
        title,
        description
    ) in zip(
        capability_columns,
        capabilities
    ):

        with column:

            render_html(
                f"""
                <div class="prediction-model-card">

                    <div class="prediction-model-title">
                        {title}
                    </div>

                    <div class="prediction-model-text">
                        {description}
                    </div>

                </div>
                """
            )


    # --------------------------------------------------------
    # AGENT EXPLANATION
    # --------------------------------------------------------

    st.markdown("")

    with st.expander(
        "How the AI Analyst works"
    ):

        st.write(
            """
            The AI Analyst is an orchestration layer rather
            than a standalone football knowledge model.

            It receives the user's natural-language question,
            determines which project tool is appropriate,
            executes that tool, and then synthesizes the
            returned result into a natural-language response.

            Structured football statistics are retrieved from
            the SQLite database through the read-only SQL tool.

            Player similarity, player clustering and performance
            prediction are handled by their corresponding
            validated machine-learning tools.

            The agent therefore acts as the interface between
            natural-language questions and the project's
            analytical systems.
            """
        )


elif page == "Knowledge Base":

    render_html(
        """
        <div class="section-label">
            RETRIEVAL-AUGMENTED GENERATION
        </div>

        <div class="section-title">
            Knowledge Base
        </div>
        """
    )

    render_html(
        """
        <div class="ai-analyst-hero">

            <div class="player-kicker">
                FIA KNOWLEDGE BASE
            </div>

            <div class="ai-analyst-title">
                Ask the project documentation.
            </div>

            <div class="ai-analyst-description">
                Search the validated Football Intelligence AI
                documentation using semantic retrieval and receive
                a grounded answer based only on the retrieved
                project context.
            </div>

        </div>
        """
    )

    query = st.text_area(
        "Knowledge Base Question",
        placeholder=(
            "Examples:\n"
            "• How is the role-aware scouting score calculated?\n"
            "• How were the player archetypes created?\n"
            "• What is the 900-minute scouting threshold?\n"
            "• What are the limitations of the scouting framework?"
        ),
        height=130,
        key="knowledge_base_question"
    )

    top_k = st.slider(
        "Retrieved sources",
        min_value=1,
        max_value=10,
        value=5,
        key="knowledge_base_top_k"
    )

    search = st.button(
        "Search Knowledge Base",
        use_container_width=True,
        type="primary"
    )

    if search:

        if not query.strip():

            st.warning(
                "Enter a question first."
            )

        else:

            with st.spinner(
                "Searching the project knowledge base..."
            ):

                try:

                    from rag.rag_answer import answer_question

                    answer, results = answer_question(
                        query.strip(),
                        top_k=top_k
                    )

                    render_html(
                        """
                        <div class="scout-section">

                            <div class="section-label">
                                GROUNDED ANSWER
                            </div>

                            <div class="section-title">
                                Knowledge result
                            </div>

                        </div>
                        """
                    )

                    st.markdown(
                        answer
                    )

                    render_html(
                        """
                        <div class="scout-section">

                            <div class="section-label">
                                RETRIEVAL EVIDENCE
                            </div>

                            <div class="section-title">
                                Documentation used
                            </div>

                        </div>
                        """
                    )

                    for i, result in enumerate(
                        results,
                        start=1
                    ):

                        with st.expander(
                            f"{i}. "
                            f"{result['source']} • "
                            f"{result['section']} • "
                            f"{result['similarity']:.3f}"
                        ):

                            st.write(
                                result["text"]
                            )

                except Exception as error:

                    st.error(
                        f"Knowledge Base unavailable: {error}"
                    )