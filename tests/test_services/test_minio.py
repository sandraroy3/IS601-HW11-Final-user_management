import io
import pytest
from uuid import uuid4
from fastapi import UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.minio_service import upload_profile_picture_to_minio

@pytest.mark.asyncio
async def test_upload_profile_picture_to_minio(monkeypatch):
    # Setup: Mock bucket check and put_object
    mock_minio_client = MagicMock()
    mock_minio_client.bucket_exists.return_value = False
    mock_minio_client.make_bucket.return_value = None
    mock_minio_client.put_object.return_value = None

    monkeypatch.setattr("app.services.minio_service.minio_client", mock_minio_client)
    monkeypatch.setattr("app.services.minio_service.MINIO_BUCKET_NAME", "test-bucket")
    monkeypatch.setattr("app.services.minio_service.BASE_URL", "http://localhost:9000/test-bucket")

    # Prepare fake file
    content = b"fake-image-content"
    file = UploadFile(file=io.BytesIO(content), filename="profile.png")

    user_id = uuid4()

    # Execute
    url = await upload_profile_picture_to_minio(file, user_id)

    # Assert
    object_name = f"{user_id}/profile.png"
    expected_url = f"http://localhost:9000/test-bucket/{object_name}"

    assert url == expected_url
    mock_minio_client.bucket_exists.assert_called_once_with("test-bucket")
    mock_minio_client.make_bucket.assert_called_once_with("test-bucket")
    mock_minio_client.put_object.assert_called_once()
