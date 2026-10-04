import sqlite3
from pathlib import Path

import pandas as pd


DATABASE_FILE = "football.db"
QUERY_FILE = Path("analytics/queries.sql")


queries_text = QUERY_FILE.read_text()

queries = queries_text.split(";")

queries = [
    query.strip()
    for query in queries
    if query.strip()
]


print("Available queries:")

for index, query in enumerate(queries, start=1):
    print(f"{index}. Query {index}")


choice = int(input("\nEnter query number: "))

query = queries[choice - 1]


connection = sqlite3.connect(DATABASE_FILE)

results = pd.read_sql_query(query, connection)

connection.close()


print("\nResults:")
print(results)