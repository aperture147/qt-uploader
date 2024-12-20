import traceback
import sys
import json

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import pyqtSlot, QThread, pyqtSignal, QObject, QDeadlineTimer
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_CONFIG = {
}

SCOPES = ["https://www.googleapis.com/auth/drive"]

class GoogleLoginWorkerSignals(QObject):
    error = pyqtSignal(tuple)
    result = pyqtSignal(dict)
    finished = pyqtSignal()
    

class GoogleLoginWorker(QObject):
    def __init__(self):
        super().__init__()
        self.signals = GoogleLoginWorkerSignals()
    
    @pyqtSlot()
    def run(self):
        try:
            # google forces me to include client secret here...
            flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
            cred_obj = flow.run_local_server(port=0)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(json.loads(cred_obj.to_json()))
        finally:
            self.signals.finished.emit()

class GoogleLoginSignal(QObject):
    credential = pyqtSignal(dict)
    finished = pyqtSignal()

class GoogleLoginMessageBox(QMessageBox):
    
    def __init__(self):
        super().__init__()
        
        self.signals = GoogleLoginSignal()
        
        self.setWindowTitle("Google Login")
        self.setText("Please complete the login process on your browser. This window will close automatically after you have logged in.")
        self.setIcon(QMessageBox.Icon.Information)
        
        # self.setStandardButtons(QMessageBox.StandardButton.Cancel)
        
        self.worker = GoogleLoginWorker()
        self.worker_thread = QThread()
        
        def end_worker_thread():
            self.worker_thread.quit()
            self.worker.deleteLater()
            self.worker_thread.deleteLater()
        
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.signals.finished.connect(end_worker_thread)
        
        self.worker.signals.result.connect(self.signals.credential.emit)
        self.worker.signals.result.connect(lambda x: self.accept())
        
        self.worker.signals.error.connect(self.reject)
        
        # self.buttons()[0].clicked.connect(self.reject)
        # self.buttons()[0].clicked.connect(end_worker_thread)
        
        self.worker_thread.start()
        
    def reject(self):
        self.worker_thread.wait(QDeadlineTimer(1000))
        super().reject()
        
    def accept(self):
        self.worker_thread.wait(QDeadlineTimer(1000))
        super().accept()