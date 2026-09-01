#!/usr/bin/env python3
"""Test MySQL/MariaDB connection using DB_* environment variables."""

import sys
from pathlib import Path

import pymysql

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.config import config


def run_connection_check():
    """Test connection to the configured MySQL/MariaDB server."""
    is_valid, error = config.validate()
    if not is_valid:
        print(f"Configuration error: {error}", file=sys.stderr)
        return False

    try:
        print(f"Attempting to connect to MySQL server at {config.DB_HOST}:{config.DB_PORT}...")
        conn = pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            charset="utf8mb4",
            connect_timeout=10,
        )
        print("Connection successful!")

        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"MySQL version: {version[0]}")

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        if tables:
            print(f"Existing tables: {[t[0] for t in tables]}")
        else:
            print("  No tables found (database is empty)")

        conn.close()
        return True

    except pymysql.err.OperationalError as e:
        print(f"Connection failed: {e}", file=sys.stderr)
        print("\nTroubleshooting steps:", file=sys.stderr)
        print("1. Confirm MySQL/MariaDB is running and reachable at DB_HOST:DB_PORT", file=sys.stderr)
        print("2. Confirm DB_USER / DB_PASSWORD / DB_NAME in .env", file=sys.stderr)
        print("3. Confirm the user is allowed to connect from this host", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = run_connection_check()
    sys.exit(0 if success else 1)
