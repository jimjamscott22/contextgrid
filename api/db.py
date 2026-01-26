"""
MySQL database layer for ContextGrid API.
Handles all database operations using PyMySQL.
"""

import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from api.config import config


# =========================
# Connection Management
# =========================

def get_connection():
    """
    Get a MySQL database connection.
    
    Returns:
        pymysql.Connection: Database connection
    """
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        charset='utf8mb4',
        cursorclass=DictCursor,
        autocommit=False
    )


@contextmanager
def get_db_cursor():
    """
    Context manager for database cursor.
    Automatically handles connection and commit/rollback.
    
    Yields:
        pymysql.cursors.DictCursor: Database cursor
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def initialize_database():
    """
    Initialize the database schema.
    Creates all tables if they don't exist.
    """
    schema_path = Path(__file__).parent.parent / "scripts" / "init_mysql.sql"
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Split by semicolons and execute each statement
    statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
    
    with get_db_cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)


def test_connection() -> tuple[bool, Optional[str]]:
    """
    Test the database connection.
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)


# =========================
# Project Operations
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
    Create a new project.
    
    Returns:
        The new project's ID
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO projects (
                name, description, status, project_type,
                primary_language, stack, repo_url, local_path,
                scope_size, learning_goal, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                name, description, status, project_type,
                primary_language, stack, repo_url, local_path,
                scope_size, learning_goal, datetime.utcnow()
            )
        )
        return cursor.lastrowid


