import sys


from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QWidget
)

from PyQt6.QtCore import QThreadPool, pyqtSlot

from widget import FileSelectDialog, FileListWidget, FileListWidgetItem

from worker import S3UploadWorker, GoogleDriveUploadWorker

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.s3_upload_threadpool = QThreadPool()
        self.google_drive_upload_threadpool = QThreadPool()

        self.setWindowTitle("R2 Google Drive Uploader")
        self.setMinimumSize(480, 640)
        main_layout = QVBoxLayout()
        
        new_3d_file_btn = QPushButton("Upload new 3D File")
        new_3d_file_btn.clicked.connect(self.upload_new_3d_file)
        main_layout.addWidget(new_3d_file_btn)
        
        self.file_list = FileListWidget()
        
        main_layout.addWidget(self.file_list)
        
        main_widget = QWidget()
        
        main_widget.setLayout(main_layout)
        
        self.setCentralWidget(main_widget)
    
    @pyqtSlot()
    def upload_new_3d_file(self):
        dlg = FileSelectDialog()
        dlg.file_selected.connect(self.create_new_upload_task)
        dlg.exec()

    @pyqtSlot(str, str, str, str, str, str, list)
    def create_new_upload_task(
        self,
        file_path: str,
        category1: str,
        category2: str,
        category3: str,
        blender_version: str,
        render_engine: str,
        image_list: list
    ):  
        
        task_item = FileListWidgetItem(file_path)
        self.file_list.add_item(task_item)

        s3_upload_worker = S3UploadWorker(
            file_path,
            category1, category2, category3,
            blender_version, render_engine,
            image_list
        )
        s3_upload_worker.signals.progress_status.connect(task_item.update_progress_status)
        self.s3_upload_threadpool.start(s3_upload_worker)
        
        
def main():
    app = QApplication(sys.argv)
    main_gui = MainWindow()
    main_gui.show()
    return app.exec()

if __name__ == "__main__":
    main()
    