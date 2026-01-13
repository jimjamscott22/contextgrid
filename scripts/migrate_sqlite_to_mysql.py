#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to MySQL.
Reads from data/projects.db and writes to configured MySQL database.
"""

import sqlite3
import pymysql
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.config import config


def get_sqlite_connection():
    """Get connection to SQLite database."""
    db_path = Path(__file__).parent.parent / "data" / "projects.db"
    
    if not db_path.exists():
        print(f"Error: SQLite database not found at {db_path}")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_mysql_connection():
    """Get connection to MySQL database."""
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def migrate_projects(sqlite_conn, mysql_conn):
    """Migrate projects table."""
    print("Migrating projects...")
    
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    # Fetch all projects from SQLite
    sqlite_cursor.execute("SELECT * FROM projects")
    projects = sqlite_cursor.fetchall()
    
    project_id_map = {}  # Map old IDs to new IDs
    
    for project in projects:
        # Convert SQLite row to dict
        project_dict = dict(project)
        
        # Convert datetime strings to datetime objects
        created_at = datetime.fromisoformat(project_dict['created_at']) if project_dict['created_at'] else None
        last_worked_at = datetime.fromisoformat(project_dict['last_worked_at']) if project_dict['last_worked_at'] else None
        
        # Insert into MySQL
        mysql_cursor.execute(
            """
            INSERT INTO projects (
                name, description, status, project_type,
                primary_language, stack, repo_url, local_path,
                scope_size, learning_goal, created_at, last_worked_at, is_archived
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                project_dict['name'],
                project_dict['description'],
                project_dict['status'],
                project_dict['project_type'],
                project_dict['primary_language'],
                project_dict['stack'],
                project_dict['repo_url'],
                project_dict['local_path'],
                project_dict['scope_size'],
                project_dict['learning_goal'],
                created_at,
                last_worked_at,
                project_dict['is_archived']
            )
        )
        
        # Map old ID to new ID
        project_id_map[project_dict['id']] = mysql_cursor.lastrowid
    
    mysql_conn.commit()
    print(f"  Migrated {len(projects)} projects")
    
    return project_id_map


def migrate_tags(sqlite_conn, mysql_conn):
    """Migrate tags table."""
    print("Migrating tags...")
    
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    # Fetch all tags from SQLite
    sqlite_cursor.execute("SELECT * FROM tags")
    tags = sqlite_cursor.fetchall()
    
    tag_id_map = {}  # Map old IDs to new IDs
    
    for tag in tags:
        tag_dict = dict(tag)
        
        # Insert into MySQL
        mysql_cursor.execute(
            "INSERT INTO tags (name) VALUES (%s)",
            (tag_dict['name'],)
        )
        
        # Map old ID to new ID
        tag_id_map[tag_dict['id']] = mysql_cursor.lastrowid
    
    mysql_conn.commit()
    print(f"  Migrated {len(tags)} tags")
    
    return tag_id_map


def migrate_project_tags(sqlite_conn, mysql_conn, project_id_map, tag_id_map):
    """Migrate project_tags junction table."""
    print("Migrating project-tag associations...")
    
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    # Fetch all associations from SQLite
    sqlite_cursor.execute("SELECT * FROM project_tags")
    associations = sqlite_cursor.fetchall()
    
    for assoc in associations:
        assoc_dict = dict(assoc)
        
        # Get new IDs
        new_project_id = project_id_map.get(assoc_dict['project_id'])
        new_tag_id = tag_id_map.get(assoc_dict['tag_id'])
        
        if new_project_id and new_tag_id:
            # Insert into MySQL
            mysql_cursor.execute(
                "INSERT INTO project_tags (project_id, tag_id) VALUES (%s, %s)",
                (new_project_id, new_tag_id)
            )
    
    mysql_conn.commit()
    print(f"  Migrated {len(associations)} associations")


def migrate_notes(sqlite_conn, mysql_conn, project_id_map):
    """Migrate project_notes table."""
    print("Migrating project notes...")
    
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    # Fetch all notes from SQLite
    sqlite_cursor.execute("SELECT * FROM project_notes")
    notes = sqlite_cursor.fetchall()
    
    for note in notes:
        note_dict = dict(note)
        
        # Get new project ID
        new_project_id = project_id_map.get(note_dict['project_id'])
        
        if new_project_id:
            # Convert datetime string to datetime object
            created_at = datetime.fromisoformat(note_dict['created_at']) if note_dict['created_at'] else None
            
            # Insert into MySQL
            mysql_cursor.execute(
                """
                INSERT INTO project_notes (project_id, note_type, content, created_at)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    new_project_id,
                    note_dict['note_type'],
                    note_dict['content'],
                    created_at
                )
            )
    
    mysql_conn.commit()
    print(f"  Migrated {len(notes)} notes")


def main():
    """Main migration function."""
    print("=" * 60)
    print("ContextGrid SQLite to MySQL Migration")
    print("=" * 60)
    print()
    
    # Validate configuration
    is_valid, error = config.validate()
    if not is_valid:
        print(f"Error: Configuration is invalid: {error}")
        sys.exit(1)
    
    print(f"Source: SQLite (data/projects.db)")
    print(f"Target: MySQL ({config.DB_USER}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME})")
    print()
    
    # Confirm migration
    response = input("This will migrate all data from SQLite to MySQL. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled")
        sys.exit(0)
    
    print()
    
    try:
        # Connect to databases
        print("Connecting to databases...")
        sqlite_conn = get_sqlite_connection()
        mysql_conn = get_mysql_connection()
        print("  Connected successfully")
        print()
        
        # Run migrations
        project_id_map = migrate_projects(sqlite_conn, mysql_conn)
        tag_id_map = migrate_tags(sqlite_conn, mysql_conn)
        migrate_project_tags(sqlite_conn, mysql_conn, project_id_map, tag_id_map)
        migrate_notes(sqlite_conn, mysql_conn, project_id_map)
        
        # Close connections
        sqlite_conn.close()
        mysql_conn.close()
        
        print()
        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print()
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
