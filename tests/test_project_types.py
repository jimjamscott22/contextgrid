"""Project type validation and migration tests."""

import re
from pathlib import Path
from typing import Any, Dict, Type

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError

from api.models import ProjectCreate, ProjectUpdate, TemplateCreate, TemplateUpdate
from src.project_types import LEGACY_PROJECT_TYPE_MAP, PROJECT_TYPE_LABELS
from web.app import app as legacy_app, templates as legacy_templates


PROJECT_TYPES = (
    "web-app",
    "cli",
    "documentation",
    "college",
    "desktop-app",
    "pwa",
    "llm-integrated",
    "website",
)

REMOVED_PROJECT_TYPES = (
    "web",
    "library",
    "school",
    "homelab",
    "desktop",
    "other",
)

MODEL_FIELDS = (
    (ProjectCreate, "project_type", {"name": "Test"}),
    (ProjectUpdate, "project_type", {}),
    (TemplateCreate, "default_project_type", {"name": "Test"}),
    (TemplateUpdate, "default_project_type", {}),
)


@pytest.mark.parametrize("model_class,field_name,base_values", MODEL_FIELDS)
@pytest.mark.parametrize("project_type", PROJECT_TYPES)
def test_project_models_accept_canonical_types(
    model_class: Type[BaseModel],
    field_name: str,
    base_values: Dict[str, Any],
    project_type: str,
) -> None:
    """Project and template models should accept every canonical type."""
    values = dict(base_values)
    values[field_name] = project_type

    model = model_class(**values)

    assert getattr(model, field_name) == project_type


@pytest.mark.parametrize("model_class,field_name,base_values", MODEL_FIELDS)
@pytest.mark.parametrize("project_type", REMOVED_PROJECT_TYPES)
def test_project_models_reject_removed_types(
    model_class: Type[BaseModel],
    field_name: str,
    base_values: Dict[str, Any],
    project_type: str,
) -> None:
    """Removed project type values should no longer pass API validation."""
    values = dict(base_values)
    values[field_name] = project_type

    with pytest.raises(ValidationError):
        model_class(**values)


def test_legacy_project_type_map_matches_expected_mapping() -> None:
    """LEGACY_PROJECT_TYPE_MAP should match the documented legacy->canonical mapping."""
    legacy_mapping = {
        "web": "web-app",
        "cli": "cli",
        "library": "documentation",
        "school": "college",
        "homelab": "desktop-app",
        "desktop": "pwa",
        "llm-integrated": "llm-integrated",
        "other": "website",
    }
    assert LEGACY_PROJECT_TYPE_MAP == legacy_mapping


def test_mysql_schema_migration_covers_every_legacy_project_type() -> None:
    """The idempotent MySQL/MariaDB migration in init_mysql.sql should stay in
    sync with LEGACY_PROJECT_TYPE_MAP so a schema init never silently drops a
    legacy->canonical mapping.

    Note: this is a static consistency check against the SQL text rather than
    a live-database migration test. Exercising initialize_database() against
    a real server requires a live MySQL/MariaDB connection (SQLite, which
    previously let this run against a disposable temp-file database, has been
    removed) and is out of scope for unit tests.
    """
    schema_path = (
        Path(__file__).resolve().parent.parent / "scripts" / "init_mysql.sql"
    )
    schema_sql = schema_path.read_text(encoding="utf-8")

    for legacy_type, canonical_type in LEGACY_PROJECT_TYPE_MAP.items():
        if legacy_type == canonical_type:
            continue  # not actually a rename, nothing to migrate
        assert f"WHEN '{legacy_type}' THEN '{canonical_type}'" in schema_sql, (
            f"init_mysql.sql is missing a migration case for legacy type "
            f"'{legacy_type}' -> '{canonical_type}'"
        )


def test_legacy_new_project_form_uses_canonical_types() -> None:
    """The legacy create form should expose the same ordered type options."""
    with TestClient(legacy_app) as client:
        response = client.get("/projects/new")

    assert response.status_code == 200
    select = re.search(
        r'<select id="project_type".*?</select>',
        response.text,
        re.DOTALL,
    )
    assert select is not None
    options = re.findall(
        r'<option value="([^"]*)"[^>]*>([^<]*)</option>',
        select.group(0),
    )
    assert options == [
        ("", "Select type..."),
        ("web-app", "Web App"),
        ("cli", "CLI"),
        ("documentation", "Documentation"),
        ("college", "College"),
        ("desktop-app", "Desktop"),
        ("pwa", "PWA"),
        ("llm-integrated", "LLM-based/integrated"),
        ("website", "Website"),
    ]


def test_all_legacy_templates_compile() -> None:
    """Every legacy template should compile after adding shared globals."""
    for template_name in legacy_templates.env.list_templates():
        legacy_templates.get_template(template_name)


def test_backend_project_type_labels_are_exact_and_ordered() -> None:
    """Backend labels should match the public selector copy and ordering."""
    assert list(PROJECT_TYPE_LABELS.items()) == [
        ("web-app", "Web App"),
        ("cli", "CLI"),
        ("documentation", "Documentation"),
        ("college", "College"),
        ("desktop-app", "Desktop"),
        ("pwa", "PWA"),
        ("llm-integrated", "LLM-based/integrated"),
        ("website", "Website"),
    ]
