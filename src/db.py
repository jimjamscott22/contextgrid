"""
Database abstraction layer for ContextGrid.
Supports both SQLite and MySQL backends with a unified interface.
"""

import os
import sqlite3
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

try:
    import pymysql
    from pymysql.cursors import DictCursor
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


# =========================
# Configuration
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "projects.db"
SQLITE_SCHEMA_PATH = BASE_DIR / "scripts" / "init_db.sql"
MYSQL_SCHEMA_PATH = BASE_DIR / "scripts" / "init_mysql.sql"


# =========================
# Abstract Database Interface
# =========================

class DatabaseBackend(ABC):
    """Abstract base class for database backends."""
    
    @abstractmethod
    def initialize_database(self):
        """Initialize the database schema."""
        pass
    
    @abstractmethod
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test the database connection."""
        pass
    
    # Project operations
    @abstractmethod
    def create_project(self, name: str, status: str = "idea", description: Optional[str] = None,
                      project_type: Optional[str] = None, primary_language: Optional[str] = None,
                      stack: Optional[str] = None, repo_url: Optional[str] = None,
                      local_path: Optional[str] = None, scope_size: Optional[str] = None,
                      learning_goal: Optional[str] = None) -> int:
        """Create a new project and return its ID."""
        pass
    
    @abstractmethod
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single project by ID."""
        pass
    
    @abstractmethod
    def list_projects(self, status: Optional[str] = None, tag: Optional[str] = None,
                     limit: Optional[int] = None, offset: Optional[int] = None,
                     sort_by: str = "last_worked_at", sort_order: str = "desc") -> List[Dict[str, Any]]:
        """List projects with optional filtering and pagination."""
        pass
    
    @abstractmethod
    def update_project(self, project_id: int, **kwargs) -> bool:
        """Update project fields."""
        pass
    
    @abstractmethod
    def delete_project(self, project_id: int) -> bool:
        """Delete a project by ID."""
        pass
    
    @abstractmethod
    def update_last_worked(self, project_id: int) -> Tuple[bool, Optional[str]]:
        """Update the last_worked_at timestamp for a project."""
        pass
    
    # Tag operations
    @abstractmethod
    def get_or_create_tag(self, tag_name: str) -> int:
        """Get a tag ID by name, or create it if it doesn't exist."""
        pass
    
    @abstractmethod
    def add_tag_to_project(self, project_id: int, tag_name: str) -> bool:
        """Add a tag to a project."""
        pass
    
    @abstractmethod
    def remove_tag_from_project(self, project_id: int, tag_name: str) -> bool:
        """Remove a tag from a project."""
        pass
    
    @abstractmethod
    def list_project_tags(self, project_id: int) -> List[str]:
        """Get all tags for a specific project."""
        pass
    
    @abstractmethod
    def list_all_tags(self) -> List[Dict[str, Any]]:
        """Get all tags with project counts."""
        pass
    
    # Note operations
    @abstractmethod
    def create_note(self, project_id: int, content: str, note_type: str = "log") -> int:
        """Create a new note for a project."""
        pass
    
    @abstractmethod
    def list_notes(self, project_id: int) -> List[Dict[str, Any]]:
        """List all notes for a project."""
        pass
    
    @abstractmethod
    def get_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single note by ID."""
        pass
    
    @abstractmethod
    def delete_note(self, note_id: int) -> bool:
        """Delete a note by ID."""
        pass


# =========================
# SQLite Backend
# =========================

class SQLiteBackend(DatabaseBackend):
    """SQLite database backend implementation."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.data_dir = self.db_path.parent
        self.schema_path = SQLITE_SCHEMA_PATH
    
    def _get_connection(self):
        """Get a SQLite database connection."""
        self.data_dir.mkdir(exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    @contextmanager
    def _get_cursor(self):
        """Context manager for database cursor."""
        conn = self._get_connection()
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
    
    def initialize_database(self):
        """Initialize the database schema."""
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        with self._get_cursor() as cursor:
            cursor.executescript(schema_sql)
    
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test the database connection."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return True, None
        except Exception as e:
            return False, str(e)
    
    def create_project(self, name: str, status: str = "idea", description: Optional[str] = None,
                      project_type: Optional[str] = None, primary_language: Optional[str] = None,
                      stack: Optional[str] = None, repo_url: Optional[str] = None,
                      local_path: Optional[str] = None, scope_size: Optional[str] = None,
                      learning_goal: Optional[str] = None) -> int:
        """Create a new project and return its ID."""
        with self._get_cursor() as cursor:
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
                    scope_size, learning_goal, datetime.utcnow().isoformat()
                )
            )
            return cursor.lastrowid
    
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single project by ID."""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_projects(self, status: Optional[str] = None, tag: Optional[str] = None,
                     limit: Optional[int] = None, offset: Optional[int] = None,
                     sort_by: str = "last_worked_at", sort_order: str = "desc") -> List[Dict[str, Any]]:
        """List projects with optional filtering and pagination."""
        valid_sort_fields = ["name", "created_at", "last_worked_at", "status"]
        if sort_by not in valid_sort_fields:
            sort_by = "last_worked_at"
        
        sort_order = sort_order.upper()
        if sort_order not in ["ASC", "DESC"]:
            sort_order = "DESC"
        
        with self._get_cursor() as cursor:
            if tag:
                query = """
                    SELECT DISTINCT p.*
                    FROM projects p
                    JOIN project_tags pt ON p.id = pt.project_id
                    JOIN tags t ON pt.tag_id = t.id
                    WHERE p.is_archived = 0 AND t.name = ?
                """
                params = [tag]
            else:
                query = "SELECT * FROM projects WHERE is_archived = 0"
                params = []
            
            if status:
                query += " AND status = ?"
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
                query += " LIMIT ?"
                params.append(limit)
                
                if offset is not None:
                    query += " OFFSET ?"
                    params.append(offset)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def update_project(self, project_id: int, **kwargs) -> bool:
        """Update project fields."""
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
        
        with self._get_cursor() as cursor:
            set_clause = ", ".join(f"{field} = ?" for field in updates.keys())
            values = list(updates.values()) + [project_id]
            
            cursor.execute(
                f"UPDATE projects SET {set_clause} WHERE id = ?",
                values
            )
            
            return cursor.rowcount > 0
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project by ID."""
        with self._get_cursor() as cursor:
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            return cursor.rowcount > 0
    
    def update_last_worked(self, project_id: int) -> Tuple[bool, Optional[str]]:
        """Update the last_worked_at timestamp for a project."""
        now = datetime.utcnow().isoformat()
        
        with self._get_cursor() as cursor:
            cursor.execute(
                "UPDATE projects SET last_worked_at = ? WHERE id = ?",
                (now, project_id)
            )
            
            if cursor.rowcount > 0:
                return True, now
            return False, None
    
    def get_or_create_tag(self, tag_name: str) -> int:
        """Get a tag ID by name, or create it if it doesn't exist."""
        with self._get_cursor() as cursor:
            # Try to find existing tag
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            row = cursor.fetchone()
            
            if row:
                return row['id']
            
            # Create new tag
            cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
            return cursor.lastrowid
    
    def add_tag_to_project(self, project_id: int, tag_name: str) -> bool:
        """Add a tag to a project."""
        tag_id = self.get_or_create_tag(tag_name)
        
        with self._get_cursor() as cursor:
            # Check if already exists
            cursor.execute(
                "SELECT 1 FROM project_tags WHERE project_id = ? AND tag_id = ?",
                (project_id, tag_id)
            )
            
            if cursor.fetchone():
                return False  # Already exists
            
            # Add the tag
            cursor.execute(
                "INSERT INTO project_tags (project_id, tag_id) VALUES (?, ?)",
                (project_id, tag_id)
            )
            
            return True
    
    def remove_tag_from_project(self, project_id: int, tag_name: str) -> bool:
        """Remove a tag from a project."""
        with self._get_cursor() as cursor:
            # Find the tag ID
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            tag_id = row['id']
            
            # Remove the association
            cursor.execute(
                "DELETE FROM project_tags WHERE project_id = ? AND tag_id = ?",
                (project_id, tag_id)
            )
            
            return cursor.rowcount > 0
    
    def list_project_tags(self, project_id: int) -> List[str]:
        """Get all tags for a specific project."""
        with self._get_cursor() as cursor:
            cursor.execute(
                """
                SELECT t.name
                FROM tags t
                JOIN project_tags pt ON t.id = pt.tag_id
                WHERE pt.project_id = ?
                ORDER BY t.name
                """,
                (project_id,)
            )
            
            rows = cursor.fetchall()
            return [row['name'] for row in rows]
    
    def list_all_tags(self) -> List[Dict[str, Any]]:
        """Get all tags with project counts."""
        with self._get_cursor() as cursor:
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
    
    def create_note(self, project_id: int, content: str, note_type: str = "log") -> int:
        """Create a new note for a project."""
        with self._get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO project_notes (project_id, note_type, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (project_id, note_type, content, datetime.utcnow().isoformat())
            )
            return cursor.lastrowid
    
    def list_notes(self, project_id: int) -> List[Dict[str, Any]]:
        """List all notes for a project."""
        with self._get_cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM project_notes
                WHERE project_id = ?
                ORDER BY created_at DESC
                """,
                (project_id,)
            )
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single note by ID."""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM project_notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note by ID."""
        with self._get_cursor() as cursor:
            cursor.execute("DELETE FROM project_notes WHERE id = ?", (note_id,))
            return cursor.rowcount > 0


# =========================
# MySQL Backend
# =========================

class MySQLBackend(DatabaseBackend):
    """MySQL database backend implementation."""
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        if not MYSQL_AVAILABLE:
            raise ImportError("pymysql is not installed. Install it with: pip install pymysql")
        
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.schema_path = MYSQL_SCHEMA_PATH
    
    def _get_connection(self):
        """Get a MySQL database connection."""
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4',
            cursorclass=DictCursor,
            autocommit=False
        )
    
    @contextmanager
    def _get_cursor(self):
        """Context manager for database cursor."""
        conn = self._get_connection()
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
    
    def initialize_database(self):
        """Initialize the database schema."""
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        
        with self._get_cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
    
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test the database connection."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return True, None
        except Exception as e:
            return False, str(e)
    
    def create_project(self, name: str, status: str = "idea", description: Optional[str] = None,
                      project_type: Optional[str] = None, primary_language: Optional[str] = None,
                      stack: Optional[str] = None, repo_url: Optional[str] = None,
                      local_path: Optional[str] = None, scope_size: Optional[str] = None,
                      learning_goal: Optional[str] = None) -> int:
        """Create a new project and return its ID."""
        with self._get_cursor() as cursor:
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
    
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single project by ID."""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
            row = cursor.fetchone()
            if row:
                # Convert datetime objects to ISO format strings
                if row['created_at']:
                    row['created_at'] = row['created_at'].isoformat()
                if row['last_worked_at']:
                    row['last_worked_at'] = row['last_worked_at'].isoformat()
            return row
    
    def list_projects(self, status: Optional[str] = None, tag: Optional[str] = None,
                     limit: Optional[int] = None, offset: Optional[int] = None,
                     sort_by: str = "last_worked_at", sort_order: str = "desc") -> List[Dict[str, Any]]:
        """List projects with optional filtering and pagination."""
        valid_sort_fields = ["name", "created_at", "last_worked_at", "status"]
        if sort_by not in valid_sort_fields:
            sort_by = "last_worked_at"
        
        sort_order = sort_order.upper()
        if sort_order not in ["ASC", "DESC"]:
            sort_order = "DESC"
        
        with self._get_cursor() as cursor:
            if tag:
                query = """
                    SELECT DISTINCT p.*
                    FROM projects p
                    JOIN project_tags pt ON p.id = pt.project_id
                    JOIN tags t ON pt.tag_id = t.id
                    WHERE p.is_archived = 0 AND t.name = %s
                """
                params = [tag]
            else:
                query = "SELECT * FROM projects WHERE is_archived = 0"
                params = []
            
            if status:
                query += " AND status = %s"
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
    
    def update_project(self, project_id: int, **kwargs) -> bool:
        """Update project fields."""
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
        
        with self._get_cursor() as cursor:
            set_clause = ", ".join(f"{field} = %s" for field in updates.keys())
            values = list(updates.values()) + [project_id]
            
            cursor.execute(
                f"UPDATE projects SET {set_clause} WHERE id = %s",
                values
            )
            
            return cursor.rowcount > 0
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project by ID."""
        with self._get_cursor() as cursor:
            cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
            return cursor.rowcount > 0
    
    def update_last_worked(self, project_id: int) -> Tuple[bool, Optional[str]]:
        """Update the last_worked_at timestamp for a project."""
        now = datetime.utcnow()
        
        with self._get_cursor() as cursor:
            cursor.execute(
                "UPDATE projects SET last_worked_at = %s WHERE id = %s",
                (now, project_id)
            )
            
            if cursor.rowcount > 0:
                return True, now.isoformat()
            return False, None
    
    def get_or_create_tag(self, tag_name: str) -> int:
        """Get a tag ID by name, or create it if it doesn't exist."""
        with self._get_cursor() as cursor:
            # Try to find existing tag
            cursor.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
            row = cursor.fetchone()
            
            if row:
                return row['id']
            
            # Create new tag
            cursor.execute("INSERT INTO tags (name) VALUES (%s)", (tag_name,))
            return cursor.lastrowid
    
    def add_tag_to_project(self, project_id: int, tag_name: str) -> bool:
        """Add a tag to a project."""
        tag_id = self.get_or_create_tag(tag_name)
        
        with self._get_cursor() as cursor:
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
    
    def remove_tag_from_project(self, project_id: int, tag_name: str) -> bool:
        """Remove a tag from a project."""
        with self._get_cursor() as cursor:
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
    
    def list_project_tags(self, project_id: int) -> List[str]:
        """Get all tags for a specific project."""
        with self._get_cursor() as cursor:
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
    
    def list_all_tags(self) -> List[Dict[str, Any]]:
        """Get all tags with project counts."""
        with self._get_cursor() as cursor:
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
    
    def create_note(self, project_id: int, content: str, note_type: str = "log") -> int:
        """Create a new note for a project."""
        with self._get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO project_notes (project_id, note_type, content, created_at)
                VALUES (%s, %s, %s, %s)
                """,
                (project_id, note_type, content, datetime.utcnow())
            )
            return cursor.lastrowid
    
    def list_notes(self, project_id: int) -> List[Dict[str, Any]]:
        """List all notes for a project."""
        with self._get_cursor() as cursor:
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
    
    def get_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single note by ID."""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM project_notes WHERE id = %s", (note_id,))
            row = cursor.fetchone()
            
            if row and row['created_at']:
                row['created_at'] = row['created_at'].isoformat()
            
            return row
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note by ID."""
        with self._get_cursor() as cursor:
            cursor.execute("DELETE FROM project_notes WHERE id = %s", (note_id,))
            return cursor.rowcount > 0


# =========================
# Database Factory
# =========================

def get_database_backend() -> DatabaseBackend:
    """
    Factory function to create the appropriate database backend based on configuration.
    
    Configuration via environment variables:
    - DB_TYPE: "sqlite" or "mysql" (default: "sqlite")
    - For SQLite:
      - DB_PATH: path to SQLite database file (default: "data/projects.db")
    - For MySQL:
      - MYSQL_HOST: MySQL hostname (default: "localhost")
      - MYSQL_PORT: MySQL port (default: 3306)
      - MYSQL_USER: MySQL username
      - MYSQL_PASSWORD: MySQL password
      - MYSQL_DATABASE: MySQL database name (default: "contextgrid")
    
    Returns:
        DatabaseBackend: Configured database backend instance
    """
    db_type = os.getenv("DB_TYPE", "sqlite").lower()
    
    if db_type == "mysql":
        host = os.getenv("MYSQL_HOST", "localhost")
        port = int(os.getenv("MYSQL_PORT", "3306"))
        user = os.getenv("MYSQL_USER", "")
        password = os.getenv("MYSQL_PASSWORD", "")
        database = os.getenv("MYSQL_DATABASE", "contextgrid")
        
        if not user or not password:
            raise ValueError(
                "MySQL backend requires MYSQL_USER and MYSQL_PASSWORD environment variables"
            )
        
        return MySQLBackend(host, port, user, password, database)
    else:
        # Default to SQLite
        db_path = os.getenv("DB_PATH", str(DB_PATH))
        return SQLiteBackend(db_path)


# =========================
# Legacy compatibility functions
# =========================

def get_connection():
    """
    Legacy function for backward compatibility.
    Returns a direct SQLite connection.
    
    Note: New code should use get_database_backend() instead.
    """
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Initialize schema if needed
    with open(SQLITE_SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    
    return conn
