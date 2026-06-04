# flask_page/utils/db_helper.py
# ---------------------------------------------------------------------------
# Shared SQLite utility for all afwan_cron modules.
#
# DATABASE LOCATION
#   All .db files live in:  afwan_cron/db/<appname>.db
#   This folder is GITIGNORED (see .gitignore: db/).
#   It is created automatically at runtime — do NOT commit .db files.
#
# TABLE NAMING CONVENTION
#   Every table must follow:  projectname_tablename_db
#   Examples:
#       catalogbaju_catalog_db
#       catalogbaju_guestcarts_db
#       kadkahwin_scores_db
#       blockpuzzle_leaderboard_db
#
# ---------------------------------------------------------------------------
# HOW TO ADD A NEW MODULE (step-by-step for the next project)
# ---------------------------------------------------------------------------
#
# STEP 1 — In your blueprint file (flask_page/modules/myapp/myapp.py):
#
#   from flask_page.utils.db_helper import get_connection, ensure_tables
#
#   _APP_NAME  = 'myapp'           # becomes db/myapp.db
#   _T_THINGS  = 'myapp_things_db' # table: projectname_tablename_db
#   _T_LOGS    = 'myapp_logs_db'
#
#   def init_myapp_db():
#       # Called once on server start from afwanhaziqmy.py.
#       # Creates tables if missing; seeds default data if needed.
#       ensure_tables(_APP_NAME, [
#           f'''CREATE TABLE IF NOT EXISTS {_T_THINGS} (
#               id         INTEGER PRIMARY KEY AUTOINCREMENT,
#               name       TEXT NOT NULL DEFAULT '',
#               value      TEXT DEFAULT '',
#               created_at TEXT DEFAULT ''
#           )''',
#           f'''CREATE TABLE IF NOT EXISTS {_T_LOGS} (
#               id        INTEGER PRIMARY KEY AUTOINCREMENT,
#               message   TEXT DEFAULT '',
#               timestamp TEXT DEFAULT ''
#           )''',
#       ])
#       # Optionally seed defaults here if the table is empty.
#
#
# STEP 2 — Export from flask_page/modules/myapp/__init__.py:
#
#   from .myapp import myapp_bp, init_myapp_db
#   __all__ = ['myapp_bp', 'init_myapp_db']
#
#
# STEP 3 — Register in afwanhaziqmy.py:
#
#   from flask_page.modules.myapp import myapp_bp, init_myapp_db
#   app.register_blueprint(myapp_bp)
#
#   with app.app_context():
#       init_all_ular_databases()
#       init_block_puzzle_db(app)
#       init_catalogbaju_db()
#       init_myapp_db()    # <-- add this line
#
#
# STEP 4 — Use get_connection() inside your routes:
#
#   @myapp_bp.route('/api/things', methods=['GET'])
#   def get_things():
#       conn = get_connection(_APP_NAME)
#       try:
#           rows = conn.execute(f'SELECT * FROM {_T_THINGS} ORDER BY id').fetchall()
#       finally:
#           conn.close()
#       return jsonify({'items': [dict(r) for r in rows]})
#
#   @myapp_bp.route('/api/things', methods=['PUT'])
#   def save_things():
#       data  = request.get_json(silent=True) or {}
#       items = data.get('items')
#       if not isinstance(items, list):
#           return jsonify({'error': 'Expected {"items": [...]}'}), 400
#       conn = get_connection(_APP_NAME)
#       try:
#           conn.execute(f'DELETE FROM {_T_THINGS}')
#           for item in items:
#               conn.execute(
#                   f'INSERT INTO {_T_THINGS} (name, value, created_at) VALUES (?, ?, ?)',
#                   (item.get('name',''), item.get('value',''), item.get('createdAt',''))
#               )
#           conn.commit()
#       finally:
#           conn.close()
#       return jsonify({'ok': True})
#
# ---------------------------------------------------------------------------
# EXISTING MODULES USING THIS HELPER
# ---------------------------------------------------------------------------
#   catalogbaju  ->  db/catalogbaju.db
#       tables: catalogbaju_catalog_db
#               catalogbaju_askowoner_db
#               catalogbaju_guestcarts_db
# ---------------------------------------------------------------------------

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
    WAL mode enabled for better concurrent-read performance.
    Always call conn.close() when done.
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
    Each statement should be CREATE TABLE IF NOT EXISTS ...
    """
    os.makedirs(_DB_DIR, exist_ok=True)
    conn = get_connection(app_name)
    try:
        for stmt in ddl_statements:
            conn.execute(stmt)
        conn.commit()
    finally:
        conn.close()
