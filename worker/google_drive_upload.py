from PyQt6.QtCore import QThreadPool, QRunnable, pyqtSlot

class GoogleDriveUploadWorker(QRunnable):
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
    @pyqtSlot()
    def run(self):
        print(f"Uploading {self.file_path} to Google Drive")
        
        # Simulate uploading
        import time
        time.sleep(3)
        
        print(f"Uploaded {self.file_path} to Google Drive")
        
        self.file_path = None