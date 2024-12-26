import urllib.parse

from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox,
    QVBoxLayout, QLabel, QLineEdit,
    QMessageBox
)
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class GoogleDriveLinkSignals(QObject):
    error = pyqtSignal(tuple)
    result = pyqtSignal(str)
    finished = pyqtSignal()

class InvalidGoogleDriveLinkMessageBox(QMessageBox):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Invalid Google Drive Link")
        self.setText("Invalid Google Drive Link")
        self.setInformativeText("Please provide a valid Google Drive Link")
        self.setIcon(QMessageBox.Icon.Warning)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)

class GoogleDriveLinkPermissionDeniedMessageBox(QMessageBox):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Permission Denied")
        self.setText("Permission Denied")
        self.setInformativeText("You don't have permission to access this folder")
        self.setIcon(QMessageBox.Icon.Critical)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)

class GoogleDriveLinkMessageBox(QDialog):
    def __init__(self, credentials: Credentials):
        super().__init__()
        
        self.credentials = credentials
        self.drive_service = build('drive', 'v3', credentials=self.credentials)

        self.setMinimumWidth(300)
        
        self.signals = GoogleDriveLinkSignals()

        self.setWindowTitle("Add Google Sheet")
        button_box_flag = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        
        main_layout = QVBoxLayout()

        main_layout.addWidget(QLabel("Add Google Drive Link"))
        self.sheet_link = QLineEdit()
        self.sheet_link.setPlaceholderText("Google Drive Link")

        main_layout.addWidget(self.sheet_link)

        self.button_box_widget = QDialogButtonBox(button_box_flag)
        self.button_box_widget.accepted.connect(self.check_and_accept)
        self.button_box_widget.rejected.connect(self.reject)

        main_layout.addWidget(self.button_box_widget)
        
        self.setLayout(main_layout)

    @pyqtSlot()
    def check_and_accept(self):
        drive_link = self.sheet_link.text()
        if not drive_link:
            InvalidGoogleDriveLinkMessageBox().exec()
            return
        parse_result = urllib.parse.urlparse(drive_link)
        path_parts = parse_result.path.split("/")
        if "folders" not in path_parts:
            InvalidGoogleDriveLinkMessageBox().exec()
            return
        
        folder_id = path_parts[path_parts.index("folders") + 1]
        
        permissions = self.drive_service.permissions().list(
            fileId=folder_id,
            fields="permissions(id, role, emailAddress)"
        ).execute()
        
        permissions: list[str] = permissions.get("permissions", [])
        if not permissions:
            InvalidGoogleDriveLinkMessageBox().exec()
            return

        user_info_service = build('oauth2', 'v2', credentials=self.credentials)
        user_info = user_info_service.userinfo().get().execute()
        user_email = user_info.get("email")
        for permission in permissions:
            if (permission["role"] == "owner") or \
                ((
                    (permission.get("emailAddress") == user_email) or \
                    (permission["id"] == "anyoneWithLink") \
                ) and (permission["role"] == "writer")):
                self.signals.result.emit(folder_id)
                self.signals.finished.emit()
                self.accept()
                return
        
        GoogleDriveLinkPermissionDeniedMessageBox().exec()