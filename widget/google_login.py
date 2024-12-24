import traceback
import sys
import json

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import pyqtSlot, QThread, pyqtSignal, QObject, QDeadlineTimer
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_CONFIG = {
    "installed": {
        "client_id": "1032794322434-6muavbv0khohaoo29qv73lf4adt99s0k.apps.googleusercontent.com",
        "project_id": "aperture-445207",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": [
            "http://localhost"
        ]
    }
}

SCOPES = [
    "https://www.googleapis.com/auth/drive",
]

class GoogleLoginWorkerSignals(QObject):
    error = pyqtSignal(tuple)
    result = pyqtSignal(dict)
    finished = pyqtSignal()
    

class GoogleLoginWorker(QObject):
    def __init__(self):
        super().__init__()
        self.signals = GoogleLoginWorkerSignals()
        self.flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)

    @pyqtSlot()
    def run(self):
        try:
            # google forces me to include client secret here...
            cred_obj = self.flow.run_local_server(port=0)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(json.loads(cred_obj.to_json()))
        finally:
            self.signals.finished.emit()

class GoogleLoginSignal(QObject):
    credentials = pyqtSignal(dict)
    finished = pyqtSignal()

class GoogleLoginMessageBox(QMessageBox):
    
    def __init__(self):
        super().__init__()
        
        self.signals = GoogleLoginSignal()
        
        self.setWindowTitle("Google Drive Login")
        self.setText("Please complete the login process on your browser. This window will close automatically after you have logged in.")
        self.setIcon(QMessageBox.Icon.Information)
        
        self.setStandardButtons(QMessageBox.StandardButton.Cancel)
        self.setDefaultButton(QMessageBox.StandardButton.Cancel)
        default_button = self.defaultButton()
        default_button.clicked.connect(self.reject)
        
        self.worker = GoogleLoginWorker()
        self.worker_thread = QThread()
        self.worker_thread.setTerminationEnabled(True)
        
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.signals.finished.connect(self.worker_thread.quit)
        self.worker.signals.finished.connect(self.worker.deleteLater)
        self.worker.signals.finished.connect(self.worker_thread.deleteLater)
        
        self.worker.signals.result.connect(self.signals.credentials.emit)
        self.worker.signals.result.connect(lambda _: self.accept())
        
        self.worker.signals.error.connect(self.reject)
        
        self.worker_thread.start()

    @pyqtSlot()
    def reject(self):
        self.worker_thread.wait(QDeadlineTimer(1000))
        super().reject()
    
    @pyqtSlot()
    def accept(self):
        self.worker_thread.wait(QDeadlineTimer(1000))
        super().accept()