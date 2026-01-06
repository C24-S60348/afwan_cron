#controllers/badminton.py
import random
from flask import abort, jsonify, request, Blueprint, render_template, render_template_string, send_from_directory, session
from apps.utils.html_helper import *
from apps.utils.db_helper import *
from datetime import datetime
import sqlite3
import random
import hashlib
import os

DB_DIR = "db"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

badminton_bp = Blueprint('badminton', __name__)

DB_FILE = "db/badminton.db"

#Initialize DB --------------
def init_db():

    if not os.path.isfile(DB_FILE):
        # Create the database file
        open(DB_FILE, 'a').close() 

    """Initialize database tables"""
    db = af_connectdb(DB_FILE)
    cursor = db.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password_hash TEXT,
            is_staff TEXT DEFAULT 'true',
            created_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            time TEXT,
            score TEXT DEFAULT "0-0",
            remark TEXT,
            playerleft TEXT,
            playerright TEXT,
            userid TEXT,
            created_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            time TEXT,
            score TEXT DEFAULT "0-0",
            remark TEXT,
            playerleft TEXT,
            playerright TEXT,
            userid TEXT,
            created_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            comment TEXT,
            created_at TEXT
        )
    ''')

    # Insert default
    cursor.execute("INSERT OR IGNORE INTO users (name) VALUES (?)", ('this is sample',))
    cursor.execute("INSERT OR IGNORE INTO history (name) VALUES (?)", ('this is sample',))
    cursor.execute("INSERT OR IGNORE INTO suggestions (name) VALUES (?)", ('this is sample',))

    db.commit()
    db.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

# # Initialize database when blueprint is registered
# @badminton_bp.before_app_request
# def setup():
#     init_db()
    
@badminton_bp.route("/badminton/initdb")
def initdb():
    try:
        init_db()
        return jsonify({"db initiated": "ehe"})
    except Exception as e:
        return jsonify({"db error": e})
    

#---------------------------------------------


@badminton_bp.route("/badminton")
def main():
    return render_template("badminton.html")

#dashboard-------------------------------------
@badminton_bp.route('/badminton/handle', methods=['GET', 'POST'])
def handle():
    endpoint = "badminton"
    dbloc = DB_FILE

    return render_template("dbviewer2.html", endpoint=endpoint, dbloc=dbloc)


@badminton_bp.route('/badminton/query', methods=['GET', 'POST'])
def query():

    # dbloc = getpostget("dbloc")
    query = getpostget("query")
    params = getpostget("parameter")
    secret = getpostget("secret")
    if secret != "afwan":
        return jsonify({"error": "invalid secret"})
    
    dbdata = af_getdb(DB_FILE, query, params)
    return jsonify(dbdata)
#---------------------------------------------

@badminton_bp.route('/badminton/api/gethistory', methods=['GET', 'POST'])
def gethistory():

    # dbloc = getpostget("dbloc")
    userid = getpostget("userid")
    query = "SELECT * FROM history WHERE userid = ?"
    params = (userid,)
    
    dbdata = af_getdb(DB_FILE, query, params)
    return jsonify(dbdata)


@badminton_bp.route('/badminton/api/inserthistory', methods=['GET', 'POST'])
def inserthistory():

    query = "INSERT INTO history (userid,date,playerleft,playerright,remark,score,time,created_at)"
    query += " VALUES (?,?,?,?,?,?,?,?)"
    
    userid = getpostget("userid")
    date = getpostget("date")
    playerleft = getpostget("playerleft")
    playerright = getpostget("playerright")
    remark = getpostget("remark")
    score = getpostget("score")
    time = getpostget("time")
    created_at = datetime.now()

    params = (userid,date,playerleft,playerright,remark,score,time,created_at,)
    
    dbdata = af_getdb(DB_FILE, query, params)
    return jsonify(dbdata)

@badminton_bp.route('/badminton/api/updatehistory', methods=['GET', 'POST'])
def updatehistory():

    query = "UPDATE history"
    query += " SET userid = ?, date = ?, playerleft = ?, playerright = ?, remark = ?, score = ?, time = ?, created_at = ?"
    query += " WHERE id = ?"
    
    userid = getpostget("userid")
    date = getpostget("date")
    playerleft = getpostget("playerleft")
    playerright = getpostget("playerright")
    remark = getpostget("remark")
    score = getpostget("score")
    time = getpostget("time")
    created_at = datetime.now()
    id = getpostget("id")

    params = (userid, date, playerleft, playerright, remark, score, time, created_at, id)
    
    dbdata = af_getdb(DB_FILE, query, params)
    return jsonify(dbdata)

@badminton_bp.route('/badminton/api/getsummary', methods=['GET', 'POST'])
def getsummary():
    userid = getpostget("userid")
    query = "SELECT * FROM history WHERE userid = ?"
    params = (userid,)
    
    dbdata = af_getdb(DB_FILE, query, params)

    # Dictionary to track player wins
    player_wins = {}
    
    # Count wins for each player
    for game in dbdata:
        score = game.get('score', '0-0')
        playerleft = game.get('playerleft', 'Left')
        playerright = game.get('playerright', 'Right')
        
        # Initialize players if not exists
        if playerleft not in player_wins:
            player_wins[playerleft] = 0
        if playerright not in player_wins:
            player_wins[playerright] = 0
        
        # Parse score (format: "21-19")
        try:
            scores = score.split('-')
            if len(scores) == 2:
                left_score = int(scores[0])
                right_score = int(scores[1])
                
                # Determine winner
                if left_score > right_score:
                    player_wins[playerleft] += 1
                elif right_score > left_score:
                    player_wins[playerright] += 1
        except (ValueError, AttributeError):
            # Skip invalid scores
            continue
    
    # Format result
    result = {
        "summary": "Player Win Summary",
        "players": player_wins,
        "total_games": len(dbdata)
    }
            
    return jsonify(result)

@badminton_bp.route('/badminton/api/insertsuggestions', methods=['GET', 'POST'])
def insertsuggestions():

    query = "INSERT INTO suggestions (name,comment,created_at)"
    query += " VALUES (?,?,?)"
    
    name = getpostget("name")
    comment = getpostget("comment")
    created_at = datetime.now()

    params = (name,comment,created_at,)
    
    dbdata = af_getdb(DB_FILE, query, params)
    return jsonify(dbdata)