import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import (
    get_settings,
    get_email_service,
    get_db,
    get_current_user,
    require_role,
)
from app.services.email_service import EmailService
from settings.config import Settings


def test_get_settings_returns_settings():
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_get_email_service_returns_email_service():
    service = get_email_service()
    assert isinstance(service, EmailService)

def test_get_current_user_valid_token(mocker):
    mock_token = "valid.token"
    mock_payload = {"sub": "123", "role": "admin"}
    mocker.patch("app.dependencies.decode_token", return_value=mock_payload)

    user = get_current_user(token=mock_token)
    assert user["user_id"] == "123"
    assert user["role"] == "admin"


def test_get_current_user_invalid_token_none(mocker):
    mocker.patch("app.dependencies.decode_token", return_value=None)
    with pytest.raises(HTTPException) as exc:
        get_current_user(token="invalid.token")
    assert exc.value.status_code == 401


def test_get_current_user_missing_fields(mocker):
    mocker.patch("app.dependencies.decode_token", return_value={"sub": "123"})
    with pytest.raises(HTTPException) as exc:
        get_current_user(token="token")
    assert exc.value.status_code == 401


def test_require_role_allows_authorized_role(mocker):
    mock_user = {"user_id": "123", "role": "admin"}
    checker = require_role("admin")
    result = checker(current_user=mock_user)
    assert result == mock_user


def test_require_role_rejects_unauthorized_role(mocker):
    mock_user = {"user_id": "123", "role": "user"}
    checker = require_role("admin")
    with pytest.raises(HTTPException) as exc:
        checker(current_user=mock_user)
    assert exc.value.status_code == 403
