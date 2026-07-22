"""Canonical project type values and display labels."""

import re
from typing import Dict, Optional, Tuple


PROJECT_TYPE_VALUES: Tuple[str, ...] = (
    "web-app",
    "cli",
    "documentation",
    "college",
    "desktop-app",
    "pwa",
    "llm-integrated",
    "website",
)

PROJECT_TYPE_LABELS: Dict[str, str] = {
    "web-app": "Web App",
    "cli": "CLI",
    "documentation": "Documentation",
    "college": "College",
    "desktop-app": "Desktop",
    "pwa": "PWA",
    "llm-integrated": "LLM-based/integrated",
    "website": "Website",
}

LEGACY_PROJECT_TYPE_MAP: Dict[str, str] = {
    "web": "web-app",
    "cli": "cli",
    "library": "documentation",
    "school": "college",
    "homelab": "desktop-app",
    "desktop": "pwa",
    "llm-integrated": "llm-integrated",
    "other": "website",
}

PROJECT_TYPE_PATTERN = "^(?:" + "|".join(
    re.escape(value) for value in PROJECT_TYPE_VALUES
) + ")?$"


def project_type_label(project_type: Optional[str]) -> Optional[str]:
    """Return the friendly label for a canonical project type."""
    if project_type is None:
        return None
    return PROJECT_TYPE_LABELS.get(project_type, project_type)
