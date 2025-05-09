import pytest
from unittest.mock import patch, MagicMock
from app.utils.smtp_connection import SMTPClient


@pytest.fixture
def smtp_client():
    return SMTPClient(
        server="smtp.test.com",
        port=587,
        username="user@test.com",
        password="securepassword"
    )


@patch("smtplib.SMTP")
def test_send_email_success(mock_smtp, smtp_client):
    mock_server_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server_instance

    smtp_client.send_email(
        subject="Test Subject",
        html_content="<p>This is a test</p>",
        recipient="recipient@test.com"
    )

    mock_smtp.assert_called_once_with("smtp.test.com", 587)
    mock_server_instance.starttls.assert_called_once()
    mock_server_instance.login.assert_called_once_with("user@test.com", "securepassword")
    mock_server_instance.sendmail.assert_called_once()
    args, kwargs = mock_server_instance.sendmail.call_args
    assert "user@test.com" in args
    assert "recipient@test.com" in args
    assert "<p>This is a test</p>" in args[2]  # email content


@patch("smtplib.SMTP")
def test_send_email_exception_handling(mock_smtp, smtp_client, caplog):
    # Simulate error during connection
    mock_smtp.side_effect = Exception("SMTP connection failed")

    with caplog.at_level("ERROR"):
        with pytest.raises(Exception, match="SMTP connection failed"):
            smtp_client.send_email(
                subject="Failing Email",
                html_content="<p>Error</p>",
                recipient="fail@test.com"
            )
        assert "Failed to send email: SMTP connection failed" in caplog.text
