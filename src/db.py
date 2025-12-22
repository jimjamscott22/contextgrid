import sqlite3
from pathlib import Path


# Resolve project root dynamically
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "projects.db"
SCHEMA_PATH = BASE_DIR / "scripts" / "init_db.sql"


def get_connection():
    """
    Returns a SQLite connection to the ContextGrid database.
    Initializes the database and schema if they do not exist.
    """
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # dict-like access

    _initialize_schema(conn)

    return conn


def _initialize_schema(conn):
    """
    Runs the schema SQL if tables do not already exist.
    Safe to call multiple times.
    """
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn.executescript(schema_sql)
    conn.commit()
