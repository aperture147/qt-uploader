from PyQt6.QtWidgets import (
    QListWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QWidget, QPushButton,
    QListWidgetItem, QProgressBar
)

from PyQt6.QtCore import Qt, pyqtSlot

class FileListWidgetItem(QWidget):
    
    def __init__(self, label_name):
        super().__init__()
        item_layout = QHBoxLayout()
        item_layout.setSpacing(10)
        
        name_and_status_layout = QVBoxLayout()
        name_and_status_layout.setContentsMargins(0, 0, 0, 0)
        name_and_status_layout.setSpacing(0)
        self.task_name_label = QLabel(label_name)
        self.task_status_label = QLabel("<i>Pending</i>")
        name_and_status_layout.addWidget(self.task_name_label)
        name_and_status_layout.addWidget(self.task_status_label)
        self.name_and_status_widget = QWidget()
        self.name_and_status_widget.setLayout(name_and_status_layout)
        item_layout.addWidget(self.name_and_status_widget)
        
        self.task_progress_bar = QProgressBar()
        self.task_progress_bar.setFixedWidth(150)
        self.task_progress_bar.setValue(0)
        item_layout.addWidget(self.task_progress_bar)
        
        self.task_delete_button = QPushButton("Delete")
        self.task_delete_button.setFixedWidth(60)
        item_layout.addWidget(self.task_delete_button)
        
        self.setLayout(item_layout)

    @pyqtSlot(int, str)
    def update_progress_status(self, progress: int, status: str):
        self.task_progress_bar.setValue(progress)
        self.task_status_label.setText(f'<i>{status}</i>')

    @pyqtSlot()
    def set_completed(self):
        self.task_status_label.setText('<span style="color:green"><i>Completed</i></span>')

    def set_failed(self):
        self.task_status_label.setText('<span style="color:red"><i>Failed</i></span>')
    
class FileListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
    def add_item(self, widgetItem: FileListWidgetItem):
        item = QListWidgetItem()
        item.setSizeHint(widgetItem.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widgetItem)
        
