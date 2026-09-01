#!/usr/bin/env python3
"""Initialize ContextGrid database on MySQL/MariaDB.

Reads DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, and DB_NAME from the environment
(or the project .env file via api.config).
"""

import re
import sys
from pathlib import Path

import pymysql

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.config import config


_DB_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")


def init_database():
    """Create database and initialize schema."""
    is_valid, error = config.validate()
    if not is_valid:
        print(f"Configuration error: {error}", file=sys.stderr)
        return False

    if not _DB_NAME_RE.match(config.DB_NAME):
        print(f"Invalid DB_NAME: {config.DB_NAME!r}", file=sys.stderr)
        return False

    print(f"Connecting to MySQL server at {config.DB_HOST}:{config.DB_PORT}...")
    try:
        conn = pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            charset="utf8mb4",
            connect_timeout=10,
        )
        cursor = conn.cursor()

        print(f"Creating database '{config.DB_NAME}'...")
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        print("Database created/verified")

        cursor.execute(f"USE `{config.DB_NAME}`")

        schema_file = Path(__file__).parent / "init_mysql.sql"
        print(f"Reading schema from {schema_file}...")
        schema = schema_file.read_text(encoding="utf-8")

        statements = [s.strip() for s in schema.split(";") if s.strip()]
        print(f"Executing {len(statements)} SQL statements...")

        for i, stmt in enumerate(statements, 1):
            try:
                cursor.execute(stmt)
                print(f"  {i}/{len(statements)} - OK")
            except pymysql.err.OperationalError as exc:
                if exc.args[0] not in (1060, 1061):
                    raise
                print(f"  {i}/{len(statements)} - already applied")

        conn.commit()
        print("\nDatabase schema initialized successfully!")

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"Created tables: {[t[0] for t in tables]}")

        conn.close()
        return True

    except pymysql.err.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
