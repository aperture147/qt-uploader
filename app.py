import sys
from typing import Any
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QWidget
)
from PyQt6.QtCore import QThreadPool, pyqtSlot

from widget import FileSelectDialog, FileListWidget, FileListWidgetItem, GoogleLoginMessageBox
from worker import S3UploadWorker
from db import QtDBObject

class MainWindow(QMainWindow):
    
    def init_db(self):
        self.db = QtDBObject()
        
    def init_threadpool(self):
        self.s3_upload_threadpool = QThreadPool()
        self.google_drive_upload_threadpool = QThreadPool()
    
    def init_ui(self):
        self.setWindowTitle("R2 Google Drive Uploader")
        self.setMinimumSize(820, 640)
        main_layout = QVBoxLayout()
        
        new_3d_file_btn = QPushButton("Upload new 3D File")
        new_3d_file_btn.clicked.connect(self.upload_new_3d_file)
        main_layout.addWidget(new_3d_file_btn)
        
        google_login_btn = QPushButton("Google Login")
        google_login_btn.clicked.connect(self.google_login)
        main_layout.addWidget(google_login_btn)
        
        self.file_list = FileListWidget()
        main_layout.addWidget(self.file_list)
        
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.file_select_dialog = FileSelectDialog()
        self.file_select_dialog.file_selected.connect(self.create_new_upload_task)
        
    
    def init_running_task_dict(self):
        self.running_task_dict = {}
    
    def google_login(self):
        dlg = GoogleLoginMessageBox()
        dlg.signals.credential.connect(self.save_google_token)
        dlg.exec()
    
    @pyqtSlot(dict)
    def save_google_token(self, credential: dict):
        self.db.save_config('google_oauth_token', credential)
        
    
    @pyqtSlot()
    def upload_new_3d_file(self):
        self.file_select_dialog.exec()

    @pyqtSlot(str, str, str, str, str, str, str, list)
    def create_new_upload_task(
        self,
        file_path: str,
        file_name: str,
        category1: str,
        category2: str,
        category3: str,
        blender_version: str,
        render_engine: str,
        image_list: list
    ):
        task_item = FileListWidgetItem(file_name)
        self.file_list.add_item(task_item)
        
        s3_upload_worker = S3UploadWorker(
            file_path, file_name,
            category1, category2, category3,
            blender_version, render_engine,
            image_list
        )
        
        self.running_task_dict[s3_upload_worker.file_id] = task_item
        self.db.create_file(
            s3_upload_worker.file_id, file_path, file_name,
            category1, category2, category3,
            blender_version, render_engine,
            image_list
        )
        
        s3_upload_worker.signals.progress_message.connect(task_item.set_progress_message)
        s3_upload_worker.signals.progress_message.connect(self.db.set_file_progress_message)
        
        s3_upload_worker.signals.status.connect(task_item.set_status)
        s3_upload_worker.signals.status.connect(self.db.set_file_status)
        
        self.s3_upload_threadpool.start(s3_upload_worker)
        
    
    def __init__(self):
        super().__init__()
        
        self.init_db()
        self.init_running_task_dict()
        self.init_threadpool()
        self.init_ui()
        
def main():
    app = QApplication(sys.argv)
    main_gui = MainWindow()
    main_gui.show()
    return app.exec()

if __name__ == "__main__":
    main()
    