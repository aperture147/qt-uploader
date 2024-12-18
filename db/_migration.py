conn.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id BLOB PRIMARY KEY,
        file_path TEXT NOT NULL,
        blender_version TEXT NOT NULL,
        render_engine TEXT NOT NULL,
        progress INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT "Pending",
        image_list JSON NOT NULL DEFAULT "[]",
    )
""")