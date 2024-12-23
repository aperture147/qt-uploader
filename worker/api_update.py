from typing import List
import sys
import traceback

from PyQt6.QtCore import QRunnable, pyqtSlot

import requests
from ulid import ULID

from ._signal import WorkerSignals

class APIUpdateWorker(QRunnable):
    def __init__(
            self,
            file_id: ULID,
            name: str,
            category_list: List[str],
            r2_model_path: str,
            r2_image_path_list: List[str],
            google_drive_model_path: str,
            google_drive_image_path_list: List[str],
            blender_version: str,
            render_engine: str
        ):
        super().__init__()
        
        self.file_id = file_id
        self.name = name
        self.category_list = category_list
        self.r2_model_path = r2_model_path
        self.r2_image_path_list = r2_image_path_list
        self.google_drive_model_path = google_drive_model_path
        self.google_drive_image_path_list = google_drive_image_path_list
        self.blender_version = blender_version
        self.render_engine = render_engine
        self.signals = WorkerSignals()
        
    @pyqtSlot()
    def run(self):
        print(f"sending {self.file_id} result to server")
        try:
            print("sending result to server")
            resp = requests.post(
                'http://localhost:8787/model',
                json={
                    'name': self.name,
                    'category_list': self.category_list,
                    'r2_model_path': self.r2_model_path,
                    'r2_image_path_list': self.r2_image_path_list,
                    'google_drive_model_path': self.google_drive_model_path,
                    'google_drive_image_path_list': self.google_drive_image_path_list,
                    'blender_version': self.blender_version,
                    'render_engine': self.render_engine
                },
                timeout=10
            )
            resp.raise_for_status()
            resp_json = resp.json()
            print("new model id: ", resp_json['id'])
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit(self.file_id, (exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit((resp_json['id'],))
        finally:
            self.signals.finished.emit()