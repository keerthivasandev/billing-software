"""SQLite connection to the project data DB (`data/data`)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

# Project root: app/db/connection.py → ../../
_ROOT = Path(__file__).resolve().parents[2]
_DB_PATH = _ROOT / "data" / "data"


def db_path() -> Path:
    return _DB_PATH


def get_connection() -> sqlite3.Connection:
    """Open the app DB. Caller must close (or use as context manager)."""
    if not _DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {_DB_PATH}. Create tables under data/data first."
        )
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
