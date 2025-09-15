from flask import Blueprint, request, jsonify
from datetime import datetime
import random

ularular_bp = Blueprint("ularular", __name__, url_prefix="/ularular")

# In-memory storage
rooms = {}

# Snake & ladder positions
snakes = {16:6, 47:26, 49:11, 56:53, 62:19, 64:60, 87:24, 93:73, 95:75, 98:78}
ladders = {1:38, 4:14, 9:31, 21:42, 28:84, 36:44, 51:67, 71:91, 80:100}

def apply_dice(pos, dice):
    new_pos = pos + dice
    if new_pos > 100:
        return pos
    if new_pos in snakes:
        new_pos = snakes[new_pos]
    if new_pos in ladders:
        new_pos = ladders[new_pos]
    return new_pos

@ularular_bp.route("/create_room", methods=["POST"])
def create_room():
    data = request.json
    code = data.get("code")
    player = data.get("player")

    rooms[code] = {
        "players": {player: 0},
        "turn": player,
        "state": "waiting",
        "moves": []
    }
    return jsonify({"room": code, "turn": player})

@ularular_bp.route("/join_room", methods=["POST"])
def join_room():
    data = request.json
    code = data.get("code")
    player = data.get("player")

    if code not in rooms:
        return jsonify({"error": "Room not found"}), 404

    rooms[code]["players"][player] = 0
    return jsonify({"room": code, "players": list(rooms[code]["players"].keys())})

@ularular_bp.route("/roll_dice", methods=["POST"])
def roll_dice():
    data = request.json
    code = data.get("code")
    player = data.get("player")

    room = rooms.get(code)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    if room["turn"] != player:
        return jsonify({"error": "Not your turn"}), 400

    dice = random.randint(1, 6)
    pos = room["players"][player]
    new_pos = apply_dice(pos, dice)
    room["players"][player] = new_pos

    if new_pos == 100:
        room["state"] = "finished"

    players = list(room["players"].keys())
    idx = players.index(player)
    room["turn"] = players[(idx + 1) % len(players)]

    room["moves"].append({
        "player": player,
        "dice": dice,
        "pos": new_pos,
        "time": datetime.now().isoformat()
    })

    return jsonify({
        "dice": dice,
        "pos": new_pos,
        "turn": room["turn"],
        "state": room["state"]
    })

@ularular_bp.route("/get_state/<code>")
def get_state(code):
    room = rooms.get(code)
    if not room:
        return jsonify({"error": "Room not found"}), 404
    return jsonify(room)