def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single project by ID.
    
    Returns:
        Dictionary of project fields, or None if not found
    """
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
        row = cursor.fetchone()
        if row:
            # Convert datetime objects to ISO format strings
            if row['created_at']:
                row['created_at'] = row['created_at'].isoformat()
            if row['last_worked_at']:
                row['last_worked_at'] = row['last_worked_at'].isoformat()
        return row


def list_projects(
    status: Optional[str] = None,
    tag: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort_by: str = "last_worked_at",
    sort_order: str = "desc"
) -> List[Dict[str, Any]]:
    """
    List projects with optional filtering and pagination.
    
    Returns:
        List of project dictionaries
    """
    # Validate sort parameters
    valid_sort_fields = ["name", "created_at", "last_worked_at", "status"]
    if sort_by not in valid_sort_fields:
        sort_by = "last_worked_at"
    
    sort_order = sort_order.upper()
    if sort_order not in ["ASC", "DESC"]:
        sort_order = "DESC"
    
    with get_db_cursor() as cursor:
        if tag:
            # Query with tag filter
            query = """
                SELECT DISTINCT p.*
                FROM projects p
                JOIN project_tags pt ON p.id = pt.project_id
                JOIN tags t ON pt.tag_id = t.id
                WHERE p.is_archived = 0 AND t.name = %s
            """
            params = [tag]
        else:
            # Query without tag filter
            query = "SELECT * FROM projects WHERE is_archived = 0"
            params = []
        
        if status:
            query += " AND status = %s" if tag else " AND status = %s"
            params.append(status)
        
        # Add ORDER BY clause
        if sort_by == "last_worked_at":
            query += f" ORDER BY CASE WHEN last_worked_at IS NULL THEN 0 ELSE 1 END {sort_order}, last_worked_at {sort_order}"
        else:
            query += f" ORDER BY {sort_by} {sort_order}"
        
        # Add secondary sort
        if sort_by != "created_at":
            query += ", created_at DESC"
        
        # Add pagination
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)
            
            if offset is not None:
                query += " OFFSET %s"
                params.append(offset)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert datetime objects to ISO format strings
        for row in rows:
            if row['created_at']:
                row['created_at'] = row['created_at'].isoformat()
            if row['last_worked_at']:
                row['last_worked_at'] = row['last_worked_at'].isoformat()
        
        return rows


def update_project(project_id: int, **kwargs) -> bool:
    """
    Update project fields.
    
    Returns:
        True if project was updated, False if not found
    """
    if not kwargs:
        return False
    
    valid_fields = {
        "name", "description", "status", "project_type",
        "primary_language", "stack", "repo_url", "local_path",
        "scope_size", "learning_goal", "is_archived"
    }
    
    updates = {k: v for k, v in kwargs.items() if k in valid_fields}
    
    if not updates:
        return False
    
    with get_db_cursor() as cursor:
        set_clause = ", ".join(f"{field} = %s" for field in updates.keys())
        values = list(updates.values()) + [project_id]
        
        cursor.execute(
            f"UPDATE projects SET {set_clause} WHERE id = %s",
            values
        )
        
        return cursor.rowcount > 0


def delete_project(project_id: int) -> bool:
    """
    Delete a project by ID.
    
    Returns:
        True if deleted, False if not found
    """
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
        return cursor.rowcount > 0


def update_last_worked(project_id: int) -> tuple[bool, Optional[str]]:
    """
    Update the last_worked_at timestamp for a project.
    
    Returns:
        Tuple of (success, timestamp)
    """
    now = datetime.utcnow()
    
    with get_db_cursor() as cursor:
        cursor.execute(
            "UPDATE projects SET last_worked_at = %s WHERE id = %s",
            (now, project_id)
        )
        
        if cursor.rowcount > 0:
            return True, now.isoformat()
        return False, None


# =========================
# Tag Operations
# =========================

def get_or_create_tag(tag_name: str) -> int:
    """
    Get a tag ID by name, or create it if it doesn't exist.
    
    Returns:
        The tag's ID
    """
    with get_db_cursor() as cursor:
        # Try to find existing tag
        cursor.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
        row = cursor.fetchone()
        
        if row:
            return row['id']
        
        # Create new tag
        cursor.execute("INSERT INTO tags (name) VALUES (%s)", (tag_name,))
        return cursor.lastrowid


def add_tag_to_project(project_id: int, tag_name: str) -> bool:
    """
    Add a tag to a project.
    
    Returns:
        True if tag was added, False if it was already present
    """
    tag_id = get_or_create_tag(tag_name)
    
    with get_db_cursor() as cursor:
        # Check if already exists
        cursor.execute(
            "SELECT 1 FROM project_tags WHERE project_id = %s AND tag_id = %s",
            (project_id, tag_id)
        )
        
        if cursor.fetchone():
            return False  # Already exists
        
        # Add the tag
        cursor.execute(
            "INSERT INTO project_tags (project_id, tag_id) VALUES (%s, %s)",
            (project_id, tag_id)
        )
        
        return True


def remove_tag_from_project(project_id: int, tag_name: str) -> bool:
    """
    Remove a tag from a project.
    
    Returns:
        True if tag was removed, False if it wasn't found
    """
    with get_db_cursor() as cursor:
        # Find the tag ID
        cursor.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        tag_id = row['id']
        
        # Remove the association
        cursor.execute(
            "DELETE FROM project_tags WHERE project_id = %s AND tag_id = %s",
            (project_id, tag_id)
        )
        
        return cursor.rowcount > 0


def list_project_tags(project_id: int) -> List[str]:
    """
    Get all tags for a specific project.
    
    Returns:
        List of tag names
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT t.name
            FROM tags t
            JOIN project_tags pt ON t.id = pt.tag_id
            WHERE pt.project_id = %s
            ORDER BY t.name
            """,
            (project_id,)
        )
        
        rows = cursor.fetchall()
        return [row['name'] for row in rows]


def list_all_tags() -> List[Dict[str, Any]]:
    """
    Get all tags with project counts.
    
    Returns:
        List of dictionaries with 'name' and 'project_count' fields
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                t.name,
                COUNT(pt.project_id) as project_count
            FROM tags t
            LEFT JOIN project_tags pt ON t.id = pt.tag_id
            GROUP BY t.id, t.name
            ORDER BY t.name
            """
        )
        
        rows = cursor.fetchall()
        return [{'name': row['name'], 'project_count': row['project_count']} for row in rows]


# =========================
# Note Operations
# =========================

def create_note(project_id: int, content: str, note_type: str = "log") -> int:
    """
    Create a new note for a project.
    
    Returns:
        The new note's ID
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO project_notes (project_id, note_type, content, created_at)
            VALUES (%s, %s, %s, %s)
            """,
            (project_id, note_type, content, datetime.utcnow())
        )
        return cursor.lastrowid


def list_notes(project_id: int) -> List[Dict[str, Any]]:
    """
    List all notes for a project.
    
    Returns:
        List of note dictionaries, ordered by created_at DESC
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM project_notes
            WHERE project_id = %s
            ORDER BY created_at DESC
            """,
            (project_id,)
        )
        
        rows = cursor.fetchall()
        
        # Convert datetime objects to ISO format strings
        for row in rows:
            if row['created_at']:
                row['created_at'] = row['created_at'].isoformat()
        
        return rows


def get_note(note_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single note by ID.
    
    Returns:
        Dictionary of note fields, or None if not found
    """
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM project_notes WHERE id = %s", (note_id,))
        row = cursor.fetchone()
        
        if row and row['created_at']:
            row['created_at'] = row['created_at'].isoformat()
        
        return row


def delete_note(note_id: int) -> bool:
    """
    Delete a note by ID.

    Returns:
        True if deleted, False if not found
    """
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM project_notes WHERE id = %s", (note_id,))
        return cursor.rowcount > 0


# =========================
# Relationship Operations
# =========================

