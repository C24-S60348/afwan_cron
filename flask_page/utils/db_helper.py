"""
Shared SQLite utility for all afwan_cron modules.

Each module gets its own .db file in afwan_cron/db/.
Table naming convention: projectname_tablename_db

Usage in any module:

    from flask_page.utils.db_helper import get_connection, ensure_tables

    APP_NAME = 'myapp'

    def init_myapp_db():
        ensure_tables(APP_NAME, [
            '''CREATE TABLE IF NOT EXISTS myapp_things_db (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )'''
        ])

    # In a route:
    with get_connection(APP_NAME) as conn:
        rows = conn.execute('SELECT * FROM myapp_things_db').fetchall()
"""
import os
import sqlite3

# Resolves to afwan_cron/db/ regardless of where the app is run from
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
_DB_DIR = os.path.join(_PROJECT_ROOT, 'db')


def get_db_path(app_name: str) -> str:
    """Return absolute path to <app_name>.db inside afwan_cron/db/."""
    return os.path.join(_DB_DIR, f'{app_name}.db')


def get_connection(app_name: str) -> sqlite3.Connection:
    """
    Open a SQLite connection for the given app.
    Creates db/ directory and the .db file if they don't exist.
    WAL mode is enabled for better concurrent-read performance.
    """
    os.makedirs(_DB_DIR, exist_ok=True)
    conn = sqlite3.connect(get_db_path(app_name))
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


def ensure_tables(app_name: str, ddl_statements: list) -> None:
    """
    Run each DDL statement once at startup.
    Idempotent — safe to call every time the server starts.
    Each statement should be a CREATE TABLE IF NOT EXISTS ...
    """
    os.makedirs(_DB_DIR, exist_ok=True)
    conn = get_connection(app_name)
    try:
        for stmt in ddl_statements:
            conn.execute(stmt)
        conn.commit()
    finally:
        conn.close()
