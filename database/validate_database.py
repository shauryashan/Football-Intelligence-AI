import sqlite3


# ---------------------------------------------------------
# Database connection
# ---------------------------------------------------------

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_ROOT / "database" / "football.db"

connection = sqlite3.connect(DATABASE_FILE)

# Enable foreign-key enforcement
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()

print("Connected to football.db")


# ---------------------------------------------------------
# 1. Check table existence
# ---------------------------------------------------------

print("\n--- TABLE CHECK ---")

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name
""")

tables = [row[0] for row in cursor.fetchall()]

expected_tables = [
    "events",
    "matches",
    "player_match",
    "players",
    "teams"
]

for table in expected_tables:
    if table in tables:
        print(f"{table}: OK")
    else:
        print(f"{table}: MISSING")


# ---------------------------------------------------------
# 2. Check row counts
# ---------------------------------------------------------

print("\n--- ROW COUNT CHECK ---")

expected_counts = {
    "teams": 20,
    "players": 644,
    "matches": 380,
    "player_match": 13678,
    "events": 1313773
}

all_counts_correct = True

for table, expected in expected_counts.items():

    cursor.execute(f"SELECT COUNT(*) FROM {table}")

    actual = cursor.fetchone()[0]

    if actual == expected:
        print(f"{table}: {actual} rows - OK")
    else:
        print(
            f"{table}: {actual} rows - "
            f"EXPECTED {expected}"
        )
        all_counts_correct = False


# ---------------------------------------------------------
# 3. Check duplicate primary keys
# ---------------------------------------------------------

print("\n--- PRIMARY KEY CHECK ---")


# Teams
cursor.execute("""
SELECT team_id, COUNT(*)
FROM teams
GROUP BY team_id
HAVING COUNT(*) > 1
""")

duplicate_teams = cursor.fetchall()

print(
    "Duplicate team IDs:",
    len(duplicate_teams)
)


# Players
cursor.execute("""
SELECT player_id, COUNT(*)
FROM players
GROUP BY player_id
HAVING COUNT(*) > 1
""")

duplicate_players = cursor.fetchall()

print(
    "Duplicate player IDs:",
    len(duplicate_players)
)


# Matches
cursor.execute("""
SELECT match_id, COUNT(*)
FROM matches
GROUP BY match_id
HAVING COUNT(*) > 1
""")

duplicate_matches = cursor.fetchall()

print(
    "Duplicate match IDs:",
    len(duplicate_matches)
)


# Events
cursor.execute("""
SELECT event_id, COUNT(*)
FROM events
GROUP BY event_id
HAVING COUNT(*) > 1
""")

duplicate_events = cursor.fetchall()

print(
    "Duplicate event IDs:",
    len(duplicate_events)
)


# Player-match composite key
cursor.execute("""
SELECT match_id, player_id, COUNT(*)
FROM player_match
GROUP BY match_id, player_id
HAVING COUNT(*) > 1
""")

duplicate_player_matches = cursor.fetchall()

print(
    "Duplicate player-match keys:",
    len(duplicate_player_matches)
)


# ---------------------------------------------------------
# 4. Foreign-key validation
# ---------------------------------------------------------

print("\n--- FOREIGN KEY CHECK ---")

cursor.execute("""
PRAGMA foreign_key_check
""")

foreign_key_errors = cursor.fetchall()

print(
    "Foreign-key violations:",
    len(foreign_key_errors)
)


# ---------------------------------------------------------
# 5. Check match-team relationships
# ---------------------------------------------------------

print("\n--- MATCH TEAM RELATIONSHIPS ---")

cursor.execute("""
SELECT COUNT(*)
FROM matches m
LEFT JOIN teams t
    ON m.home_team_id = t.team_id
WHERE t.team_id IS NULL
""")

missing_home_teams = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(*)
FROM matches m
LEFT JOIN teams t
    ON m.away_team_id = t.team_id
WHERE t.team_id IS NULL
""")

missing_away_teams = cursor.fetchone()[0]

print(
    "Matches with missing home team:",
    missing_home_teams
)

print(
    "Matches with missing away team:",
    missing_away_teams
)


# ---------------------------------------------------------
# 6. Check player-match relationships
# ---------------------------------------------------------

print("\n--- PLAYER-MATCH RELATIONSHIPS ---")

cursor.execute("""
SELECT COUNT(*)
FROM player_match pm
LEFT JOIN players p
    ON pm.player_id = p.player_id
WHERE p.player_id IS NULL
""")

missing_players = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(*)
FROM player_match pm
LEFT JOIN teams t
    ON pm.team_id = t.team_id
