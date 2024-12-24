import re
from typing import List

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
            category_list: List[str],
            blender_version: str,
            render_engine: str,
            image_path_list: List[str]
        ):
        super().__init__()
        
        self.file_id = file_id
        self.file_path = file_path
        self.file_name = re.sub(FILE_NAME_REGEX, '_', file_name)
        self.category_list = [re.sub(FILE_NAME_REGEX, '_', x) for x in category_list]
        self.blender_version = blender_version
        self.render_engine = render_engine
        self.image_path_list = image_path_list

        self.signals = WorkerSignals()