FILE_NAME_REGEX = r'[^\w_. -]'
import re

from PyQt6.QtCore import QRunnable
from ulid import ULID

from ._signal import WorkerSignals

FILE_NAME_REGEX = r'[^\w_. -]'
MODEL_FILE_UPLOAD_PROGRESS_RATIO = 0.7
FULL_3D_MODEL_PROGRESS = 100 * MODEL_FILE_UPLOAD_PROGRESS_RATIO


class _BaseUploadWorker(QRunnable):
    def __init__(
            self,
            file_id: ULID,
            file_path: str,
            file_name: str,
            category1: str,
            category2: str,
            category3: str,
            blender_version: str,
            render_engine: str,
            image_list: list
        ):
        super().__init__()
        
        self.file_id = file_id
        self.file_path = file_path
        self.file_name = re.sub(FILE_NAME_REGEX, '_', file_name)
        self.category1 = re.sub(FILE_NAME_REGEX, '_', category1)
        self.category2 = re.sub(FILE_NAME_REGEX, '_', category2)
        self.category3 = re.sub(FILE_NAME_REGEX, '_', category3)
        self.blender_version = blender_version
        self.render_engine = render_engine
        self.image_list = image_list

        self.signals = WorkerSignals()