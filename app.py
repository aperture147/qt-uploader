import sys


from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QWidget
)

from widget import FileSelectDialog, FileListWidget, FileListWidgetItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("R2 Google Drive Uploader")
        self.setMinimumSize(480, 640)
        main_layout = QVBoxLayout()
        
        button = QPushButton("Click me!")
        button.clicked.connect(self.button_clicked)
        main_layout.addWidget(button)
        
        file_list = FileListWidget()
        file_list.add_item(FileListWidgetItem("Test"))
        
        main_layout.addWidget(file_list)
        
        main_widget = QWidget()
        
        main_widget.setLayout(main_layout)
        
        self.setCentralWidget(main_widget)
    
    def button_clicked(self):
        dlg = FileSelectDialog()
        dlg.fileSelected.connect(lambda *x: print(x))
        
        dlg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = MainWindow()
    main_gui.show()
    sys.exit(app.exec())
    