from typing import Dict, List
from worker import APIUpdateWorker

def create_api_upload_worker(
        file_id: str,
        name: str,
        category_list: List[str],
        blender_version: str,
        render_engine: str,
        result: Dict[str, tuple]
    ) -> APIUpdateWorker:
    
    params = {
        'file_id': file_id,
        'name': name,
        'category_list': category_list,
        'blender_version': blender_version,
        'render_engine': render_engine
    }
    google_drive_model_path, google_drive_image_path_list = result['google_drive']
    r2_model_path, r2_image_path_list = result['s3']
    params['google_drive_model_path'] = google_drive_model_path
    params['google_drive_image_path_list'] = google_drive_image_path_list
    params['r2_model_path'] = r2_model_path
    params['r2_image_path_list'] = r2_image_path_list
    
    return APIUpdateWorker(**params)