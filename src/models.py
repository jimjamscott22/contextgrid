"""
Database query layer for ContextGrid projects.
This module provides a unified interface that works in both API mode and direct database mode.

When USE_API=true: Delegates to API client (makes HTTP requests)
When USE_API=false: Uses direct database access via database backend

All functions maintain the same signatures for backward compatibility.
"""

import os
import sys
from typing import Optional, List, Dict, Any

# Import configuration
from config import config

# Conditional imports based on mode
if config.USE_API:
    from api_client import get_api_client, APIError
    _client = get_api_client()
    _db_backend = None
else:
    from db import get_database_backend
    _client = None
    _db_backend = get_database_backend()
    # Initialize database on first use
    try:
        _db_backend.initialize_database()
    except Exception as e:
        # Log error but continue - database may already be initialized
        print(f"Warning: Database initialization encountered an issue: {e}", file=sys.stderr)
        # Try to test connection to verify database is accessible
        success, error = _db_backend.test_connection()
        if not success:
            raise Exception(f"Cannot connect to database: {error}")


def _handle_error(e: Exception):
    """Convert errors to standard exceptions."""
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
        if config.USE_API:
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
        else:
            return _db_backend.create_project(
                name=name,
                status=status,
                description=description,
                project_type=project_type,
                primary_language=primary_language,
                stack=stack,
                repo_url=repo_url,
                local_path=local_path,
                scope_size=scope_size,
                learning_goal=learning_goal
            )
    except Exception as e:
        _handle_error(e)


def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single project by ID.
    """
    try:
        if config.USE_API:
            return _client.get_project(project_id)
        else:
            return _db_backend.get_project(project_id)
    except Exception as e:
        _handle_error(e)


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
        if config.USE_API:
            return _client.list_projects(
                status=status,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order
            )
        else:
            return _db_backend.list_projects(
                status=status,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order
            )
    except Exception as e:
        _handle_error(e)


def update_project(project_id: int, **kwargs) -> bool:
    """
    Update project fields.
    """
    try:
        if config.USE_API:
            return _client.update_project(project_id, **kwargs)
        else:
            return _db_backend.update_project(project_id, **kwargs)
    except Exception as e:
        _handle_error(e)


def update_last_worked(project_id: int) -> bool:
    """
    Update the last_worked_at timestamp for a project.
    """
    try:
        if config.USE_API:
            return _client.update_last_worked(project_id)
        else:
            success, _ = _db_backend.update_last_worked(project_id)
            return success
    except Exception as e:
        _handle_error(e)


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
        if config.USE_API:
            return _client.create_note(project_id, content, note_type)
        else:
            return _db_backend.create_note(project_id, content, note_type)
    except Exception as e:
        _handle_error(e)


def list_notes(project_id: int, note_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all notes for a project, optionally filtered by type.
    """
    try:
        if config.USE_API:
            return _client.list_notes(project_id, note_type)
        else:
            notes = _db_backend.list_notes(project_id)
            # Filter by note_type if specified
            if note_type:
                notes = [n for n in notes if n['note_type'] == note_type]
            return notes
    except Exception as e:
        _handle_error(e)


def get_note(note_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single note by ID.
    """
    try:
        if config.USE_API:
            return _client.get_note(note_id)
        else:
            return _db_backend.get_note(note_id)
    except Exception as e:
        _handle_error(e)


def delete_note(note_id: int) -> bool:
    """
    Delete a note by ID.
    """
    try:
        if config.USE_API:
            return _client.delete_note(note_id)
        else:
            return _db_backend.delete_note(note_id)
    except Exception as e:
        _handle_error(e)


def get_recent_notes(project_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the N most recent notes for a project.
    """
    try:
        if config.USE_API:
            return _client.get_recent_notes(project_id, limit)
        else:
            notes = _db_backend.list_notes(project_id)
            return notes[:limit]
    except Exception as e:
        _handle_error(e)


# =========================
# Tag Management Functions
# =========================

def get_or_create_tag(tag_name: str) -> int:
    """
    Get a tag ID by name, or create it if it doesn't exist.
    Note: In API mode, tags are created automatically.
    """
    if config.USE_API:
        # Not needed with API - tags are created automatically
        return 0
    else:
        try:
            return _db_backend.get_or_create_tag(tag_name)
        except Exception as e:
            _handle_error(e)


def add_tag_to_project(project_id: int, tag_name: str) -> bool:
    """
    Add a tag to a project.
    """
    try:
        if config.USE_API:
            return _client.add_tag_to_project(project_id, tag_name)
        else:
            return _db_backend.add_tag_to_project(project_id, tag_name)
    except Exception as e:
        _handle_error(e)


def remove_tag_from_project(project_id: int, tag_name: str) -> bool:
    """
    Remove a tag from a project.
    """
    try:
        if config.USE_API:
            return _client.remove_tag_from_project(project_id, tag_name)
        else:
            return _db_backend.remove_tag_from_project(project_id, tag_name)
    except Exception as e:
        _handle_error(e)


def list_project_tags(project_id: int) -> List[str]:
    """
    Get all tags for a specific project.
    """
    try:
        if config.USE_API:
            return _client.list_project_tags(project_id)
        else:
            return _db_backend.list_project_tags(project_id)
    except Exception as e:
        _handle_error(e)


def list_all_tags() -> List[Dict[str, Any]]:
    """
    Get all tags with project counts.
    """
    try:
        if config.USE_API:
            return _client.list_all_tags()
        else:
            return _db_backend.list_all_tags()
    except Exception as e:
        _handle_error(e)


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
        if config.USE_API:
            return _client.list_projects(
                status=status,
                tag=tag_name,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order
            )
        else:
            return _db_backend.list_projects(
                status=status,
                tag=tag_name,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order
            )
    except Exception as e:
        _handle_error(e)


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
    Note: This is not fully implemented yet, so we'll just list all projects.
    """
    # TODO: Implement full-text search
    try:
        if config.USE_API:
            return _client.list_projects(
                status=status,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order
            )
        else:
            return _db_backend.list_projects(
                status=status,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order
            )
    except Exception as e:
        _handle_error(e)


def get_projects_count(status: Optional[str] = None, tag: Optional[str] = None, search: Optional[str] = None) -> int:
    """
    Get the total count of projects matching the given filters.
    """
    try:
        if config.USE_API:
            projects = _client.list_projects(status=status, tag=tag)
            return len(projects)
        else:
            projects = _db_backend.list_projects(status=status, tag=tag)
            return len(projects)
    except Exception as e:
        _handle_error(e)
