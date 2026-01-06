"""
Database query layer for ContextGrid projects.
Handles all CRUD operations for projects table.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from db import get_connection


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
    
    Args:
        name: Project name (required)
        status: One of: idea, active, paused, archived (default: idea)
        description: Project description
        project_type: One of: web, cli, library, homelab, research
        primary_language: Main programming language
        stack: Technology stack description
        repo_url: Git repository URL
        local_path: Local filesystem path
        scope_size: One of: tiny, medium, long-haul
        learning_goal: What you're trying to learn
    
    Returns:
        The new project's ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    created_at = datetime.utcnow().isoformat()
    
    cursor.execute(
        """
        INSERT INTO projects (
            name, description, status, project_type,
            primary_language, stack, repo_url, local_path,
            scope_size, learning_goal, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name, description, status, project_type,
            primary_language, stack, repo_url, local_path,
            scope_size, learning_goal, created_at
        ),
    )
    
    conn.commit()
    project_id = cursor.lastrowid
    conn.close()
    
    return project_id


def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single project by ID.
    
    Args:
        project_id: The project's ID
    
    Returns:
        Dictionary of project fields, or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def list_projects(
    status: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort_by: str = "last_worked_at",
    sort_order: str = "desc"
) -> List[Dict[str, Any]]:
    """
    List all projects, optionally filtered by status.
    
    Args:
        status: Filter by status (idea, active, paused, archived)
        limit: Maximum number of projects to return (for pagination)
        offset: Number of projects to skip (for pagination)
        sort_by: Field to sort by (name, created_at, last_worked_at, status)
        sort_order: Sort order (asc or desc)
    
    Returns:
        List of project dictionaries, ordered by the specified sort criteria
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Validate sort parameters
    valid_sort_fields = ["name", "created_at", "last_worked_at", "status"]
    if sort_by not in valid_sort_fields:
        sort_by = "last_worked_at"
    
    sort_order = sort_order.lower()
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"
    
    # Build the query
    query = "SELECT * FROM projects WHERE is_archived = 0"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    # Add ORDER BY clause
    # Handle NULL values in last_worked_at by treating them as very old
    if sort_by == "last_worked_at":
        query += f" ORDER BY CASE WHEN last_worked_at IS NULL THEN 0 ELSE 1 END {sort_order.upper()}, last_worked_at {sort_order.upper()}"
    else:
        query += f" ORDER BY {sort_by} {sort_order.upper()}"
    
    # Add secondary sort by created_at for consistency
    if sort_by != "created_at":
        query += ", created_at DESC"
    
    # Add pagination
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
        
        if offset is not None:
            query += " OFFSET ?"
            params.append(offset)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_project(project_id: int, **kwargs) -> bool:
    """
    Update project fields.
    
    Args:
        project_id: The project's ID
        **kwargs: Fields to update (name, description, status, etc.)
    
    Returns:
        True if project was updated, False if not found
    """
    if not kwargs:
        return False
    
    # Build dynamic UPDATE query
    valid_fields = {
        "name", "description", "status", "project_type",
        "primary_language", "stack", "repo_url", "local_path",
        "scope_size", "learning_goal", "is_archived"
    }
    
    # Filter to valid fields only
    updates = {k: v for k, v in kwargs.items() if k in valid_fields}
    
    if not updates:
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build SET clause
    set_clause = ", ".join(f"{field} = ?" for field in updates.keys())
    values = list(updates.values()) + [project_id]
    
    cursor.execute(
        f"UPDATE projects SET {set_clause} WHERE id = ?",
        values
    )
    
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    return rows_affected > 0


def update_last_worked(project_id: int) -> bool:
    """
    Update the last_worked_at timestamp for a project.
    
    Args:
        project_id: The project's ID
    
    Returns:
        True if updated, False if project not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    cursor.execute(
        "UPDATE projects SET last_worked_at = ? WHERE id = ?",
        (now, project_id)
    )
    
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    return rows_affected > 0


# =========================
# Project Notes Functions
# =========================

