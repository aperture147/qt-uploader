import os
import traceback
import sys

import boto3

from PyQt6.QtCore import pyqtSlot

from ._upload_base import (
    _BaseWorker,
    FULL_3D_MODEL_PROGRESS,
    MODEL_FILE_UPLOAD_PROGRESS_RATIO
)

s3_client = boto3.client(
    "s3",
    endpoint_url = 'https://56c1fdc0e46364be6a2a901129366679.r2.cloudflarestorage.com',
    aws_access_key_id = 'a91cfe1b30d1a2b932eab21fe98ae2e2',
    aws_secret_access_key = '0b5d1088e4ce8dcaabd553e31292d53e6b74cf135666970e0f5ab197e9699ffa',
)



class S3UploadWorker(_BaseWorker):
    @pyqtSlot()
    def run(self):
        try:
            self.signals.status.emit(self.file_id, "running")
            self.signals.progress_message.emit(self.file_id, 10, "Uploading to S3")
            orig_file_name = os.path.basename(self.file_path)
            _, ext = os.path.splitext(self.file_path)
            object_key = os.path.join(
                self.category1,
                self.category2,
                self.category3,
                f'{self.file_name}{ext}'
            )
            
            file_size = os.path.getsize(self.file_path)
            
            def upload_progress(transfered):
                progress = int(transfered / file_size * 100)
                self.signals.progress_message.emit(
                    self.file_id,
                    progress * MODEL_FILE_UPLOAD_PROGRESS_RATIO,
                    f"Uploading {orig_file_name}: {progress}%"
                )

            s3_client.upload_file(
                Filename=self.file_path,
                Bucket="test-bucket",
                Key=object_key,
                Callback=upload_progress
            )
            
            self.signals.progress_message.emit(
                self.file_id,
                FULL_3D_MODEL_PROGRESS,
                "Uploaded images to S3"
            )
            
            image_count = len(self.image_list)
            for i, image_path in enumerate(self.image_list):
                fs_image_file_name = os.path.basename(image_path)
                image_file_name = f'{os.path.splitext(self.file_name)[0]}-preview-{i}{os.path.splitext(fs_image_file_name)[1]}'
                
                self.signals.progress_message.emit(
                    self.file_id,
                    FULL_3D_MODEL_PROGRESS + (i * 29 / image_count),
                    f"Uploading image {fs_image_file_name} {i + 1}/{image_count}"
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
                self.signals.progress_message.emit(
                    self.file_id,
                    FULL_3D_MODEL_PROGRESS + ((i + 1) * 29 / image_count),
                    f"Uploaded image {fs_image_file_name} as {image_file_name}"
                )
            
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.status.emit(self.file_id, "error")
            self.signals.error.emit(self.file_id, (exctype, value, traceback.format_exc()))
            self.signals.progress_message.emit(self.file_id, 0, "Failed to upload data to S3")
        else:
            self.signals.progress_message.emit(self.file_id, 100, "All uploaded to S3")
            self.signals.status.emit(self.file_id, "finished")
        finally:
            self.signals.finished.emit()
        
            
            