def create_relationship(source_project_id: int, target_project_id: int, relationship_type: str) -> int:
    """
    Create a relationship between two projects.

    Returns:
        The new relationship's ID
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO project_relationships (source_project_id, target_project_id, relationship_type, created_at)
            VALUES (%s, %s, %s, %s)
            """,
            (source_project_id, target_project_id, relationship_type, datetime.utcnow())
        )
        return cursor.lastrowid


def get_relationship(relationship_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single relationship by ID.

    Returns:
        Dictionary of relationship fields with target project name, or None if not found
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT r.*, p.name as target_project_name
            FROM project_relationships r
            JOIN projects p ON r.target_project_id = p.id
            WHERE r.id = %s
            """,
            (relationship_id,)
        )
        row = cursor.fetchone()
        if row and row['created_at']:
            row['created_at'] = row['created_at'].isoformat()
            row['direction'] = 'outgoing'
        return row


def list_project_relationships(project_id: int) -> List[Dict[str, Any]]:
    """
    Get all relationships for a project (both outgoing and incoming).

    Returns:
        List of relationship dictionaries with target project names
    """
    with get_db_cursor() as cursor:
        # Get outgoing relationships (where this project is the source)
        cursor.execute(
            """
            SELECT r.*, p.name as target_project_name, 'outgoing' as direction
            FROM project_relationships r
            JOIN projects p ON r.target_project_id = p.id
            WHERE r.source_project_id = %s
            ORDER BY r.created_at DESC
            """,
            (project_id,)
        )
        outgoing = cursor.fetchall()

        # Get incoming relationships (where this project is the target)
        cursor.execute(
            """
            SELECT r.id, r.target_project_id as source_project_id, r.source_project_id as target_project_id,
                   r.relationship_type, r.created_at, p.name as target_project_name, 'incoming' as direction
            FROM project_relationships r
            JOIN projects p ON r.source_project_id = p.id
            WHERE r.target_project_id = %s
            ORDER BY r.created_at DESC
            """,
            (project_id,)
        )
        incoming = cursor.fetchall()

        all_relationships = list(outgoing) + list(incoming)

        for row in all_relationships:
            if row['created_at']:
                row['created_at'] = row['created_at'].isoformat()

        return all_relationships


def delete_relationship(relationship_id: int) -> bool:
    """
    Delete a relationship by ID.

    Returns:
        True if deleted, False if not found
    """
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM project_relationships WHERE id = %s", (relationship_id,))
        return cursor.rowcount > 0


def relationship_exists(source_project_id: int, target_project_id: int, relationship_type: str) -> bool:
    """
    Check if a specific relationship already exists.

    Returns:
        True if exists, False otherwise
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT 1 FROM project_relationships
            WHERE source_project_id = %s AND target_project_id = %s AND relationship_type = %s
            """,
            (source_project_id, target_project_id, relationship_type)
        )
        return cursor.fetchone() is not None


# =========================
# Graph Data Operations
# =========================

def get_graph_data() -> Dict[str, Any]:
    """
    Get all data needed for the full project graph.

    Returns:
        Dict with 'nodes' (projects) and 'explicit_edges' (relationships)
    """
    with get_db_cursor() as cursor:
        # Get all non-archived projects as nodes
        cursor.execute(
            """
            SELECT id, name, status, project_type, primary_language, stack
            FROM projects
            WHERE is_archived = 0
            """
        )
        nodes = cursor.fetchall()

        # Get all explicit relationships as edges
        cursor.execute(
            """
            SELECT r.source_project_id, r.target_project_id, r.relationship_type
            FROM project_relationships r
            JOIN projects p1 ON r.source_project_id = p1.id
            JOIN projects p2 ON r.target_project_id = p2.id
            WHERE p1.is_archived = 0 AND p2.is_archived = 0
            """
        )
        explicit_edges = cursor.fetchall()

        return {
            'nodes': list(nodes),
            'explicit_edges': list(explicit_edges)
        }


def get_projects_sharing_tags(project_id: int) -> List[Dict[str, Any]]:
    """
    Get projects that share tags with the given project.

    Returns:
        List of projects with shared_tags count
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT p.id, p.name, COUNT(pt2.tag_id) as shared_tags
            FROM projects p
            JOIN project_tags pt2 ON p.id = pt2.project_id
            WHERE pt2.tag_id IN (
                SELECT tag_id FROM project_tags WHERE project_id = %s
            )
            AND p.id != %s
            AND p.is_archived = 0
            GROUP BY p.id, p.name
            ORDER BY shared_tags DESC
            """,
            (project_id, project_id)
        )
        return list(cursor.fetchall())


def get_projects_by_language(primary_language: str, exclude_project_id: int) -> List[Dict[str, Any]]:
    """
    Get projects using the same primary language.

    Returns:
        List of project dictionaries
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name
            FROM projects
            WHERE primary_language = %s AND id != %s AND is_archived = 0
            """,
            (primary_language, exclude_project_id)
        )
        return list(cursor.fetchall())
