import sys


from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from widget import FileSelectDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("R2 Google Drive Uploader")
        self.setMinimumSize(720, 720)

        button = QPushButton("Click me!")
        button.clicked.connect(self.button_clicked)
        self.setCentralWidget(button)
        
    def button_clicked(self):
        dlg = FileSelectDialog()
        dlg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = MainWindow()
    main_gui.show()
    sys.exit(app.exec())
    