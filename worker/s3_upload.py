import os
import traceback
import sys

import boto3

from PyQt6.QtCore import pyqtSlot

from ._upload_base import _BaseUploadWorker

s3_client = boto3.client(
    "s3",
    endpoint_url = '',
    aws_access_key_id = '',
    aws_secret_access_key = '',
)

FILE_NAME_REGEX = r'[^\w_. -]'
MODEL_FILE_UPLOAD_PROGRESS_RATIO = 0.7

class S3UploadWorker(_BaseUploadWorker):
    @pyqtSlot()
    def run(self):
        try:
            self.signals.progress_status.emit(1, "Uploading to S3")
            orig_file_name = os.path.basename(self.file_path)
            _, ext = os.path.splitext(self.file_path)
            object_key = os.path.join(
                self.category1,
                self.category2,
                self.category3,
                f'{self.file_name}{ext}'
            )
            
            file_size = os.path.getsize(self.file_path)
            full_3d_model_progress = 100 * MODEL_FILE_UPLOAD_PROGRESS_RATIO
            
            def upload_progress(transfered):
                progress = int(transfered / file_size * 100)
                self.signals.progress_status.emit(
                    progress * MODEL_FILE_UPLOAD_PROGRESS_RATIO,
                    f"Uploading {orig_file_name}: {progress}%"
                )

            s3_client.upload_file(
                Filename=self.file_path,
                Bucket="test-bucket",
                Key=object_key,
                Callback=upload_progress
            )
            
            self.signals.progress_status.emit(full_3d_model_progress, "Uploading images to S3")
            
            image_count = len(self.image_list)
            for i, image_path in enumerate(self.image_list):
                fs_image_file_name = os.path.basename(image_path)
                image_file_name = f'{os.path.splitext(self.file_name)[0]}-preview-{i}.{os.path.splitext(fs_image_file_name)[1]}'
                
                self.signals.progress_status.emit(
                    full_3d_model_progress + (i * 29 / image_count),
                    f"Uploaded image {fs_image_file_name}"
                )
                image_key = os.path.join(
                    self.category1,
                    self.category2,
                    self.category3,
                    image_file_name
                )
                s3_client.upload_file(
                    Filename=image_path,
                    Bucket="test-bucket",
                    Key=image_key
                )
                self.signals.progress_status.emit(
                    full_3d_model_progress + ((i + 1) * 29 / image_count),
                    f"Uploaded image {fs_image_file_name} as {image_file_name}"
                )
            
            self.signals.progress_status.emit(100, "All uploaded to S3")

            self.signals.finished.emit()
            
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
            self.signals.progress_status.emit(0, "Failed to upload data to S3")
            
            