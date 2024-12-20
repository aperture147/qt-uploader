from sqlite3 import connect
from contextlib import closing
import json
from typing import Any

from PyQt6.QtCore import pyqtSlot, QObject
from ulid import ULID

class QtDBObject(QObject):
    def __init__(self):
        super().__init__()
        self.conn = connect("db.sqlite3")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA ignore_check_constraints=OFF")
        self.conn.execute("PRAGMA synchronous=OFF")

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS file (
                id BLOB PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                blender_version TEXT NOT NULL,
                render_engine TEXT NOT NULL,
                category_1 TEXT NOT NULL,
                category_2 TEXT NOT NULL,
                category_3 TEXT NOT NULL,
                image_list JSON NOT NULL DEFAULT '[]',
                task_status TEXT NOT NULL,
                task_progress INTEGER NOT NULL DEFAULT 0,
                task_message TEXT NOT NULL DEFAULT ''
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT NOT NULL PRIMARY KEY,
                value JSON NOT NULL DEFAULT '{}'
            )
        """)
        
    def __del__(self):
        self.conn.close()
    
    def list_files(self):
        with closing(self.conn.cursor()) as cur:
            cur.execute("""
                SELECT
                    id, name, path,
                    blender_version, render_engine,
                    category_1, category_2, category_3,
                    image_list,
                    task_status, task_progress, task_message
                FROM file
            """)
            for file_id, *cols, image_list in cur.fetchall():
                yield (ULID(value=file_id), *cols, json.loads(image_list))
    
    @pyqtSlot(str, Any)
    def save_config(self, key: str, value: Any):
        with closing(self.conn.cursor()) as cur:
            cur.execute("""
                INSERT INTO config
                (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = ?
            """, (key, json.dumps(value), json.dumps(value)))
            self.conn.commit()
    
    @pyqtSlot(ULID, str, str, str, str, str, str, str, list)
    def create_file(
        self,
        file_id: ULID,
        file_path: str,
        file_name: str,
        category1: str,
        category2: str,
        category3: str,
        blender_version: str,
        render_engine: str,
        image_list: list
    ):
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                """
                INSERT INTO file
                (
                    id, name, path,
                    blender_version, render_engine,
                    category_1, category_2, category_3,
                    image_list,
                    task_status, task_progress, task_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    file_id.bytes,
                    file_name,
                    file_path,
                    blender_version,
                    render_engine,
                    category1,
                    category2,
                    category3,
                    json.dumps(image_list),
                    "pending",
                    0,
                    "Pending"
                )
            )
            self.conn.commit()
    
    @pyqtSlot(ULID, int, str)
    def set_file_progress_message(self, file_id: ULID, progress: int, status: str):
        with closing(self.conn.cursor()) as cur:
            cur.execute("""
                UPDATE file
                SET task_progress = ?, task_message = ?
                WHERE id = ?
            """, (progress, status, file_id.bytes))
            self.conn.commit()

    @pyqtSlot(ULID, str)
    def set_file_status(self, file_id: ULID, status: str):
        with closing(self.conn.cursor()) as cur:
            cur.execute("""
                UPDATE file
                SET task_status = ?
                WHERE id = ?
            """,(status, file_id.bytes,))
            self.conn.commit()