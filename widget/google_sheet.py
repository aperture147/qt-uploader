from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox,
    QVBoxLayout, QLabel, QLineEdit,
    QMessageBox
)
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

class GoogleSheetSignals(QObject):
    error = pyqtSignal(tuple)
    result = pyqtSignal(str)
    finished = pyqtSignal()

class NoGoogleSheetLinkMessageBox(QMessageBox):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("No Google Sheet Link")
        self.setText("No Google Sheet Link")
        self.setInformativeText("Please provide Google Sheet Link")
        self.setIcon(QMessageBox.Icon.Critical)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)

class GoogleSheetMessageBox(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setMinimumWidth(300)
        
        self.signals = GoogleSheetSignals()

        self.setWindowTitle("Add Google Sheet")
        button_box_flag = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        
        main_layout = QVBoxLayout()

        main_layout.addWidget(QLabel("Add Google Sheet"))
        self.sheet_link = QLineEdit()
        self.sheet_link.setPlaceholderText("Google Sheet Link")

        main_layout.addWidget(self.sheet_link)

        self.button_box_widget = QDialogButtonBox(button_box_flag)
        self.button_box_widget.accepted.connect(self.check_and_accept)
        self.button_box_widget.rejected.connect(self.reject)

        main_layout.addWidget(self.button_box_widget)
        
        self.setLayout(main_layout)

    @pyqtSlot()
    def check_and_accept(self):
        sheet_link = self.sheet_link.text()
        if not sheet_link:
            NoGoogleSheetLinkMessageBox().exec()
            return

        self.signals.result.emit(self.sheet_link.text())
        self.signals.finished.emit()
        self.accept()