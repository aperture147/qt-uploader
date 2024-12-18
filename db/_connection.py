import sqlite3

conn = sqlite3.connect("uploader.sqlite3")

conn.execute("""
    CREATE TABLE IF NOT EXISTS migration (
        id INTEGER PRIMARY KEY,
        previous_version BLOB NOT NULL,
        current_version BLOB NOT NULL,
    )
""")
