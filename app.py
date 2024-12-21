import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget
)
from PyQt6.QtCore import QThreadPool, pyqtSlot

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from widget import (
    FileSelectDialog, FileListWidget, FileListWidgetItem,
    GoogleLoginMessageBox, GoogleSheetMessageBox
)
from worker import S3UploadWorker, GoogleDriveUploadWorker
from db import QtDBObject

class MainWindow(QMainWindow):
    
    def init_db(self):
        self.db = QtDBObject()
        
    def init_threadpool(self):
        self.upload_threadpool = QThreadPool()
    
    def init_ui(self):
        self.setWindowTitle("R2 Google Drive Uploader")
        self.setMinimumSize(820, 640)
        main_layout = QVBoxLayout()
        
        google_btn_layout = QHBoxLayout()
        google_btn_layout.setContentsMargins(0, 0, 0, 0)

        new_3d_file_btn = QPushButton("Upload new 3D File")
        new_3d_file_btn.clicked.connect(self.upload_new_3d_file)
        google_btn_layout.addWidget(new_3d_file_btn)

        self.google_login_btn = QPushButton("Google Drive Login")
        self.google_login_btn.clicked.connect(self.google_login)
        self.google_login_btn.setEnabled(False)
        google_btn_layout.addWidget(self.google_login_btn)

        google_sheet_btn = QPushButton("Google Sheet Link")
        google_sheet_btn.clicked.connect(self.google_sheet)
        google_btn_layout.addWidget(google_sheet_btn)

        google_btn_widget = QWidget()
        google_btn_widget.setLayout(google_btn_layout)

        main_layout.addWidget(google_btn_widget)
        
        self.file_list = FileListWidget()
        main_layout.addWidget(self.file_list)
        
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.file_select_dialog = FileSelectDialog()
        self.file_select_dialog.file_selected.connect(self.create_new_upload_task)

        google_oauth_token = self.db.get_config('google_oauth_token')
        self.google_oauth_credentials = None
        
        if not google_oauth_token:
            self.google_login_btn.setEnabled(True)
            return
        
        self.google_oauth_credentials = Credentials.from_authorized_user_info(google_oauth_token)
        if self.google_oauth_credentials.valid:
            self.google_login_btn.setText("Google Drive Logged In")
            return
        
        if not self.google_oauth_credentials.refresh_token:
            self.google_login_btn.setEnabled(True)
            return
        
        self.google_oauth_credentials.refresh(Request())
        if self.google_oauth_credentials.valid:
            self.google_login_btn.setText("Google Drive Logged In")
            return
        
        self.google_login_btn.setEnabled(True)
            
    def init_file_list(self):
        file_list = self.db.list_files()
        for file_id, name, path, \
            blender_version, render_engine, \
            category1, category2, category3, \
            image_list, status, progress, message in file_list:
            task_item = FileListWidgetItem(name, status, progress, message)
            if status == "finished":
                self.file_list.add_item(task_item)
                continue

            if file_id in self.running_task_dict:
                s3_upload_worker: S3UploadWorker = self.running_task_dict[file_id]
                s3_upload_worker.signals.progress_message.connect(task_item.set_progress_message)
                s3_upload_worker.signals.progress_message.connect(self.db.set_file_progress_message)
                
                s3_upload_worker.signals.status.connect(task_item.set_status)
                s3_upload_worker.signals.status.connect(self.db.set_file_status)
                
                self.file_list.add_item(task_item)

    def init_running_task_dict(self):
        self.running_task_dict = {}
    
    def google_login(self):
        dlg = GoogleLoginMessageBox()
        dlg.signals.credentials.connect(self.save_google_token)
        dlg.exec()
    
    def google_sheet(self):
        dlg = GoogleSheetMessageBox()
        dlg.signals.result.connect(lambda x: self.db.save_config('google_sheet_link', x))
        dlg.exec()

    @pyqtSlot(dict)
    def save_google_token(self, credentials: dict):
        self.db.save_config('google_oauth_token', credentials)
        self.google_login_btn.setText("Google Drive Logged In")
        self.google_login_btn.setEnabled(False)
    
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
        
        self.running_task_dict[s3_upload_worker.file_id] = s3_upload_worker
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
        
        self.upload_threadpool.start(s3_upload_worker)

        if not self.google_oauth_credentials or not self.google_oauth_credentials.valid:
            print("Credential is invalid, upload to Google Drive skipped")
            return

        google_drive_upload_worker = GoogleDriveUploadWorker(
            file_path, file_name,
            category1, category2, category3,
            blender_version, render_engine,
            image_list,
            self.google_oauth_credentials
        )

        google_drive_upload_worker.signals.progress_message.connect(task_item.set_progress_message)
        google_drive_upload_worker.signals.progress_message.connect(self.db.set_file_progress_message)
        
        google_drive_upload_worker.signals.status.connect(task_item.set_status)
        google_drive_upload_worker.signals.status.connect(self.db.set_file_status)

        self.upload_threadpool.start(google_drive_upload_worker)
        
    
    def __init__(self):
        super().__init__()
        
        self.init_db()
        self.init_running_task_dict()
        self.init_threadpool()
        self.init_ui()
        self.init_file_list()
        
def main():
    app = QApplication(sys.argv)
    main_gui = MainWindow()
    main_gui.show()
    return app.exec()

if __name__ == "__main__":
    main()
    