import sqlite3


# ---------------------------------------------------------
# Connect to database
# ---------------------------------------------------------

connection = sqlite3.connect("football.db")

# Enable foreign-key enforcement in SQLite
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()

print("Connected to football.db")


# ---------------------------------------------------------
# Create teams table
# ---------------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    team_name TEXT NOT NULL
)
""")

print("Created teams table")


# ---------------------------------------------------------
# Create players table
# ---------------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    player_name TEXT NOT NULL,
    player_nickname TEXT,
    country TEXT
)
""")

print("Created players table")


# ---------------------------------------------------------
# Create matches table
# ---------------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    match_date TEXT NOT NULL,
    kick_off TEXT NOT NULL,
    season_id INTEGER NOT NULL,
    season_name TEXT NOT NULL,

    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,

    home_score INTEGER NOT NULL,
    away_score INTEGER NOT NULL,

    match_week INTEGER,
    competition_stage TEXT,
    stadium TEXT,
    referee TEXT,
    match_result TEXT NOT NULL,

    FOREIGN KEY (home_team_id)
        REFERENCES teams(team_id),

    FOREIGN KEY (away_team_id)
        REFERENCES teams(team_id)
)
""")

print("Created matches table")


# ---------------------------------------------------------
# Create player_match table
# ---------------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS player_match (
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,

    jersey_number INTEGER,
    position_id INTEGER,
    position TEXT,

    start_reason TEXT,
    end_reason TEXT,

    from_time TEXT,
    to_time TEXT,

    minutes_played REAL NOT NULL,

    PRIMARY KEY (match_id, player_id),

    FOREIGN KEY (match_id)
        REFERENCES matches(match_id),

    FOREIGN KEY (player_id)
        REFERENCES players(player_id),

    FOREIGN KEY (team_id)
        REFERENCES teams(team_id)
)
""")

print("Created player_match table")


# ---------------------------------------------------------
# Create events table
# ---------------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    match_id INTEGER NOT NULL,
    event_id TEXT PRIMARY KEY,
    event_index INTEGER NOT NULL,

    period INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    minute INTEGER NOT NULL,
    second REAL NOT NULL,

    event_type TEXT NOT NULL,

    possession INTEGER,
    possession_team_id INTEGER,
    play_pattern TEXT,

    team_id INTEGER,
    player_id INTEGER,
    position_id INTEGER,
    position TEXT,

    location_x REAL,
    location_y REAL,

    duration REAL,
    under_pressure INTEGER,
    counterpress INTEGER,

    pass_recipient_id INTEGER,
    pass_length REAL,
    pass_angle REAL,
    pass_height TEXT,
    pass_end_x REAL,
    pass_end_y REAL,
    pass_body_part TEXT,
    pass_type TEXT,
    pass_outcome TEXT,

    shot_xg REAL,
    shot_end_x REAL,
    shot_end_y REAL,
    shot_body_part TEXT,
    shot_type TEXT,
    shot_outcome TEXT,
    shot_first_time INTEGER,
    shot_technique TEXT,
    shot_key_pass_id TEXT,

    carry_end_x REAL,
    carry_end_y REAL,

    duel_type TEXT,
    dribble_outcome TEXT,
    interception_outcome TEXT,
    clearance_body_part TEXT,

    FOREIGN KEY (match_id)
        REFERENCES matches(match_id),

    FOREIGN KEY (possession_team_id)
        REFERENCES teams(team_id),

    FOREIGN KEY (team_id)
        REFERENCES teams(team_id),

    FOREIGN KEY (player_id)
        REFERENCES players(player_id),

    FOREIGN KEY (pass_recipient_id)
        REFERENCES players(player_id)
)
""")

print("Created events table")


# ---------------------------------------------------------
# Create indexes
# ---------------------------------------------------------

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_matches_date
ON matches(match_date)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_player_match_player
ON player_match(player_id)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_player_match_team
ON player_match(team_id)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_events_match
ON events(match_id)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_events_player
ON events(player_id)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_events_team
ON events(team_id)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_events_type
ON events(event_type)
""")

print("Created indexes")


# ---------------------------------------------------------
# Save changes
# ---------------------------------------------------------

connection.commit()

print("\nDatabase schema created successfully.")


# ---------------------------------------------------------
# Display tables
# ---------------------------------------------------------

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name
""")

tables = cursor.fetchall()

print("\nTables in database:")

for table in tables:
    print("-", table[0])


# ---------------------------------------------------------
# Close connection
# ---------------------------------------------------------

connection.close()

print("\nDatabase connection closed.")