WHERE t.team_id IS NULL
""")

missing_teams = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(*)
FROM player_match pm
LEFT JOIN matches m
    ON pm.match_id = m.match_id
WHERE m.match_id IS NULL
""")

missing_matches = cursor.fetchone()[0]

print(
    "Player-match records with missing player:",
    missing_players
)

print(
    "Player-match records with missing team:",
    missing_teams
)

print(
    "Player-match records with missing match:",
    missing_matches
)


# ---------------------------------------------------------
# 7. Check event relationships
# ---------------------------------------------------------

print("\n--- EVENT RELATIONSHIPS ---")

cursor.execute("""
SELECT COUNT(*)
FROM events e
LEFT JOIN matches m
    ON e.match_id = m.match_id
WHERE m.match_id IS NULL
""")

event_missing_matches = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM events e
LEFT JOIN teams t
    ON e.team_id = t.team_id
WHERE e.team_id IS NOT NULL
AND t.team_id IS NULL
""")

event_missing_teams = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM events e
LEFT JOIN teams t
    ON e.possession_team_id = t.team_id
WHERE e.possession_team_id IS NOT NULL
AND t.team_id IS NULL
""")

event_missing_possession_teams = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM events e
LEFT JOIN players p
    ON e.player_id = p.player_id
WHERE e.player_id IS NOT NULL
AND p.player_id IS NULL
""")

event_missing_players = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM events e
LEFT JOIN players p
    ON e.pass_recipient_id = p.player_id
WHERE e.pass_recipient_id IS NOT NULL
AND p.player_id IS NULL
""")

event_missing_recipients = cursor.fetchone()[0]


print(
    "Events with missing match:",
    event_missing_matches
)

print(
    "Events with invalid team:",
    event_missing_teams
)

print(
    "Events with invalid possession team:",
    event_missing_possession_teams
)

print(
    "Events with invalid player:",
    event_missing_players
)

print(
    "Events with invalid pass recipient:",
    event_missing_recipients
)


# ---------------------------------------------------------
# 8. Basic match validation
# ---------------------------------------------------------

print("\n--- MATCH DATA CHECK ---")

cursor.execute("""
SELECT COUNT(*)
FROM matches
WHERE home_score < 0
OR away_score < 0
""")

invalid_scores = cursor.fetchone()[0]

print(
    "Matches with invalid scores:",
    invalid_scores
)


cursor.execute("""
SELECT match_result, COUNT(*)
FROM matches
GROUP BY match_result
ORDER BY match_result
""")

print("\nMatch results:")

for result, count in cursor.fetchall():
    print(f"{result}: {count}")


# ---------------------------------------------------------
# 9. Basic event validation
# ---------------------------------------------------------

print("\n--- EVENT DATA CHECK ---")

cursor.execute("""
SELECT COUNT(*)
FROM events
WHERE minute < 0
OR second < 0
""")

invalid_timestamps = cursor.fetchone()[0]

print(
    "Events with invalid timestamps:",
    invalid_timestamps
)


cursor.execute("""
SELECT COUNT(*)
FROM events
WHERE shot_xg IS NOT NULL
AND (
    shot_xg < 0
    OR shot_xg > 1
)
""")

invalid_xg = cursor.fetchone()[0]

print(
    "Events with invalid xG:",
    invalid_xg
)


# ---------------------------------------------------------
# 10. Final validation result
# ---------------------------------------------------------

print("\n========================================")
print("DATABASE VALIDATION COMPLETE")
print("========================================")

total_fk_errors = len(foreign_key_errors)

total_relationship_errors = (
    missing_home_teams
    + missing_away_teams
    + missing_players
    + missing_teams
    + missing_matches
    + event_missing_matches
    + event_missing_teams
    + event_missing_possession_teams
    + event_missing_players
    + event_missing_recipients
)

total_duplicates = (
    len(duplicate_teams)
    + len(duplicate_players)
    + len(duplicate_matches)
    + len(duplicate_events)
    + len(duplicate_player_matches)
)

total_data_errors = (
    total_fk_errors
    + total_relationship_errors
    + total_duplicates
    + invalid_scores
    + invalid_timestamps
    + invalid_xg
)

if all_counts_correct and total_data_errors == 0:
    print("\nDATABASE VALIDATION: PASSED")
else:
    print("\nDATABASE VALIDATION: FAILED")

print("========================================")


# ---------------------------------------------------------
# Close connection
# ---------------------------------------------------------

connection.close()

print("\nDatabase connection closed.")