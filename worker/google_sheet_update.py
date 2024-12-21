import os
import traceback
import sys

from PyQt6.QtCore import pyqtSlot

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from ._upload_base import _BaseWorker

class GoogleSheetUpdateWorker(_BaseWorker):
    def __init__(
            self,
            file_path: str,
            file_name: str,
            category1: str,
            category2: str,
            category3: str,
            blender_version: str,
            render_engine: str,
            image_list: list,
            credentials: Credentials
        ):
        super().__init__(
            file_path, file_name,
            category1, category2, category3,
            blender_version, render_engine,
            image_list
        )
        self.credentials = credentials
        self.sheet_service = build('sheets', 'v3', credentials=self.credentials)

    @pyqtSlot()
    def run(self):
        try:
            sheet = self.sheet_service.spreadsheets()
            
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.status.emit(self.file_id, "error")
            self.signals.error.emit(self.file_id, (exctype, value, traceback.format_exc()))
            self.signals.progress_message.emit(self.file_id, 0, "Failed to upload data to S3")
        else:
            self.signals.progress_message.emit(self.file_id, 100, "All uploaded to S3")
            self.signals.status.emit(self.file_id, "finished")
        finally:
            self.signals.finished.emit()
        
            
            