import traceback
import sys

from typing import List

from ulid import ULID

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

import requests

class UploadWaiterSignals(QObject):
    error = pyqtSignal(tuple)
    result = pyqtSignal(tuple)
    finished = pyqtSignal()
    

class UploadWaiter(QObject):
    def __init__(
            self,
            file_id: ULID,
            name: str,
            category_list: List[str],
            blender_version: str,
            render_engine: str,
            count: int = 2
        ):
        super().__init__()
        
        self.file_id = file_id
        self.name = name
        self.category_list = category_list
        self.blender_version = blender_version
        self.render_engine = render_engine
        
        self.count = count
        self.signals = UploadWaiterSignals()
    
    def _send_confirm(self):
        try:
            print("sending result to server")
            resp = requests.post(
                'http://localhost:8787/model',
                json={
                    'name': self.name,
                    'category_list': self.category_list,
                    'r2_model_path': self.r2_file_path,
                    'r2_image_path_list': self.r2_image_file_list,
                    'google_drive_model_path': self.google_drive_file_id,
                    'google_drive_image_path_list': self.google_drive_file_id_list,
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
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit((resp_json['id'],))
        finally:
            self.signals.finished.emit()
            self.deleteLater()
    
    @pyqtSlot(ULID, tuple)
    def receive_s3_upload_result(self, file_id: ULID, result: tuple):
        print(f"Received S3 upload result for {file_id}")
        self.count -= 1
        self.r2_file_path, self.r2_image_file_list = result
        if self.count > 0:
            print(f'Waiting for Google Drive upload event')
            return
        self._send_confirm()
    
    @pyqtSlot(ULID, tuple)
    def receive_google_drive_upload_result(self, file_id: ULID, result: tuple):
        print(f"Received Google Drive upload result for {file_id}")
        self.count -= 1
        self.google_drive_file_id, self.google_drive_file_id_list = result
        if self.count > 0:
            print(f'Waiting for S3 upload event')
            return
        self._send_confirm()
        
        
        
        