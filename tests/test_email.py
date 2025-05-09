import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager
from app.models.user_model import User


@pytest.fixture
def mock_template_manager():
    manager = MagicMock(spec=TemplateManager)
    manager.render_template.return_value = "<html>Email Content</html>"
    return manager


@pytest.fixture
def email_service(mock_template_manager):
    with patch("app.services.email_service.SMTPClient") as MockSMTP:
        smtp_instance = MockSMTP.return_value
        smtp_instance.send_email = MagicMock()
        return EmailService(template_manager=mock_template_manager)


@pytest.mark.asyncio
async def test_send_email_verification(email_service):
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    await email_service.send_user_email(user_data, 'email_verification')
    email_service.smtp_client.send_email.assert_called_once()


@pytest.mark.asyncio
async def test_send_password_reset_email(email_service):
    user_data = {
        "email": "reset@example.com",
        "name": "Reset User",
        "reset_url": "http://example.com/reset"
    }
    await email_service.send_user_email(user_data, 'password_reset')
    email_service.smtp_client.send_email.assert_called_once()


@pytest.mark.asyncio
async def test_send_account_locked_email(email_service):
    user_data = {
        "email": "locked@example.com",
        "name": "Locked User",
        "locked_reason": "Too many attempts"
    }
    await email_service.send_user_email(user_data, 'account_locked')
    email_service.smtp_client.send_email.assert_called_once()


@pytest.mark.asyncio
async def test_send_email_invalid_type_raises(email_service):
    user_data = {
        "email": "invalid@example.com",
        "name": "Invalid User"
    }
    with pytest.raises(ValueError, match="Invalid email type"):
        await email_service.send_user_email(user_data, 'unknown_type')


@pytest.mark.asyncio
async def test_send_verification_email_calls_send_user_email(email_service):
    user = User(
        id=1,
        email="verify@example.com",
        first_name="Verify",
        verification_token="token123"
    )
    with patch.object(email_service, "send_user_email", new_callable=AsyncMock) as mock_send:
        await email_service.send_verification_email(user)
        mock_send.assert_awaited_once()
        args, kwargs = mock_send.call_args
        assert args[1] == 'email_verification'
        assert args[0]["email"] == "verify@example.com"
        assert "verify-email" in args[0]["verification_url"]
