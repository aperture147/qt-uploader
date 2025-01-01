import math

from PyQt6.QtWidgets import (
    QListWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QWidget, QPushButton,
    QListWidgetItem, QProgressBar,
    QMessageBox
)
from PyQt6.QtCore import (
    Qt, pyqtSlot,
    QObject, pyqtSignal
)
from ulid import ULID

STATUS_TO_COLOR = {
    'pending': 'gray',
    'running': 'white',
    'finished': 'green',
    'failed': 'red'
}

class FileListWidgetDeleteMessageBox(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete File")
        self.setText("Are you sure you want to delete this file?")
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        self.setDefaultButton(QMessageBox.StandardButton.No)

class FileListWidgetItemSignals(QObject):
    deleted = pyqtSignal(ULID)

class FileListWidgetItem(QWidget):
    
    def __init__(
        self,
        file_id: ULID,
        name: str,
        status: str = 'pending',
        progress: int = 0,
        message: str = "Pending"
    ):
        super().__init__()
        
        self.file_id = file_id
        self.signals = FileListWidgetItemSignals()

        item_layout = QHBoxLayout()
        item_layout.setSpacing(10)
        
        name_and_status_layout = QVBoxLayout()
        name_and_status_layout.setContentsMargins(0, 0, 0, 0)
        name_and_status_layout.setSpacing(0)
        self.task_name_label = QLabel(name)
        status_color = STATUS_TO_COLOR.get(status, 'gray')
        self.task_status_label = QLabel(f'<span style="color:{status_color}"><i>{message}</i></span>')
        name_and_status_layout.addWidget(self.task_name_label)
        name_and_status_layout.addWidget(self.task_status_label)
        self.name_and_status_widget = QWidget()
        self.name_and_status_widget.setLayout(name_and_status_layout)
        item_layout.addWidget(self.name_and_status_widget)
        
        self.task_progress_bar = QProgressBar()
        self.task_progress_bar.setFixedWidth(150)
        self.task_progress_bar.setValue(progress)
        item_layout.addWidget(self.task_progress_bar)
        
        self.task_delete_button = QPushButton("Delete")
        self.task_delete_button.clicked.connect(self.delete_item)
        self.task_delete_button.setFixedWidth(60)
        item_layout.addWidget(self.task_delete_button)
        
        self.setLayout(item_layout)

    @pyqtSlot()
    def confirm_delete(self):
        self.signals.deleted.emit(self.file_id)
        self.deleteLater()

    @pyqtSlot()
    def delete_item(self):
        msg_box = FileListWidgetDeleteMessageBox()
        msg_box.accepted.connect(self.confirm_delete)
        msg_box.exec()
        
    @pyqtSlot(ULID, float, str)
    def set_progress_message(self, file_id: ULID, progress: float, status: str):
        self.task_progress_bar.setValue(math.ceil(progress))
        self.task_status_label.setText(f'<i>{status}</i>')

    @pyqtSlot(ULID, str)
    def set_status(self, file_id: ULID, status: str):
        status_color = STATUS_TO_COLOR.get(status, 'gray')
        self.task_status_label.setText(f'<span style="color:{status_color}"><i>{status}</i></span>')

    
class FileListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def update_items(self, item_list: list[FileListWidgetItem]):
        self.clear()
        for item in item_list:
            self.add_item(item)
    
    def add_item(self, widget_item: FileListWidgetItem):
        item = QListWidgetItem()
        item.setSizeHint(widget_item.sizeHint())
        self.insertItem(0, item)
        self.setItemWidget(item, widget_item)
        
        widget_item.signals.deleted.connect(lambda _: self.takeItem(self.row(item)))