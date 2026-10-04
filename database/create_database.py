import sqlite3

# Create / connect to the SQLite database
connection = sqlite3.connect("football.db")

print("Database connected successfully.")

# Close the connection
connection.close()

print("Database connection closed.")