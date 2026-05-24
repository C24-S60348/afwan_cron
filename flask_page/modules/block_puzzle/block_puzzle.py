"""
flask_page/modules/block_puzzle/block_puzzle.py
Block Puzzle Flask Blueprint — integrated into afwanhaziq.my
Routes:
  GET  /block-puzzle/           → single-player game
  GET  /block-puzzle/mp         → online multiplayer game (UI only)
  GET  /block-puzzle/levels.json
  GET  /block-puzzle/assets/<filename>
  POST /block-puzzle/api/game/create
  POST /block-puzzle/api/game/join
  GET  /block-puzzle/api/game/<room_code>
"""
import sqlite3, random, string, json, time, os
from flask import Blueprint, request, jsonify, g, send_from_directory, make_response

block_puzzle_bp = Blueprint('block_puzzle', __name__, url_prefix='/block-puzzle')

# File paths relative to this module
_MODULE_DIR = os.path.dirname(__file__)
DB_PATH    = os.path.join(_MODULE_DIR, 'block_puzzle.db')
STATIC_DIR = os.path.join(_MODULE_DIR, 'static', 'block-puzzle')
ASSETS_DIR = os.path.join(_MODULE_DIR, 'assets')

# ── Static file serving ────────────────────────────────────────────────────

@block_puzzle_bp.route('/')
@block_puzzle_bp.route('')
def index():
    return send_from_directory(STATIC_DIR, 'block-puzzle.html')

@block_puzzle_bp.route('/mp')
def mp():
    return send_from_directory(STATIC_DIR, 'block-puzzle-mp.html')

@block_puzzle_bp.route('/levels.json')
def levels():
    resp = make_response(send_from_directory(STATIC_DIR, 'levels.json'))
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp

@block_puzzle_bp.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(ASSETS_DIR, filename)

# ── DB ─────────────────────────────────────────────────────────────────────

def init_block_puzzle_db(app):
    db = sqlite3.connect(DB_PATH)
    db.executescript('''
        CREATE TABLE IF NOT EXISTS bp_rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code TEXT UNIQUE NOT NULL,
            created_at INTEGER NOT NULL,
            status TEXT DEFAULT 'waiting',
            p1_name TEXT, p2_name TEXT,
            p1_level INTEGER DEFAULT 0, p2_level INTEGER DEFAULT 0,
            p1_moves INTEGER DEFAULT 0, p2_moves INTEGER DEFAULT 0,
            p1_time_ms INTEGER DEFAULT 0, p2_time_ms INTEGER DEFAULT 0,
            winner_id INTEGER DEFAULT NULL,
            p1_vote TEXT DEFAULT NULL, p2_vote TEXT DEFAULT NULL
        );
        CREATE TABLE IF NOT EXISTS bp_state_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code TEXT NOT NULL, player_id INTEGER NOT NULL,
            level_index INTEGER NOT NULL, blocks_json TEXT NOT NULL,
            moves INTEGER DEFAULT 0, time_ms INTEGER DEFAULT 0,
            updated_at INTEGER NOT NULL
        );
    ''')
    db.commit(); db.close()
    print(f'[block_puzzle] DB ready at {DB_PATH}')

def get_bp_db():
    db = getattr(g, '_bp_db', None)
    if db is None:
        db = g._bp_db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def bp_query(sql, args=(), one=False):
    db = get_bp_db(); cur = db.execute(sql, args); rv = cur.fetchall(); db.commit()
    return (rv[0] if rv else None) if one else rv

def bp_mutate(sql, args=()):
    db = get_bp_db(); cur = db.execute(sql, args); db.commit(); return cur.lastrowid

def gen_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@block_puzzle_bp.teardown_request
def close_bp_db(error):
    db = getattr(g, '_bp_db', None)
    if db: db.close()

def _get_room(room_code):
    db = sqlite3.connect(DB_PATH); db.row_factory = sqlite3.Row
    row = db.execute('SELECT * FROM bp_rooms WHERE room_code=?', (room_code,)).fetchone()
    db.close(); return row

def _update_room(room_code, **kwargs):
    sets = ', '.join(f'{k}=?' for k in kwargs)
    vals = list(kwargs.values()) + [room_code]
    db = sqlite3.connect(DB_PATH)
    db.execute(f'UPDATE bp_rooms SET {sets} WHERE room_code=?', vals)
    db.commit(); db.close()

# ── REST ───────────────────────────────────────────────────────────────────

@block_puzzle_bp.route('/api/game/create', methods=['POST'])
def create_game():
    data = request.get_json() or {}
    name = data.get('display_name', 'Player 1')[:20]
    for _ in range(10):
        code = gen_room_code()
        if not bp_query('SELECT id FROM bp_rooms WHERE room_code=?', (code,), one=True):
            break
    bp_mutate('INSERT INTO bp_rooms (room_code,created_at,status,p1_name) VALUES (?,?,?,?)',
              (code, int(time.time()), 'waiting', name))
    return jsonify({'room_code': code, 'player_id': 1})

@block_puzzle_bp.route('/api/game/join', methods=['POST'])
def join_game():
    data = request.get_json() or {}
    code = data.get('room_code', '').strip().upper()
    name = data.get('display_name', 'Player 2')[:20]
    room = bp_query('SELECT * FROM bp_rooms WHERE room_code=?', (code,), one=True)
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    if room['status'] != 'waiting':
        return jsonify({'error': 'Room is full or already started'}), 400
    bp_mutate('UPDATE bp_rooms SET p2_name=?, status=? WHERE room_code=?', (name, 'playing', code))
    return jsonify({'room_code': code, 'player_id': 2, 'opponent_name': room['p1_name']})

@block_puzzle_bp.route('/api/game/<room_code>', methods=['GET'])
def get_game(room_code):
    room = bp_query('SELECT * FROM bp_rooms WHERE room_code=?', (room_code.upper(),), one=True)
    if not room: return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(room))
