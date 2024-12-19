from PyQt6.QtCore import QObject, pyqtSignal

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    progress_status = pyqtSignal(int, str)