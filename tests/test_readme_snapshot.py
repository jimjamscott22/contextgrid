"""
Tests for README snapshot feature.

Tests cover:
- _parse_github_url helper
- API model validation
- CLI command parsing

Note: CRUD-level coverage of the README snapshot operations against a live
database lives with the MySQL/MariaDB-backed API layer (see api/db.py); the
Direct-mode `src.db` backend requires a real MySQL/MariaDB server and is not
exercised here since there is no lightweight, dependency-free way to spin one
up for unit tests (SQLite support, which previously filled that role, was
removed).
"""

import sys
import pytest
from pathlib import Path

# Ensure src is on the path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))


# =========================
# URL Parser Tests
# =========================

def _parse_github_url(url: str):
    """Inline copy of the helper from api/server.py for unit testing."""
    import re
    match = re.match(r'https?://github\.com/([^/\s]+)/([^/\s]+?)(?:\.git)?/?$', url.strip())
    if match:
        return match.group(1), match.group(2)
    match = re.match(r'git@github\.com:([^/\s]+)/([^/\s]+?)(?:\.git)?$', url.strip())
    if match:
        return match.group(1), match.group(2)
    return None, None


@pytest.mark.parametrize("url,expected_owner,expected_repo", [
    ("https://github.com/owner/repo", "owner", "repo"),
    ("https://github.com/owner/repo.git", "owner", "repo"),
    ("https://github.com/owner/repo/", "owner", "repo"),
    ("git@github.com:owner/repo.git", "owner", "repo"),
    ("git@github.com:owner/repo", "owner", "repo"),
    ("https://github.com/jimjamscott22/contextgrid", "jimjamscott22", "contextgrid"),
    ("https://gitlab.com/owner/repo", None, None),
    ("not-a-url", None, None),
    ("", None, None),
])
def test_parse_github_url(url, expected_owner, expected_repo):
    """Test GitHub URL parsing for various formats."""
    owner, repo = _parse_github_url(url)
    assert owner == expected_owner
    assert repo == expected_repo


# =========================
# API Model Tests
# =========================

def test_readme_snapshot_response_model():
    """ReadmeSnapshotResponse should validate required fields."""
    from api.models import ReadmeSnapshotResponse
    snap = ReadmeSnapshotResponse(
        project_id=1,
        content="# Hello",
        source_ref="main",
        fetched_at="2024-01-01T12:00:00",
    )
    assert snap.project_id == 1
    assert snap.content == "# Hello"
    assert snap.source_ref == "main"


def test_readme_attach_response_model():
    """ReadmeAttachResponse should validate required fields."""
    from api.models import ReadmeAttachResponse
    resp = ReadmeAttachResponse(
        message="Attached",
        project_id=1,
        source_ref="main",
        fetched_at="2024-01-01T12:00:00",
    )
    assert resp.message == "Attached"
    assert resp.project_id == 1


def test_readme_snapshot_response_optional_source_ref():
    """source_ref should be optional in ReadmeSnapshotResponse."""
    from api.models import ReadmeSnapshotResponse
    snap = ReadmeSnapshotResponse(
        project_id=2,
        content="# Test",
        fetched_at="2024-01-01T00:00:00",
    )
    assert snap.source_ref is None


# =========================
# CLI Parser Tests
# =========================

def test_readme_attach_command_parsing():
    """'readme attach <id>' should parse correctly."""
    from src.cli import create_parser
    parser = create_parser()
    args = parser.parse_args(["readme", "attach", "42"])
    assert args.command == "readme"
    assert args.readme_command == "attach"
    assert args.project_id == 42


def test_readme_show_command_parsing():
    """'readme show <id>' should parse correctly."""
    from src.cli import create_parser
    parser = create_parser()
    args = parser.parse_args(["readme", "show", "7"])
    assert args.command == "readme"
    assert args.readme_command == "show"
    assert args.project_id == 7


def test_readme_delete_command_parsing():
    """'readme delete <id>' should parse correctly."""
    from src.cli import create_parser
    parser = create_parser()
    args = parser.parse_args(["readme", "delete", "3"])
    assert args.command == "readme"
    assert args.readme_command == "delete"
    assert args.project_id == 3


# =========================
# Markdown Rendering Test
# =========================

def test_markdown_rendering():
    """_render_markdown logic should produce valid HTML from Markdown input."""
    import markdown as md_lib
    html = md_lib.markdown(
        "# Hello\n\nThis is **bold** text.",
        extensions=["fenced_code", "tables", "toc"],
    )
    assert "<h1" in html
    assert "<strong>bold</strong>" in html


def test_markdown_rendering_handles_empty_string():
    """_render_markdown logic should not raise for empty input."""
    import markdown as md_lib
    html = md_lib.markdown("", extensions=["fenced_code", "tables", "toc"])
    assert isinstance(html, str)


def test_markdown_rendering_code_blocks():
    """_render_markdown logic should handle fenced code blocks."""
    import markdown as md_lib
    content = "```python\nprint('hello')\n```"
    html = md_lib.markdown(content, extensions=["fenced_code", "tables", "toc"])
    assert "<code" in html
