from PyQt6.QtCore import QRunnable, pyqtSlot

from ._upload_base import _BaseUploadWorker

class GoogleDriveUploadWorker(_BaseUploadWorker):
    @pyqtSlot()
    def run(self):
        print(f"Uploading {self.file_path} to Google Drive")
        
        # Simulate uploading
        import time
        time.sleep(3)
        
        print(f"Uploaded {self.file_path} to Google Drive")
        
        self.file_path = None