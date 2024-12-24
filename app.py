import sys
from typing import Dict, Tuple, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget
)
from PyQt6.QtCore import QThreadPool, pyqtSlot, QThread

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from ulid import ULID

from widget import (
    FileSelectDialog, FileListWidget,FileListWidgetItem,
    GoogleLoginMessageBox, # GoogleSheetMessageBox
)

from worker import (
    S3UploadWorker, GoogleDriveUploadWorker,
    UploadWaiterWorker
)

from util.api import create_api_upload_worker


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
        google_btn_layout.setSpacing(10)
        google_btn_layout.setContentsMargins(0, 0, 0, 0)

        new_3d_file_btn = QPushButton("Upload new 3D File")
        new_3d_file_btn.clicked.connect(self.upload_new_3d_file)
        google_btn_layout.addWidget(new_3d_file_btn)

        self.google_login_btn = QPushButton("Google Drive Login")
        self.google_login_btn.clicked.connect(self.google_login)
        self.google_login_btn.setEnabled(False)
        google_btn_layout.addWidget(self.google_login_btn)

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
        for file_id, name, *_, \
            status, progress, message in file_list:
            task_item = FileListWidgetItem(name, status, progress, message)
            self.file_list.add_item(task_item)
            if status == "finished":
                continue
            
            if file_id in self.running_task_dict:
                *_, upload_waiter, _ = self.running_task_dict[file_id]
                upload_waiter.signals.progress_message.connect(task_item.set_progress_message)
    
    def init_running_task_dict(self):
        self.running_task_dict: Dict[ULID, Tuple[S3UploadWorker, GoogleDriveUploadWorker, UploadWaiterWorker, QThread]] = {}
    
    def google_login(self):
        dlg = GoogleLoginMessageBox()
        dlg.signals.credentials.connect(self.save_google_token)
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
        image_path_list: List[str]
    ):
        if not self.google_oauth_credentials or not self.google_oauth_credentials.valid:
            print("Google Drive credential is invalid, cannot upload")
            # FIXME: show message box
            return

        task_item = FileListWidgetItem(file_name)
        self.file_list.add_item(task_item)
        
        file_id = ULID()
        
        self.db.create_file(
            file_id, file_path, file_name,
            [category1, category2, category3],
            image_path_list,
            blender_version, render_engine
        )
        
        upload_waiter = UploadWaiterWorker(
            file_id, file_name,
            [category1, category2, category3],
            blender_version, render_engine
        )
        upload_waiter_thread = QThread()
        upload_waiter.moveToThread(upload_waiter_thread)
        upload_waiter.signals.finished.connect(upload_waiter_thread.quit)
        upload_waiter.signals.finished.connect(upload_waiter_thread.deleteLater)
        upload_waiter.signals.finished.connect(upload_waiter.deleteLater)
        
        s3_upload_worker = S3UploadWorker(
            file_id, file_path, file_name,
            [category1, category2, category3],
            blender_version, render_engine,
            image_path_list
        )
        
        upload_waiter.signals.progress_message.connect(task_item.set_progress_message)
        upload_waiter.signals.progress_message.connect(self.db.set_file_progress_message)

        google_drive_upload_worker = GoogleDriveUploadWorker(
            file_id, file_path, file_name,
            [category1, category2, category3],
            blender_version, render_engine,
            image_path_list,
            self.google_oauth_credentials
        )
        
        upload_waiter.add_upload_worker("google_drive", google_drive_upload_worker)
        upload_waiter.add_upload_worker("s3", s3_upload_worker)
        
        upload_waiter_thread.start()
        
        self.upload_threadpool.start(s3_upload_worker)
        self.upload_threadpool.start(google_drive_upload_worker)
        
        def handle_result(file_id: ULID, result_tuple: Tuple[Dict[str, tuple]]):
            task_item.set_progress_message(file_id, 99, "Committing to API")
            result, = result_tuple
            api_upload_worker = create_api_upload_worker(
                file_id, file_name,
                [category1, category2, category3],
                blender_version, render_engine, result
            )
            api_upload_worker.signals.result.connect(lambda: task_item.set_progress_message(file_id, 100, "Finished"))
            api_upload_worker.signals.result.connect(lambda: self.db.set_file_progress_message(file_id, 100, "Finished"))
            api_upload_worker.signals.result.connect(lambda: self.db.set_file_status(file_id, "finished"))
            self.upload_threadpool.start(api_upload_worker)

        upload_waiter.signals.result.connect(handle_result)
        upload_waiter.signals.result.connect(self.db.set_uploaded_file_attributes)
        
        self.running_task_dict[s3_upload_worker.file_id] = (
            s3_upload_worker, google_drive_upload_worker,
            upload_waiter, upload_waiter_thread
        )


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
    