from sqlite3 import connect
from contextlib import closing
import json
from typing import Any, Generator, Dict, Tuple, List
import math

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
                category_list JSON NOT NULL DEFAULT '[]',
                image_path_list JSON NOT NULL DEFAULT '[]',
                s3_model_key TEXT,
                s3_image_key_list JSON NOT NULL DEFAULT '[]',
                google_drive_model_id TEXT,
                google_drive_image_id_list JSON NOT NULL DEFAULT '[]',
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
    
    def list_files(self) -> Generator[tuple[
            ULID, str, str,
            str, str,
            List[str], List[str],
            str, List[str],
            str, List[str],
            str, str, str
        ], None, None]:
        with closing(self.conn.cursor()) as cur:
            cur.execute("""
                SELECT
                    id, name, path,
                    blender_version, render_engine,
                    category_list, image_path_list,
                    s3_model_key, s3_image_key_list,
                    google_drive_model_id, google_drive_image_id_list,
                    task_status, task_progress, task_message
                FROM file
            """)
            for file_id, name, path, \
                blender_version, render_engine, \
                category_list, image_path_list, \
                s3_model_key, s3_image_key_list, \
                google_drive_model_id, google_drive_image_id_list, \
                status, progress, message in cur.fetchall():
                yield (
                    ULID(value=file_id), name, path,
                    blender_version, render_engine,
                    json.loads(category_list), json.loads(image_path_list),
                    s3_model_key, json.loads(s3_image_key_list),
                    google_drive_model_id, json.loads(google_drive_image_id_list),
                    status, progress, message
                )
    
    @pyqtSlot(str, dict)
    def save_config(self, key: str, value: dict):
        with closing(self.conn.cursor()) as cur:
            cur.execute("""
                INSERT INTO config
                (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = ?
            """, (key, json.dumps(value), json.dumps(value)))
            self.conn.commit()
    
    def get_config(self, key: str) -> Any:
        with closing(self.conn.cursor()) as cur:
            cur.execute("""
                SELECT value
                FROM config
                WHERE key = ?
                LIMIT 1
            """, (key,))
            credentials = cur.fetchone()
            if not credentials:
                return None
            return json.loads(credentials[0])

    @pyqtSlot(ULID, str, str, list, list, str, str)
    def create_file(
        self,
        file_id: ULID,
        file_name: str,
        file_path: str,
        category_list: List[str],
        image_path_list: List[str],
        blender_version: str,
        render_engine: str,
    ):
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                """
                INSERT INTO file
                (
                    id, name, path,
                    blender_version, render_engine,
                    category_list, image_path_list,
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
                    json.dumps(category_list),
                    json.dumps(image_path_list),
                    "pending",
                    0,
                    "Pending"
                )
            )
            self.conn.commit()
    
    @pyqtSlot(ULID, float, str)
    def set_file_progress_message(self, file_id: ULID, progress: float, message: str):
        print(f"Setting progress message for {file_id} to {progress}: {message}")
        with closing(self.conn.cursor()) as cur:
            cur.execute("""
                UPDATE file
                SET task_progress = ?, task_message = ?
                WHERE id = ?
            """, (math.ceil(progress), message, file_id.bytes))
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
    
    @pyqtSlot(ULID, tuple)
    def set_uploaded_file_attributes(
            self,
            file_id: ULID,
            result_tuple: Tuple[Dict[str, tuple]]
        ):
        with closing(self.conn.cursor()) as cur:
            result, = result_tuple
            google_drive_model_path, google_drive_image_path_list = result['google_drive']
            s3_model_key, s3_image_key_list = result['s3']
            cur.execute("""
                UPDATE file SET 
                    s3_model_key = ?, s3_image_key_list = ?,
                    google_drive_model_id = ?, google_drive_image_id_list = ?
                WHERE id = ?
            """, (
                s3_model_key, json.dumps(s3_image_key_list),
                google_drive_model_path, json.dumps(google_drive_image_path_list),
                file_id.bytes
            ))
            
            self.conn.commit()