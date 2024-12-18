from PyQt6.QtCore import QRunnable, pyqtSlot

class S3UploadWorker(QRunnable):
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
    @pyqtSlot()
    def run(self):
        print(f"Uploading {self.file_path} to S3")
        
        # Simulate uploading
        import time
        time.sleep(3)
        
        print(f"Uploaded {self.file_path} to S3")
        
        self.file_path = None