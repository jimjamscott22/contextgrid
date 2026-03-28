"""
Tests for README snapshot feature.

Tests cover:
- _parse_github_url helper
- SQLite backend README snapshot CRUD (upsert, get, delete)
- API model validation
- CLI command parsing
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from typing import Optional

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
# SQLite Backend Tests
# =========================

def _get_sqlite_backend(db_path: str):
    """Create a fresh SQLiteBackend for testing."""
    from src.db import SQLiteBackend
    backend = SQLiteBackend(db_path)
    backend.initialize_database()
    return backend


def _create_test_project(backend, name: str = "Test Project") -> int:
    """Helper: create a project in the test database and return its ID."""
    return backend.create_project(
        name=name,
        status="active",
        repo_url="https://github.com/owner/repo",
    )


class TestSQLiteReadmeSnapshot:
    """Tests for SQLiteBackend README snapshot operations."""

    def setup_method(self):
        """Create a temp database for each test."""
        self._tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self._tmpdir, "test.db")
        self.backend = _get_sqlite_backend(self.db_path)
        self.project_id = _create_test_project(self.backend)

    def test_get_readme_snapshot_returns_none_when_missing(self):
        """get_readme_snapshot should return None for a project with no snapshot."""
        result = self.backend.get_readme_snapshot(self.project_id)
        assert result is None

    def test_upsert_creates_snapshot(self):
        """upsert_readme_snapshot should create a new snapshot."""
        content = "# Hello\n\nThis is the README."
        self.backend.upsert_readme_snapshot(self.project_id, content, "main")

        snapshot = self.backend.get_readme_snapshot(self.project_id)
        assert snapshot is not None
        assert snapshot["project_id"] == self.project_id
        assert snapshot["content"] == content
        assert snapshot["source_ref"] == "main"
        assert snapshot["fetched_at"] is not None

    def test_upsert_updates_existing_snapshot(self):
        """upsert_readme_snapshot should replace an existing snapshot."""
        self.backend.upsert_readme_snapshot(self.project_id, "# Old", "main")
        self.backend.upsert_readme_snapshot(self.project_id, "# New", "master")

        snapshot = self.backend.get_readme_snapshot(self.project_id)
        assert snapshot["content"] == "# New"
        assert snapshot["source_ref"] == "master"

    def test_delete_readme_snapshot(self):
        """delete_readme_snapshot should remove the snapshot."""
        self.backend.upsert_readme_snapshot(self.project_id, "# README", "main")
        deleted = self.backend.delete_readme_snapshot(self.project_id)
        assert deleted is True
        assert self.backend.get_readme_snapshot(self.project_id) is None

    def test_delete_readme_snapshot_returns_false_when_missing(self):
        """delete_readme_snapshot should return False when nothing to delete."""
        deleted = self.backend.delete_readme_snapshot(self.project_id)
        assert deleted is False

    def test_snapshot_deleted_when_project_is_deleted(self):
        """Snapshot should be cascade-deleted when its project is deleted."""
        self.backend.upsert_readme_snapshot(self.project_id, "# README", "main")
        self.backend.delete_project(self.project_id)
        snapshot = self.backend.get_readme_snapshot(self.project_id)
        assert snapshot is None

    def test_upsert_without_source_ref(self):
        """upsert_readme_snapshot should work without a source_ref."""
        self.backend.upsert_readme_snapshot(self.project_id, "# README", None)
        snapshot = self.backend.get_readme_snapshot(self.project_id)
        assert snapshot is not None
        assert snapshot["source_ref"] is None


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
