from pathlib import Path
import sqlite3
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATABASE_FILE = PROJECT_ROOT / "database" / "football.db"


def run_sql(query):
    """
    Execute a read-only SQL query against the Football Intelligence AI database.

    Only SELECT queries are allowed.
    """

    query = query.strip()

    # -----------------------------
    # Read-only safety check
    # -----------------------------

    if not query.lower().startswith("select"):
        raise ValueError(
            "SQL tool only allows read-only SELECT queries."
        )

    connection = sqlite3.connect(DATABASE_FILE)

    try:

        result = pd.read_sql_query(
            query,
            connection
        )

        return result

    finally:

        connection.close()


# -----------------------------
# Test
# -----------------------------

if __name__ == "__main__":

    print("Testing valid SELECT query...")

    test_query = """
    SELECT
        team_name,
        COUNT(*) AS matches
    FROM matches
    JOIN teams
        ON teams.team_id = matches.home_team_id
    GROUP BY team_name
    ORDER BY matches DESC;
    """

    result = run_sql(test_query)

    print(result)

    print("\nValid SELECT test: PASSED")


    # -----------------------------
    # Test rejected query
    # -----------------------------

    print("\nTesting rejected modification query...")

    try:

        run_sql(
            "DELETE FROM matches;"
        )

    except ValueError as error:

        print("Rejected correctly:")
        print(error)

        print("\nRead-only safety test: PASSED")