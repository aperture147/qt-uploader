from PyQt6.QtCore import QRunnable, pyqtSlot
import boto3
from PyQt6.QtCore import QObject, pyqtSignal
import time

# s3_client = boto3.client(
#     "s3",
#     endpoint_url = 'https://<accountid>.r2.cloudflarestorage.com',
#     aws_access_key_id = '<access_key_id>',
#     aws_secret_access_key = '<access_key_secret>'
# )

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    progress_status = pyqtSignal(int, str)

class S3UploadWorker(QRunnable):
    def __init__(
            self,
            file_path: str,
            category1: str,
            category2: str,
            category3: str,
            blender_version: str,
            render_engine: str,
            image_list: list
        ):
        super().__init__()

        self.file_path = file_path
        self.category1 = category1
        self.category2 = category2
        self.category3 = category3
        self.blender_version = blender_version
        self.render_engine = render_engine
        self.image_list = image_list

        self.signals = WorkerSignals()
    
    @pyqtSlot()
    def run(self):
        self.signals.progress_status.emit(1, "Uploading to S3")
        
        # Simulate uploading
        time.sleep(1)
        self.signals.progress_status.emit(50, "Uploaded to S3")
        time.sleep(2)

        self.signals.progress_status.emit(100, "Uploaded to S3")
        self.signals.finished.emit()