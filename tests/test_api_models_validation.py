"""Tests for Pydantic API model validation across all model families.

Existing tests covered ProjectCreate/ProjectUpdate types and URL scheme
validation. This file extends coverage to Notes, Tags, Relationships, Links,
Commands, Tasks (checklist), Templates, and Analytics models — verifying
acceptance of valid data, field constraints, pattern validation, and defaults.
"""

import pytest
from pydantic import ValidationError

from api.models import (
    # Notes
    NoteCreate,
    NoteResponse,
    NoteStatusUpdate,
    # Tags
    TagCreate,
    TagResponse,
    # Relationships
    RelationshipCreate,
    # Links
    LinkCreate,
    # Commands
    CommandCreate,
    # Tasks (checklist)
    ProjectTaskCreate,
    # Templates
    TemplateCreate,
    TemplateUpdate,
    # Analytics / Graph
    AnalyticsSummary,
    AnalyticsChartItem,
    GraphNode,
    GraphEdge,
    # Screenshot
    ScreenshotResponse,
    CoverRequest,
    # Mermaid
    MermaidResponse,
    # Health / generic
    HealthResponse,
    MessageResponse,
    TouchResponse,
    # Project (additional edge cases not in existing tests)
    ProjectBase,
    ProjectUpdate,
)


# ═══════════════════════════════════════════════════════════════════════════
# Note models
# ═══════════════════════════════════════════════════════════════════════════

class TestNoteModels:
    """Validation tests for Note models."""

    @pytest.mark.parametrize("note_type", ["log", "idea", "blocker", "reflection", "future_idea"])
    def test_note_create_accepts_valid_types(self, note_type: str) -> None:
        note = NoteCreate(content="Some note", note_type=note_type)
        assert note.note_type == note_type

    def test_note_create_default_type_is_log(self) -> None:
        note = NoteCreate(content="Default type")
        assert note.note_type == "log"

    def test_note_create_rejects_invalid_type(self) -> None:
        with pytest.raises(ValidationError):
            NoteCreate(content="Bad type", note_type="invalid")

    def test_note_create_requires_non_empty_content(self) -> None:
        with pytest.raises(ValidationError):
            NoteCreate(content="")

    @pytest.mark.parametrize("status", ["active", "completed", "archived"])
    def test_note_status_update_accepts_valid(self, status: str) -> None:
        obj = NoteStatusUpdate(status=status)
        assert obj.status == status

    def test_note_status_update_rejects_invalid(self) -> None:
        with pytest.raises(ValidationError):
            NoteStatusUpdate(status="deleted")


# ═══════════════════════════════════════════════════════════════════════════
# Tag models
# ═══════════════════════════════════════════════════════════════════════════

class TestTagModels:
    """Validation tests for Tag models."""

    def test_tag_create_accepts_valid_name(self) -> None:
        tag = TagCreate(name="python")
        assert tag.name == "python"

    def test_tag_create_rejects_empty_name(self) -> None:
        with pytest.raises(ValidationError):
            TagCreate(name="")

    def test_tag_create_rejects_overlength_name(self) -> None:
        with pytest.raises(ValidationError):
            TagCreate(name="a" * 101)

    def test_tag_response_defaults(self) -> None:
        tag = TagResponse(name="rust")
        assert tag.project_count == 0


# ═══════════════════════════════════════════════════════════════════════════
# Relationship models
# ═══════════════════════════════════════════════════════════════════════════

class TestRelationshipModels:
    """Validation tests for Relationship models."""

    @pytest.mark.parametrize("rel_type", ["related_to", "depends_on", "part_of"])
    def test_create_accepts_valid_types(self, rel_type: str) -> None:
        rel = RelationshipCreate(target_project_id=2, relationship_type=rel_type)
        assert rel.relationship_type == rel_type

    def test_create_rejects_invalid_type(self) -> None:
        with pytest.raises(ValidationError):
            RelationshipCreate(target_project_id=2, relationship_type="friends_with")


# ═══════════════════════════════════════════════════════════════════════════
# Link models
# ═══════════════════════════════════════════════════════════════════════════

