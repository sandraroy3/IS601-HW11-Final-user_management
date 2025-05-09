from pathlib import Path
import pytest
from unittest.mock import patch, mock_open
from app.utils.template_manager import TemplateManager


@pytest.fixture
def template_manager():
    return TemplateManager()


@patch("builtins.open", new_callable=mock_open, read_data="# Hello\nThis is a test.")
@patch("app.utils.template_manager.TemplateManager._read_template")
def test_render_template(mock_read_template, mock_file, template_manager):
    # Mock templates
    mock_read_template.side_effect = [
        "# Header",
        "# Footer",
        "## Welcome, {name}\nPlease verify your email: {verification_url}"
    ]

    result = template_manager.render_template(
        "email_verification",
        name="Alice",
        verification_url="http://example.com/verify"
    )

    assert "Alice" in result
    assert "http://example.com/verify" in result
    assert "<h2" in result  # Rendered markdown
    assert "font-family: Arial" in result  # Styled HTML
    assert "<div" in result


def test_apply_email_styles():
    html_input = "<h1>Title</h1><p>Content</p><a href='x'>link</a>"
    tm = TemplateManager()
    styled = tm._apply_email_styles(html_input)

    assert 'style="font-size: 24px;' in styled  # h1 style
    assert 'style="font-size: 16px;' in styled  # p style
    assert '<div style=' in styled


@patch("builtins.open", new_callable=mock_open, read_data="Sample Template")
def test_read_template(mock_file):
    tm = TemplateManager()
    # manually patch path to avoid real FS access
    tm.templates_dir = Path("/mock/templates")
    result = tm._read_template("template.md")

    mock_file.assert_called_once_with(Path("/mock/templates/template.md"), 'r', encoding='utf-8')
    assert result == "Sample Template"
