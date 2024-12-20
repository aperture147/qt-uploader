from PyQt6.QtCore import pyqtSlot

from ._upload_base import _BaseUploadWorker

class GoogleDriveUploadWorker(_BaseUploadWorker):
    @pyqtSlot()
    def run(self, token):
        
        self.file_path = None