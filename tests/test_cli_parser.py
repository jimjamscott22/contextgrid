"""Tests for CLI argument parser covering all commands and subcommands.

Existing tests only covered `readme attach/show/delete` parsing. This file
exercises the full parser surface: top-level commands, subcommand routing,
positional and optional arguments, and defaults.
"""

import pytest

from src.cli import create_parser


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def parser():
    """Fresh parser for each test."""
    return create_parser()


# ---------------------------------------------------------------------------
# Top-level commands
# ---------------------------------------------------------------------------

class TestAddCommand:
    """Parser tests for 'add <name>'."""

    def test_add_parses_name(self, parser) -> None:
        args = parser.parse_args(["add", "MyProject"])
        assert args.command == "add"
        assert args.name == "MyProject"

    def test_add_requires_name(self, parser) -> None:
        with pytest.raises(SystemExit):
            parser.parse_args(["add"])


class TestListCommand:
    """Parser tests for 'list [--status STATUS] [--tag TAG]'."""

    def test_list_no_filters(self, parser) -> None:
        args = parser.parse_args(["list"])
        assert args.command == "list"
        assert args.status is None

    def test_list_with_status(self, parser) -> None:
        args = parser.parse_args(["list", "--status", "active"])
        assert args.status == "active"

    def test_list_with_tag(self, parser) -> None:
        args = parser.parse_args(["list", "--tag", "python"])
        assert args.tag == "python"

    def test_list_rejects_invalid_status(self, parser) -> None:
        with pytest.raises(SystemExit):
            parser.parse_args(["list", "--status", "invalid"])


class TestSearchCommand:
    """Parser tests for 'search <query> [--status STATUS]'."""

    def test_search_parses_query(self, parser) -> None:
        args = parser.parse_args(["search", "grid"])
        assert args.command == "search"
        assert args.query == "grid"

    def test_search_with_status(self, parser) -> None:
        args = parser.parse_args(["search", "grid", "--status", "active"])
        assert args.query == "grid"
        assert args.status == "active"

    def test_search_requires_query(self, parser) -> None:
        with pytest.raises(SystemExit):
            parser.parse_args(["search"])


class TestShowCommand:
    """Parser tests for 'show <id>'."""

    def test_show_parses_id(self, parser) -> None:
        args = parser.parse_args(["show", "42"])
        assert args.command == "show"
        assert args.id == 42

    def test_show_requires_id(self, parser) -> None:
        with pytest.raises(SystemExit):
            parser.parse_args(["show"])


class TestUpdateCommand:
    """Parser tests for 'update <id>'."""

    def test_update_parses_id(self, parser) -> None:
        args = parser.parse_args(["update", "7"])
        assert args.command == "update"
        assert args.id == 7


class TestTouchCommand:
    """Parser tests for 'touch <id>'."""

    def test_touch_parses_id(self, parser) -> None:
        args = parser.parse_args(["touch", "3"])
        assert args.command == "touch"
        assert args.id == 3


class TestRoadmapCommand:
    """Parser tests for 'roadmap [--output FILE]'."""

    def test_roadmap_default_output(self, parser) -> None:
        args = parser.parse_args(["roadmap"])
        assert args.command == "roadmap"
        assert args.output == "ROADMAP.md"

    def test_roadmap_custom_output(self, parser) -> None:
        args = parser.parse_args(["roadmap", "--output", "my-roadmap.md"])
        assert args.output == "my-roadmap.md"


# ---------------------------------------------------------------------------
# Note subcommands
# ---------------------------------------------------------------------------

class TestNoteCommands:
    """Parser tests for 'note add|list|show|delete'."""

    def test_note_add(self, parser) -> None:
        args = parser.parse_args(["note", "add", "5"])
        assert args.command == "note"
        assert args.note_command == "add"
        assert args.project_id == 5

    def test_note_list(self, parser) -> None:
        args = parser.parse_args(["note", "list", "5"])
        assert args.command == "note"
        assert args.note_command == "list"
        assert args.project_id == 5

    def test_note_list_with_type(self, parser) -> None:
        args = parser.parse_args(["note", "list", "5", "--type", "blocker"])
        assert args.type == "blocker"

    def test_note_list_rejects_invalid_type(self, parser) -> None:
        with pytest.raises(SystemExit):
            parser.parse_args(["note", "list", "5", "--type", "invalid"])

    def test_note_show(self, parser) -> None:
        args = parser.parse_args(["note", "show", "10"])
        assert args.note_command == "show"
        assert args.note_id == 10

    def test_note_delete(self, parser) -> None:
        args = parser.parse_args(["note", "delete", "10"])
        assert args.note_command == "delete"
        assert args.note_id == 10


# ---------------------------------------------------------------------------
# Tag subcommands
# ---------------------------------------------------------------------------

class TestTagCommands:
    """Parser tests for 'tag add|remove|list'."""

    def test_tag_add(self, parser) -> None:
        args = parser.parse_args(["tag", "add", "1", "python"])
        assert args.command == "tag"
        assert args.tag_command == "add"
        assert args.project_id == 1
        assert args.tag_name == "python"

    def test_tag_remove(self, parser) -> None:
        args = parser.parse_args(["tag", "remove", "1", "python"])
        assert args.tag_command == "remove"
        assert args.project_id == 1
        assert args.tag_name == "python"

    def test_tag_list_all(self, parser) -> None:
        args = parser.parse_args(["tag", "list"])
        assert args.tag_command == "list"
        assert args.project_id is None

    def test_tag_list_for_project(self, parser) -> None:
        args = parser.parse_args(["tag", "list", "5"])
        assert args.tag_command == "list"
        assert args.project_id == 5


# ---------------------------------------------------------------------------
# README subcommands
# ---------------------------------------------------------------------------

class TestReadmeCommands:
    """Parser tests for 'readme attach|show|delete'."""

    def test_readme_attach(self, parser) -> None:
        args = parser.parse_args(["readme", "attach", "42"])
        assert args.command == "readme"
        assert args.readme_command == "attach"
        assert args.project_id == 42

    def test_readme_show(self, parser) -> None:
        args = parser.parse_args(["readme", "show", "7"])
        assert args.readme_command == "show"
        assert args.project_id == 7

    def test_readme_delete(self, parser) -> None:
        args = parser.parse_args(["readme", "delete", "3"])
        assert args.readme_command == "delete"
        assert args.project_id == 3


# ---------------------------------------------------------------------------
# No-command / help behaviour
# ---------------------------------------------------------------------------

class TestNoCommand:
    """Calling with no args should print help (return code 1)."""

    def test_no_command_returns_nonzero(self, parser) -> None:
        from src.cli import main
        assert main([]) == 1
