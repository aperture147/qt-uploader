import sqlite3

conn = sqlite3.connect("uploader.sqlite3")

conn.execute("""
    CREATE TABLE IF NOT EXISTS migration (
        id BLOB PRIMARY KEY,
        previous_id BLOB NOT NULL,
        description TEXT NOT NULL
    )
""")
