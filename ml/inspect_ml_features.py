import sqlite3
import pandas as pd

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_FILE = PROJECT_ROOT / "database" / "football.db"


# --------------------------------------------------
# CONNECT TO DATABASE
# --------------------------------------------------

connection = sqlite3.connect(DATABASE_FILE)

print("Connected to football.db")


# --------------------------------------------------
# INSPECT AVAILABLE TABLES
# --------------------------------------------------

tables = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name;
    """,
    connection
)

print("\n--- DATABASE TABLES ---")
print(tables)


# --------------------------------------------------
# INSPECT PLAYER-MATCH DATA
# --------------------------------------------------

player_match_columns = pd.read_sql_query(
    "PRAGMA table_info(player_match);",
    connection
)

print("\n--- PLAYER_MATCH COLUMNS ---")
print(player_match_columns[["name", "type"]])


# --------------------------------------------------
# INSPECT EVENTS
# --------------------------------------------------

event_columns = pd.read_sql_query(
    "PRAGMA table_info(events);",
    connection
)

print("\n--- EVENTS COLUMNS ---")
print(event_columns[["name", "type"]])


# --------------------------------------------------
# CHECK PLAYER POPULATION
# --------------------------------------------------

player_count = pd.read_sql_query(
    """
    SELECT COUNT(*) AS players
    FROM players;
    """,
    connection
)

print("\n--- PLAYER COUNT ---")
print(player_count)


# --------------------------------------------------
# CHECK 900+ MINUTE POPULATION
# --------------------------------------------------

scouting_population = pd.read_sql_query(
    """
    SELECT
        COUNT(*) AS players,
        MIN(total_minutes) AS min_minutes,
        MAX(total_minutes) AS max_minutes,
        AVG(total_minutes) AS avg_minutes
    FROM (
        SELECT
            player_id,
            SUM(minutes_played) AS total_minutes
        FROM player_match
        GROUP BY player_id
        HAVING SUM(minutes_played) >= 900
    );
    """,
    connection
)

print("\n--- SCOUTING POPULATION ---")
print(scouting_population)


# --------------------------------------------------
# CLOSE DATABASE
# --------------------------------------------------

connection.close()

print("\nDatabase connection closed.")