class TestLinkModels:
    """Validation tests for Link models."""

    @pytest.mark.parametrize("link_type", ["docs", "deployment", "design", "board", "repo", "other"])
    def test_create_accepts_valid_link_types(self, link_type: str) -> None:
        link = LinkCreate(title="Link", url="https://example.com", link_type=link_type)
        assert link.link_type == link_type

    def test_create_default_link_type_is_other(self) -> None:
        link = LinkCreate(title="Link", url="https://example.com")
        assert link.link_type == "other"

    def test_create_rejects_invalid_link_type(self) -> None:
        with pytest.raises(ValidationError):
            LinkCreate(title="Link", url="https://example.com", link_type="social")

    def test_create_rejects_empty_title(self) -> None:
        with pytest.raises(ValidationError):
            LinkCreate(title="", url="https://example.com")

    def test_create_rejects_empty_url(self) -> None:
        with pytest.raises(ValidationError):
            LinkCreate(title="Link", url="")

    def test_create_rejects_javascript_url(self) -> None:
        with pytest.raises(ValidationError):
            LinkCreate(title="Bad", url="javascript:void(0)", link_type="other")

    def test_create_accepts_https_url(self) -> None:
        link = LinkCreate(title="Good", url="https://docs.example.com")
        assert link.url == "https://docs.example.com"


# ═══════════════════════════════════════════════════════════════════════════
# Command models
# ═══════════════════════════════════════════════════════════════════════════

class TestCommandModels:
    """Validation tests for Command models."""

    def test_create_accepts_valid_command(self) -> None:
        cmd = CommandCreate(label="Run tests", command="uv run pytest")
        assert cmd.label == "Run tests"
        assert cmd.command == "uv run pytest"

    def test_create_rejects_empty_label(self) -> None:
        with pytest.raises(ValidationError):
            CommandCreate(label="", command="uv run pytest")

    def test_create_rejects_empty_command(self) -> None:
        with pytest.raises(ValidationError):
            CommandCreate(label="Run tests", command="")


# ═══════════════════════════════════════════════════════════════════════════
# Project task (checklist) models
# ═══════════════════════════════════════════════════════════════════════════

class TestProjectTaskModels:
    """Validation tests for checklist Task models."""

    def test_create_accepts_valid_title(self) -> None:
        task = ProjectTaskCreate(title="Implement feature")
        assert task.title == "Implement feature"

    def test_create_rejects_empty_title(self) -> None:
        with pytest.raises(ValidationError):
            ProjectTaskCreate(title="")

    def test_create_rejects_overlength_title(self) -> None:
        with pytest.raises(ValidationError):
            ProjectTaskCreate(title="x" * 501)


# ═══════════════════════════════════════════════════════════════════════════
# Template models
# ═══════════════════════════════════════════════════════════════════════════

class TestTemplateModels:
    """Validation tests for Template models."""

    def test_create_minimal(self) -> None:
        tmpl = TemplateCreate(name="Quick CLI")
        assert tmpl.name == "Quick CLI"
        assert tmpl.default_status == "idea"

    def test_create_full(self) -> None:
        tmpl = TemplateCreate(
            name="Full Stack",
            description="Template for full-stack projects",
            default_status="active",
            default_project_type="web-app",
            default_primary_language="Python",
            default_stack="FastAPI + React",
            default_scope_size="long-haul",
            default_learning_goal="Deployable SaaS",
            default_tags="fullstack,python",
        )
        assert tmpl.default_project_type == "web-app"
        assert tmpl.default_tags == "fullstack,python"

    def test_create_rejects_invalid_status(self) -> None:
        with pytest.raises(ValidationError):
            TemplateCreate(name="Bad", default_status="draft")

    def test_create_rejects_invalid_scope_size(self) -> None:
        with pytest.raises(ValidationError):
            TemplateCreate(name="Bad", default_scope_size="massive")

    def test_update_all_optional(self) -> None:
        update = TemplateUpdate()
        assert update.name is None
        assert update.default_status is None

    def test_update_rejects_invalid_project_type(self) -> None:
        with pytest.raises(ValidationError):
            TemplateUpdate(default_project_type="invalid-type")


