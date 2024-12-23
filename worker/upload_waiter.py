import traceback
import sys
import math

from typing import List

from ulid import ULID

from PyQt6.QtCore import QObject, pyqtSlot

import requests

from ._signal import WorkerSignals
from ._upload_base import _BaseUploadWorker as UploadWorker

class UploadWaiterWorker(QObject):
    def __init__(
            self,
            file_id: ULID,
            name: str,
            category_list: List[str],
            blender_version: str,
            render_engine: str,
        ):
        super().__init__()
        
        self.file_id = file_id
        self.name = name
        self.category_list = category_list
        self.blender_version = blender_version
        self.render_engine = render_engine
        
        self.count = 0
        self.signals = WorkerSignals()
        self.worker_dict = {}
        self.progress_dict = {}
        self.result_dict = {}
    
    def add_upload_worker(self, slot_id: str, worker: UploadWorker):
        if worker.file_id != self.file_id:
            raise ValueError("File ID mismatch")
        
        self.worker_dict[slot_id] = worker
        self.count += 1
        worker.signals.progress_message.connect(lambda x, y, z: self.receive_progress_message(slot_id, x, y, z))
        worker.signals.result.connect(lambda x, y: self.receive_result(slot_id, x, y))
        worker.signals.error.connect(lambda x, y: self.receive_error(slot_id, x, y))
    
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
    
    @pyqtSlot(str, ULID, tuple)
    def receive_result(self, slot_id: str, file_id: ULID, result: tuple):
        print(f"Received upload result of {slot_id} for {file_id}")
        self.count -= 1
        self.result_dict[slot_id] = result
        
        if self.count > 0:
            print(f'Waiting for {self.count} upload event')
            return
        self.signals.result.emit(file_id, (self.result_dict,))
    
    @pyqtSlot(str, ULID, float, str)
    def receive_progress_message(self, slot_id: str, file_id: ULID, progress: float, message: str):
        print(f"Received pload progress of {slot_id} for {file_id}: {progress:.2f}% - {message}")
        self.progress_dict[slot_id] = progress
        self.signals.progress_message.emit(
            self.file_id,
            math.ceil(sum(self.progress_dict.values()) / len(self.progress_dict)),
            message
        )
    
    @pyqtSlot(str, ULID, tuple)
    def receive_error(self, slot_id: str, file_id: ULID, err_tuple: tuple):
        print(f"Slot {slot_id} caused error: {err_tuple[0]}")
        self.signals.error.emit(file_id, err_tuple)
        self.signals.finished.emit()