def create_note(project_id: int, content: str, note_type: str = "log") -> int:
    """
    Create a new note for a project.
    
    Args:
        project_id: The project's ID
        content: Note content
        note_type: One of: log, idea, blocker, reflection (default: log)
    
    Returns:
        The new note's ID
    
    Raises:
        ValueError: If note_type is not valid
    """
    # Validate note_type
    valid_types = ["log", "idea", "blocker", "reflection"]
    if note_type not in valid_types:
        raise ValueError(f"Invalid note_type: {note_type}. Must be one of: {', '.join(valid_types)}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    created_at = datetime.utcnow().isoformat()
    
    cursor.execute(
        """
        INSERT INTO project_notes (project_id, note_type, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (project_id, note_type, content, created_at)
    )
    
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    
    return note_id


def list_notes(project_id: int, note_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all notes for a project, optionally filtered by type.
    
    Args:
        project_id: The project's ID
        note_type: Optional filter by note type
    
    Returns:
        List of note dictionaries, ordered by created_at DESC
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if note_type:
        cursor.execute(
            """
            SELECT * FROM project_notes
            WHERE project_id = ? AND note_type = ?
            ORDER BY created_at DESC
            """,
            (project_id, note_type)
        )
    else:
        cursor.execute(
            """
            SELECT * FROM project_notes
            WHERE project_id = ?
            ORDER BY created_at DESC
            """,
            (project_id,)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_note(note_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single note by ID.
    
    Args:
        note_id: The note's ID
    
    Returns:
        Dictionary of note fields, or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM project_notes WHERE id = ?",
        (note_id,)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def delete_note(note_id: int) -> bool:
    """
    Delete a note by ID.
    
    Args:
        note_id: The note's ID
    
    Returns:
        True if deleted, False if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM project_notes WHERE id = ?",
        (note_id,)
    )
    
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    return rows_affected > 0


def get_recent_notes(project_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the N most recent notes for a project.
    
    Args:
        project_id: The project's ID
        limit: Maximum number of notes to return (default: 5)
    
    Returns:
        List of note dictionaries, ordered by created_at DESC
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT * FROM project_notes
        WHERE project_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (project_id, limit)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# =========================
# Tag Management Functions
# =========================

def get_or_create_tag(tag_name: str) -> int:
    """
    Get a tag ID by name, or create it if it doesn't exist.
    
    Args:
        tag_name: The tag name
    
    Returns:
        The tag's ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Try to find existing tag
    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
    row = cursor.fetchone()
    
    if row:
        tag_id = row['id']
        conn.close()
        return tag_id
    
    # Create new tag
    cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
    conn.commit()
    tag_id = cursor.lastrowid
    conn.close()
    
    return tag_id


def add_tag_to_project(project_id: int, tag_name: str) -> bool:
    """
    Add a tag to a project.
    
    Args:
        project_id: The project's ID
        tag_name: The tag name
    
    Returns:
        True if tag was added, False if it was already present
    """
    tag_id = get_or_create_tag(tag_name)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if already exists
    cursor.execute(
        "SELECT 1 FROM project_tags WHERE project_id = ? AND tag_id = ?",
        (project_id, tag_id)
    )
    
    if cursor.fetchone():
        conn.close()
        return False  # Already exists
    
    # Add the tag
    cursor.execute(
        "INSERT INTO project_tags (project_id, tag_id) VALUES (?, ?)",
        (project_id, tag_id)
    )
    
    conn.commit()
    conn.close()
    return True


def remove_tag_from_project(project_id: int, tag_name: str) -> bool:
    """
    Remove a tag from a project.
    
    Args:
        project_id: The project's ID
        tag_name: The tag name
    
    Returns:
        True if tag was removed, False if it wasn't found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Find the tag ID
    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return False
    
    tag_id = row['id']
    
    # Remove the association
    cursor.execute(
        "DELETE FROM project_tags WHERE project_id = ? AND tag_id = ?",
        (project_id, tag_id)
    )
    
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    return rows_affected > 0


def list_project_tags(project_id: int) -> List[str]:
    """
    Get all tags for a specific project.
    
    Args:
        project_id: The project's ID
    
    Returns:
        List of tag names
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT tags.name
        FROM tags
        JOIN project_tags ON tags.id = project_tags.tag_id
        WHERE project_tags.project_id = ?
        ORDER BY tags.name
        """,
        (project_id,)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [row['name'] for row in rows]


def list_all_tags() -> List[Dict[str, Any]]:
    """
    Get all tags with project counts.
    
    Returns:
        List of dictionaries with 'name' and 'project_count' fields
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT 
            tags.name,
            COUNT(project_tags.project_id) as project_count
        FROM tags
        LEFT JOIN project_tags ON tags.id = project_tags.tag_id
        GROUP BY tags.id, tags.name
        ORDER BY tags.name
        """
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{'name': row['name'], 'project_count': row['project_count']} for row in rows]


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
    
    Args:
        tag_name: The tag name to filter by
        status: Optional status filter
        limit: Maximum number of projects to return (for pagination)
        offset: Number of projects to skip (for pagination)
        sort_by: Field to sort by (name, created_at, last_worked_at, status)
        sort_order: Sort order (asc or desc)
    
    Returns:
        List of project dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Validate sort parameters
    valid_sort_fields = ["name", "created_at", "last_worked_at", "status"]
    if sort_by not in valid_sort_fields:
        sort_by = "last_worked_at"
    
    sort_order = sort_order.lower()
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"
    
    query = """
        SELECT DISTINCT projects.*
        FROM projects
        JOIN project_tags ON projects.id = project_tags.project_id
        JOIN tags ON project_tags.tag_id = tags.id
        WHERE tags.name = ? AND projects.is_archived = 0
    """
    params = [tag_name]
    
    if status:
        query += " AND projects.status = ?"
        params.append(status)
    
    # Add ORDER BY clause
    if sort_by == "last_worked_at":
        query += f" ORDER BY CASE WHEN projects.last_worked_at IS NULL THEN 0 ELSE 1 END {sort_order.upper()}, projects.last_worked_at {sort_order.upper()}"
    else:
        query += f" ORDER BY projects.{sort_by} {sort_order.upper()}"
    
    # Add secondary sort
    if sort_by != "created_at":
        query += ", projects.created_at DESC"
    
    # Add pagination
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
        
        if offset is not None:
            query += " OFFSET ?"
            params.append(offset)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def search_projects(query: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for projects across multiple text fields.
    
    Args:
        query: Search query string (case-insensitive)
        status: Optional status filter
    
    Returns:
        List of project dictionaries matching the search query
    """
    if not query or not query.strip():
        return list_projects(status=status)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build search pattern for LIKE queries
    search_pattern = f"%{query}%"
    
    # Build the SQL query to search across multiple fields
    sql = """
        SELECT DISTINCT projects.*
        FROM projects
        LEFT JOIN project_tags ON projects.id = project_tags.project_id
        LEFT JOIN tags ON project_tags.tag_id = tags.id
        LEFT JOIN project_notes ON projects.id = project_notes.project_id
        WHERE projects.is_archived = 0
        AND (
            projects.name LIKE ? COLLATE NOCASE
            OR projects.description LIKE ? COLLATE NOCASE
            OR projects.primary_language LIKE ? COLLATE NOCASE
            OR projects.stack LIKE ? COLLATE NOCASE
            OR projects.learning_goal LIKE ? COLLATE NOCASE
            OR projects.project_type LIKE ? COLLATE NOCASE
            OR tags.name LIKE ? COLLATE NOCASE
            OR project_notes.content LIKE ? COLLATE NOCASE
        )
    """
    
    params = [search_pattern] * 8  # 8 fields to search
    
    if status:
        sql += " AND projects.status = ?"
        params.append(status)
    
    sql += " ORDER BY projects.last_worked_at DESC, projects.created_at DESC"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_projects_count(status: Optional[str] = None, tag: Optional[str] = None, search: Optional[str] = None) -> int:
    """
    Get the total count of projects matching the given filters.
    
    Args:
        status: Optional status filter
        tag: Optional tag filter
        search: Optional search query
    
    Returns:
        Total count of projects matching the filters
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if search and search.strip():
        # Count search results
        search_pattern = f"%{search}%"
        sql = """
            SELECT COUNT(DISTINCT projects.id)
            FROM projects
            LEFT JOIN project_tags ON projects.id = project_tags.project_id
            LEFT JOIN tags ON project_tags.tag_id = tags.id
            LEFT JOIN project_notes ON projects.id = project_notes.project_id
            WHERE projects.is_archived = 0
            AND (
                projects.name LIKE ? COLLATE NOCASE
                OR projects.description LIKE ? COLLATE NOCASE
                OR projects.primary_language LIKE ? COLLATE NOCASE
                OR projects.stack LIKE ? COLLATE NOCASE
                OR projects.learning_goal LIKE ? COLLATE NOCASE
                OR projects.project_type LIKE ? COLLATE NOCASE
                OR tags.name LIKE ? COLLATE NOCASE
                OR project_notes.content LIKE ? COLLATE NOCASE
            )
        """
        params = [search_pattern] * 8
        
        if status:
            sql += " AND projects.status = ?"
            params.append(status)
        
        cursor.execute(sql, params)
    elif tag:
        # Count by tag
        sql = """
            SELECT COUNT(DISTINCT projects.id)
            FROM projects
            JOIN project_tags ON projects.id = project_tags.project_id
            JOIN tags ON project_tags.tag_id = tags.id
            WHERE tags.name = ? AND projects.is_archived = 0
        """
        params = [tag]
        
        if status:
            sql += " AND projects.status = ?"
            params.append(status)
        
        cursor.execute(sql, params)
    else:
        # Count all projects
        if status:
            cursor.execute(
                "SELECT COUNT(*) FROM projects WHERE status = ? AND is_archived = 0",
                (status,)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM projects WHERE is_archived = 0")
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count

