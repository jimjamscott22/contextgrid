#!/usr/bin/env python3
"""Initialize ContextGrid database on MySQL server."""

import pymysql
import sys
from pathlib import Path

def init_database():
    """Create database and initialize schema."""
    
    # First, connect without specifying a database to create it
    print("Connecting to MySQL server at 192.168.1.25:3306...")
    try:
        conn = pymysql.connect(
            host='192.168.1.25',
            port=3306,
            user='contextgrid_user',
            password='Yar22',
            charset='utf8mb4',
            connect_timeout=10
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        print("Creating database 'contextgrid'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS contextgrid CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✓ Database created/verified")
        
        # Switch to the database
        cursor.execute("USE contextgrid")
        
        # Read and execute schema
        schema_file = Path(__file__).parent / 'init_mysql.sql'
        print(f"Reading schema from {schema_file}...")
        schema = schema_file.read_text(encoding='utf-8')
        
        # Split into statements and execute
        statements = [s.strip() for s in schema.split(';') if s.strip()]
        print(f"Executing {len(statements)} SQL statements...")
        
        for i, stmt in enumerate(statements, 1):
            cursor.execute(stmt)
            print(f"  {i}/{len(statements)} - OK")
        
        conn.commit()
        print("\n✓ Database schema initialized successfully!")
        
        # Verify tables were created
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✓ Created tables: {[t[0] for t in tables]}")
        
        conn.close()
        return True
        
    except pymysql.err.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