# ═══════════════════════════════════════════════════════════════════════════
# Project edge cases (supplementing existing test_project_types.py)
# ═══════════════════════════════════════════════════════════════════════════

class TestProjectEdgeCases:
    """Edge-case validation for Project models not covered elsewhere."""

    def test_progress_min_boundary(self) -> None:
        p = ProjectBase(name="Test", progress=0)
        assert p.progress == 0

    def test_progress_max_boundary(self) -> None:
        p = ProjectBase(name="Test", progress=100)
        assert p.progress == 100

    def test_progress_rejects_negative(self) -> None:
        with pytest.raises(ValidationError):
            ProjectBase(name="Test", progress=-1)

    def test_progress_rejects_over_100(self) -> None:
        with pytest.raises(ValidationError):
            ProjectBase(name="Test", progress=101)

    def test_name_rejects_empty(self) -> None:
        with pytest.raises(ValidationError):
            ProjectBase(name="")

    @pytest.mark.parametrize("status", ["idea", "active", "paused", "archived"])
    def test_valid_statuses(self, status: str) -> None:
        p = ProjectBase(name="Test", status=status)
        assert p.status == status

    def test_rejects_invalid_status(self) -> None:
        with pytest.raises(ValidationError):
            ProjectBase(name="Test", status="deleted")

    @pytest.mark.parametrize("scope", ["tiny", "medium", "long-haul"])
    def test_valid_scope_sizes(self, scope: str) -> None:
        p = ProjectBase(name="Test", scope_size=scope)
        assert p.scope_size == scope

    def test_rejects_invalid_scope_size(self) -> None:
        with pytest.raises(ValidationError):
            ProjectBase(name="Test", scope_size="huge")

    def test_update_all_none_is_valid(self) -> None:
        update = ProjectUpdate()
        assert update.name is None
        assert update.status is None
        assert update.progress is None


# ═══════════════════════════════════════════════════════════════════════════
# Analytics / Graph / misc response models
# ═══════════════════════════════════════════════════════════════════════════

class TestAnalyticsAndGraphModels:
    """Basic instantiation tests for analytics and graph models."""

    def test_analytics_summary_defaults(self) -> None:
        summary = AnalyticsSummary()
        assert summary.total == 0
        assert summary.avg_progress == 0.0

    def test_analytics_chart_item(self) -> None:
        item = AnalyticsChartItem(label="Python", value=5)
        assert item.label == "Python"

    def test_graph_node(self) -> None:
        node = GraphNode(id=1, label="ContextGrid", status="active")
        assert node.project_type is None

    def test_graph_edge(self) -> None:
        edge = GraphEdge(source=1, target=2, relationship_type="depends_on")
        assert edge.is_inferred is False

    def test_graph_edge_inferred(self) -> None:
        edge = GraphEdge(source=1, target=2, relationship_type="shared_tag", is_inferred=True)
        assert edge.is_inferred is True

    def test_screenshot_response(self) -> None:
        ss = ScreenshotResponse(filename="shot.png", url="/uploads/1/shot.png", label="shot")
        assert ss.is_cover is False

    def test_cover_request(self) -> None:
        cr = CoverRequest(filename="cover.png")
        assert cr.filename == "cover.png"

    def test_mermaid_response(self) -> None:
        mr = MermaidResponse(diagram="graph TD; A-->B", diagram_type="flowchart")
        assert "A-->B" in mr.diagram

    def test_health_response(self) -> None:
        hr = HealthResponse(status="ok", message="Running")
        assert hr.status == "ok"

    def test_message_response(self) -> None:
        mr = MessageResponse(message="Done")
        assert mr.message == "Done"

    def test_touch_response(self) -> None:
        tr = TouchResponse(message="Updated", last_worked_at="2026-01-01T12:00:00")
        assert tr.last_worked_at == "2026-01-01T12:00:00"
