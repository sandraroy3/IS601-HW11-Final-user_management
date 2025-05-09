from minio import Minio
from fastapi import UploadFile
from uuid import UUID
import io
import os
from settings.config import settings

minio_client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=False  # Set to True if using HTTPS
)

MINIO_BUCKET_NAME = "profile-pictures"
BASE_URL = f"http://{os.getenv('MINIO_ENDPOINT', 'localhost:9000')}/{MINIO_BUCKET_NAME}"

async def upload_profile_picture_to_minio(file: UploadFile, user_id: UUID) -> str:
    if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
        minio_client.make_bucket(MINIO_BUCKET_NAME)

    object_name = f"{user_id}/{file.filename}"
    content = await file.read()

    minio_client.put_object(
        MINIO_BUCKET_NAME,
        object_name,
        io.BytesIO(content),
        length=len(content),
        content_type=file.content_type,
    )

    return f"{BASE_URL}/{object_name}"