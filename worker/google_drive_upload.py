import os
import traceback
import sys
import mimetypes

from PyQt6.QtCore import pyqtSlot

from ulid import ULID

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

from ._upload_base import (
    _BaseUploadWorker,
    FULL_3D_MODEL_PROGRESS
)

class GoogleDriveUploadWorker(_BaseUploadWorker):
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
            image_list: list,
            credentials: Credentials
        ):
        super().__init__(
            file_id, file_path, file_name,
            category1, category2, category3,
            blender_version, render_engine,
            image_list
        )
        self.credentials = credentials
        self.drive_service = build('drive', 'v3', credentials=self.credentials)

    @pyqtSlot()
    def run(self):
        try:
            self.signals.progress_message.emit(self.file_id, 1, "Preparing for uploading to Google Drive")

            self.signals.progress_message.emit(self.file_id, 3, "Checking for existing folders")
            parent_folder_id = None
            folder_metadata = {
                'mimeType': 'application/vnd.google-apps.folder'
            }
            current_folder_path = ''
            folder_checking_progress = 10
            for category in [self.category1, self.category2, self.category3]:
                folder_metadata['name'] = category
                current_folder_path += f'{category}/'
                self.signals.progress_message.emit(self.file_id, folder_checking_progress, f"Checking folder {current_folder_path}")
                conditions = [
                    f"name='{category}'",
                    "mimeType='application/vnd.google-apps.folder'",
                    "trashed=false"
                ]
                if parent_folder_id:
                    conditions.append(f"'{parent_folder_id}' in parents")
                    folder_metadata['parents'] = [parent_folder_id]
                
                query = " and ".join(conditions)
                results = self.drive_service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id, name)').execute()
                
                items = results.get('files', [])
                if items:
                    self.signals.progress_message.emit(self.file_id, folder_checking_progress + 10, f"Folder {current_folder_path} already existed")
                    parent_folder_id = items[0]['id']
                else:
                    self.signals.progress_message.emit(self.file_id, folder_checking_progress + 5, f"Folder {current_folder_path} does not exist, creating")
                    folder = self.drive_service.files().create(body=folder_metadata, fields='id').execute()
                    self.signals.progress_message.emit(self.file_id, folder_checking_progress + 5, f"Folder {current_folder_path} created")
                    parent_folder_id = folder.get('id')

            _, ext = os.path.splitext(self.file_path)
            file_name = f'{self.file_name}{ext}'
            
            file_metadata = {
                'name': file_name,
                'parents': [parent_folder_id]
            }

            mime_type, _ = mimetypes.guess_type(self.file_path)
            media = MediaFileUpload(self.file_path, mimetype=mime_type)
            
            self.signals.progress_message.emit(
                self.file_id,
                folder_checking_progress + 5,
                "Uploading model to Google Drive"
            )

            file = self.drive_service.files() \
                .create(body=file_metadata, media_body=media, fields="id") \
                .execute()
            model_file_id = file.get("id")
            print(f'File ID: {model_file_id}')

            self.signals.progress_message.emit(
                self.file_id,
                FULL_3D_MODEL_PROGRESS,
                "Uploaded images to Google Drive"
            )
            image_file_id_list = []
            image_count = len(self.image_list)
            for i, image_path in enumerate(self.image_list):
                fs_image_file_name = os.path.basename(image_path)
                image_file_name = f'{os.path.splitext(self.file_name)[0]}-preview-{i}{os.path.splitext(fs_image_file_name)[1]}'
                
                self.signals.progress_message.emit(
                    self.file_id,
                    FULL_3D_MODEL_PROGRESS + (i * 29 / image_count),
                    f"Uploading image {fs_image_file_name} {i + 1}/{image_count}"
                )
                
                file_metadata = {
                    'name': image_file_name,
                    'parents': [parent_folder_id]
                }
                image_mime_type, _ = mimetypes.guess_type(image_path)
                media = MediaFileUpload(image_path, mimetype=image_mime_type)
                image_file = self.drive_service.files() \
                    .create(body=file_metadata, media_body=media, fields="id") \
                    .execute()
                image_file_id_list.append(image_file.get("id"))
                print(f'Image File ID: {image_file.get("id")}')
                self.signals.progress_message.emit(
                    self.file_id,
                    FULL_3D_MODEL_PROGRESS + ((i + 1) * 29 / image_count),
                    f"Uploaded image {fs_image_file_name} as {image_file_name}"
                )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit(self.file_id, (exctype, value, traceback.format_exc()))
            self.signals.progress_message.emit(self.file_id, 0, "Failed to upload data to Google Drive")
        else:
            self.signals.progress_message.emit(self.file_id, 100, "All uploaded to Google Drive")            
            self.signals.result.emit(self.file_id, (model_file_id, image_file_id_list))
        finally:
            self.signals.finished.emit()