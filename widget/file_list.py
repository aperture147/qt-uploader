from PyQt6.QtWidgets import (
    QListWidget, QHBoxLayout, QLabel,
    QWidget, QPushButton, QProgressBar,
    QListWidgetItem
)

from PyQt6.QtCore import Qt, pyqtSlot

class FileListWidgetItem(QListWidgetItem):
    
    def __init__(self, label_name):
        super().__init__()
        self.item_widget = QWidget()
        item_layout = QHBoxLayout()
        
        self.task_label = QLabel(label_name)
        
        self.task_progress_bar = QProgressBar()
        self.task_progress_bar.setFixedWidth(150)
        self.task_progress_bar.setValue(0)
        
        self.task_delete_button = QPushButton("Delete")
        self.task_delete_button.setFixedWidth(60)
        
        item_layout.addWidget(self.task_label)
        item_layout.addWidget(self.task_progress_bar)
        item_layout.addWidget(self.task_delete_button)
        
        self.item_widget.setLayout(item_layout)
        self.setSizeHint(self.item_widget.sizeHint())

    def update_progress_status(self, progress: int, status: str):
        self.task_progress_bar.setValue(progress)
        self.task_label.setText(status)

class FileListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
    def add_item(self, item: FileListWidgetItem):
        self.addItem(item)
        self.setItemWidget(item, item.item_widget)
        
