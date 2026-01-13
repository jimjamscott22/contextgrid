"""
Database query layer for ContextGrid projects.
This module provides a unified interface that delegates to the API client.

All functions maintain the same signatures as the original SQLite implementation
for backward compatibility.
"""

from typing import Optional, List, Dict, Any
from api_client import get_api_client, APIError


# Get the API client
_client = get_api_client()


def _handle_api_error(e: APIError):
    """Convert API errors to standard exceptions."""
    raise Exception(str(e))


# =========================
# Project Functions
# =========================

def create_project(
    name: str,
    status: str = "idea",
    description: Optional[str] = None,
    project_type: Optional[str] = None,
    primary_language: Optional[str] = None,
    stack: Optional[str] = None,
    repo_url: Optional[str] = None,
    local_path: Optional[str] = None,
    scope_size: Optional[str] = None,
    learning_goal: Optional[str] = None,
) -> int:
    """
    Create a new project and return its ID.
    """
    try:
        return _client.create_project(
            name=name,
            description=description,
            status=status,
            project_type=project_type,
            primary_language=primary_language,
            stack=stack,
            repo_url=repo_url,
            local_path=local_path,
            scope_size=scope_size,
            learning_goal=learning_goal
        )
    except APIError as e:
        _handle_api_error(e)


def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single project by ID.
    """
    try:
        return _client.get_project(project_id)
    except APIError as e:
        _handle_api_error(e)


def list_projects(
    status: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort_by: str = "last_worked_at",
    sort_order: str = "desc"
) -> List[Dict[str, Any]]:
    """
    List all projects, optionally filtered by status.
    """
    try:
        return _client.list_projects(
            status=status,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except APIError as e:
        _handle_api_error(e)


def update_project(project_id: int, **kwargs) -> bool:
    """
    Update project fields.
    """
    try:
        return _client.update_project(project_id, **kwargs)
    except APIError as e:
        _handle_api_error(e)


def update_last_worked(project_id: int) -> bool:
    """
    Update the last_worked_at timestamp for a project.
    """
    try:
        return _client.update_last_worked(project_id)
    except APIError as e:
        _handle_api_error(e)


# =========================
# Project Notes Functions
# =========================

def create_note(project_id: int, content: str, note_type: str = "log") -> int:
    """
    Create a new note for a project.
    """
    # Validate note_type
    valid_types = ["log", "idea", "blocker", "reflection"]
    if note_type not in valid_types:
        raise ValueError(f"Invalid note_type: {note_type}. Must be one of: {', '.join(valid_types)}")
    
    try:
        return _client.create_note(project_id, content, note_type)
    except APIError as e:
        _handle_api_error(e)


def list_notes(project_id: int, note_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all notes for a project, optionally filtered by type.
    """
    try:
        return _client.list_notes(project_id, note_type)
    except APIError as e:
        _handle_api_error(e)


def get_note(note_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single note by ID.
    """
    try:
        return _client.get_note(note_id)
    except APIError as e:
        _handle_api_error(e)


def delete_note(note_id: int) -> bool:
    """
    Delete a note by ID.
    """
    try:
        return _client.delete_note(note_id)
    except APIError as e:
        _handle_api_error(e)


def get_recent_notes(project_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the N most recent notes for a project.
    """
    try:
        return _client.get_recent_notes(project_id, limit)
    except APIError as e:
        _handle_api_error(e)


# =========================
# Tag Management Functions
# =========================

def get_or_create_tag(tag_name: str) -> int:
    """
    Get a tag ID by name, or create it if it doesn't exist.
    Note: This is not directly supported by the API, so we'll just add the tag.
    """
    # Not needed with API - tags are created automatically
    return 0


def add_tag_to_project(project_id: int, tag_name: str) -> bool:
    """
    Add a tag to a project.
    """
    try:
        return _client.add_tag_to_project(project_id, tag_name)
    except APIError as e:
        _handle_api_error(e)


def remove_tag_from_project(project_id: int, tag_name: str) -> bool:
    """
    Remove a tag from a project.
    """
    try:
        return _client.remove_tag_from_project(project_id, tag_name)
    except APIError as e:
        _handle_api_error(e)


def list_project_tags(project_id: int) -> List[str]:
    """
    Get all tags for a specific project.
    """
    try:
        return _client.list_project_tags(project_id)
    except APIError as e:
        _handle_api_error(e)


def list_all_tags() -> List[Dict[str, Any]]:
    """
    Get all tags with project counts.
    """
    try:
        return _client.list_all_tags()
    except APIError as e:
        _handle_api_error(e)


def list_projects_by_tag(
    tag_name: str,
    status: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort_by: str = "last_worked_at",
    sort_order: str = "desc"
) -> List[Dict[str, Any]]:
    """
    List all projects that have a specific tag.
    """
    try:
        return _client.list_projects(
            status=status,
            tag=tag_name,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except APIError as e:
        _handle_api_error(e)


def search_projects(
    query: str,
    status: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort_by: str = "last_worked_at",
    sort_order: str = "desc"
) -> List[Dict[str, Any]]:
    """
    Search for projects across multiple text fields.
    Note: This is not implemented in the API yet, so we'll just list all projects.
    """
    # TODO: Implement search in API
    try:
        return _client.list_projects(
            status=status,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except APIError as e:
        _handle_api_error(e)


def get_projects_count(status: Optional[str] = None, tag: Optional[str] = None, search: Optional[str] = None) -> int:
    """
    Get the total count of projects matching the given filters.
    Note: API returns all matching projects, so we count them.
    """
    try:
        projects = _client.list_projects(status=status, tag=tag)
        return len(projects)
    except APIError as e:
        _handle_api_error(e)
