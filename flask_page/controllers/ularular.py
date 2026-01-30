from flask import Blueprint, request, jsonify, g
from datetime import datetime
import sqlite3
import random

ularular_bp = Blueprint("ularular", __name__, url_prefix="/ularular")

DB_FILE = "ularular.db"

# 🐍 Snakes & ladders positions
snakes = {16:6, 47:26, 49:11, 56:53, 62:19, 64:60, 87:24, 93:73, 95:75, 98:78}
ladders = {1:38, 4:14, 9:31, 21:42, 28:84, 36:44, 51:67, 71:91, 80:100}

# ----------------------
# DB Helpers
# ----------------------
def ularular_get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row
    return g.db

@ularular_bp.teardown_app_request
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def ularular_init_db():
    """Initialize ularular database tables if they don't exist"""
    db = ularular_get_db()
    
    try:
        # Check if tables exist and have correct structure
        cursor = db.cursor()
        
        # Get existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        # Create tables if they don't exist
        db.executescript("""
        CREATE TABLE IF NOT EXISTS rooms (
            code TEXT PRIMARY KEY,
            turn TEXT,
            state TEXT
        );

        CREATE TABLE IF NOT EXISTS players (
            room_code TEXT,
            player TEXT,
            pos INTEGER,
            PRIMARY KEY (room_code, player)
        );

        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code TEXT,
            player TEXT,
            dice INTEGER,
            pos INTEGER,
            time TEXT
        );
        """)
        db.commit()
        print("✅ Ularular database tables initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing ularular database: {e}")
        db.rollback()

# ----------------------
# Game Logic
# ----------------------
def apply_dice(pos, dice):
    new_pos = pos + dice
    if new_pos > 100:
        return pos
    if new_pos in snakes:
        new_pos = snakes[new_pos]
    if new_pos in ladders:
        new_pos = ladders[new_pos]
    return new_pos

import string
import random

def generate_room_code(length=4):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# ----------------------
# Endpoints
# ----------------------
@ularular_bp.route("/create_room", methods=["POST"])
def create_room():
    data = request.json
    #code = data.get("code")
    code = generate_room_code()
    player = data.get("player")

    db = ularular_get_db()
    db.execute("INSERT INTO rooms (code, turn, state) VALUES (?, ?, ?)",
               (code, player, "waiting"))
    db.execute("INSERT INTO players (room_code, player, pos) VALUES (?, ?, ?)",
               (code, player, 0))
    db.commit()

    return jsonify({"room": code, "turn": player})

@ularular_bp.route("/join_room", methods=["POST"])
def join_room():
    data = request.json
    code = data.get("code")
    player = data.get("player")

    db = ularular_get_db()
    room = db.execute("SELECT * FROM rooms WHERE code=?", (code,)).fetchone()
    if not room:
        return jsonify({"error": "Room not found"}), 404

    db.execute("INSERT OR IGNORE INTO players (room_code, player, pos) VALUES (?, ?, ?)",
               (code, player, 0))
    db.commit()

    players = db.execute("SELECT player FROM players WHERE room_code=?", (code,)).fetchall()
    return jsonify({"room": code, "players": [p["player"] for p in players]})

@ularular_bp.route("/roll_dice", methods=["POST"])
def roll_dice():
    data = request.json
    code = data.get("code")
    player = data.get("player")

    db = ularular_get_db()
    room = db.execute("SELECT * FROM rooms WHERE code=?", (code,)).fetchone()
    if not room:
        return jsonify({"error": "Room not found"}), 404

    if room["turn"] != player:
        return jsonify({"error": "Not your turn"}), 400

    # get current position
    pos_row = db.execute("SELECT pos FROM players WHERE room_code=? AND player=?", 
                         (code, player)).fetchone()
    pos = pos_row["pos"]

    dice = random.randint(1, 6)
    new_pos = apply_dice(pos, dice)

    db.execute("UPDATE players SET pos=? WHERE room_code=? AND player=?", 
               (new_pos, code, player))

    state = room["state"]
    if new_pos == 100:
        state = "finished"
        db.execute("UPDATE rooms SET state=? WHERE code=?", (state, code))

    # determine next turn
    players = db.execute("SELECT player FROM players WHERE room_code=?", (code,)).fetchall()
    player_list = [p["player"] for p in players]
    idx = player_list.index(player)
    next_turn = player_list[(idx + 1) % len(player_list)]

    db.execute("UPDATE rooms SET turn=? WHERE code=?", (next_turn, code))
    db.execute(
        "INSERT INTO moves (room_code, player, dice, pos, time) VALUES (?, ?, ?, ?, ?)",
        (code, player, dice, new_pos, datetime.now().isoformat())
    )
    db.commit()

    return jsonify({
        "dice": dice,
        "pos": new_pos,
        "turn": next_turn,
        "state": state
    })

@ularular_bp.route("/get_state/<code>")
def get_state(code):
    db = ularular_get_db()
    room = db.execute("SELECT * FROM rooms WHERE code=?", (code,)).fetchone()
    if not room:
        return jsonify({"error": "Room not found"}), 404

    players = db.execute("SELECT player, pos FROM players WHERE room_code=?", (code,)).fetchall()
    moves = db.execute("SELECT * FROM moves WHERE room_code=? ORDER BY id DESC LIMIT 10", 
                       (code,)).fetchall()

    return jsonify({
        "room": dict(room),
        "players": {p["player"]: p["pos"] for p in players},
        "moves": [dict(m) for m in moves]
    })