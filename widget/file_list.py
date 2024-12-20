from PyQt6.QtWidgets import (
    QListWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QWidget, QPushButton,
    QListWidgetItem, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSlot
from ulid import ULID

STATUS_TO_COLOR = {
    'pending': 'gray',
    'running': 'white',
    'finished': 'green',
    'failed': 'red'
}

class FileListWidgetItem(QWidget):
    
    def __init__(
        self,
        name: str,
        status: str = 'pending',
        progress: int = 0,
        message: str = "Pending"
    ):
        super().__init__()
        
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
        self.task_delete_button.setFixedWidth(60)
        item_layout.addWidget(self.task_delete_button)
        
        self.setLayout(item_layout)

    @pyqtSlot(ULID, int, str)
    def set_progress_message(self, file_id: ULID, progress: int, status: str):
        self.task_progress_bar.setValue(progress)
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
    
    def add_item(self, widgetItem: FileListWidgetItem):
        item = QListWidgetItem()
        item.setSizeHint(widgetItem.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widgetItem)
        
