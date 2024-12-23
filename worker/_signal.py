from PyQt6.QtCore import QObject, pyqtSignal
from ulid import ULID

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(ULID, tuple)
    status = pyqtSignal(ULID, str)
    progress_message = pyqtSignal(ULID, float, str)
    result = pyqtSignal(ULID, tuple)