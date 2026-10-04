import sqlite3
import pandas as pd


# ---------------------------------------------------------
# File paths
# ---------------------------------------------------------

DATABASE_FILE = "football.db"

TEAMS_FILE = "teams.csv"
PLAYERS_FILE = "players.csv"
MATCHES_FILE = "matches_cleaned.csv"
PLAYER_MATCH_FILE = "player_match_cleaned.csv"
EVENTS_FILE = "events_final.csv"


# ---------------------------------------------------------
# Connect to database
# ---------------------------------------------------------

connection = sqlite3.connect(DATABASE_FILE)

# Enable foreign-key enforcement
connection.execute("PRAGMA foreign_keys = ON")

print("Connected to football.db")


try:

    # -----------------------------------------------------
    # Load CSV files into Pandas
    # -----------------------------------------------------

    teams_df = pd.read_csv(TEAMS_FILE)
    players_df = pd.read_csv(PLAYERS_FILE)
    matches_df = pd.read_csv(MATCHES_FILE)
    player_match_df = pd.read_csv(PLAYER_MATCH_FILE)
    events_df = pd.read_csv(EVENTS_FILE)

    print("\nCSV files loaded successfully.")

    print("Teams:", len(teams_df))
    print("Players:", len(players_df))
    print("Matches:", len(matches_df))
    print("Player-match records:", len(player_match_df))
    print("Events:", len(events_df))


    # -----------------------------------------------------
    # Insert teams
    # -----------------------------------------------------

    teams_df.to_sql(
        "teams",
        connection,
        if_exists="append",
        index=False
    )

    print("\nTeams inserted successfully.")


    # -----------------------------------------------------
    # Insert players
    # -----------------------------------------------------

    players_df.to_sql(
        "players",
        connection,
        if_exists="append",
        index=False
    )

    print("Players inserted successfully.")


    # -----------------------------------------------------
    # Insert matches
    # -----------------------------------------------------

    matches_df.to_sql(
        "matches",
        connection,
        if_exists="append",
        index=False
    )

    print("Matches inserted successfully.")


    # -----------------------------------------------------
    # Insert player-match records
    # -----------------------------------------------------

    player_match_df.to_sql(
        "player_match",
        connection,
        if_exists="append",
        index=False
    )

    print("Player-match records inserted successfully.")


    # -----------------------------------------------------
    # Insert events
    # -----------------------------------------------------

    events_df.to_sql(
        "events",
        connection,
        if_exists="append",
        index=False
    )

    print("Events inserted successfully.")


    # -----------------------------------------------------
    # Save all changes
    # -----------------------------------------------------

    connection.commit()

    print("\nAll data inserted successfully.")


finally:

    # -----------------------------------------------------
    # Close database connection
    # -----------------------------------------------------

    connection.close()

    print("Database connection closed.")