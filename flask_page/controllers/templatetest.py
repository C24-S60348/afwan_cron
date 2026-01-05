#controllers/templatetest.py
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

templatetest_bp = Blueprint('templatetest', __name__)

DB_FILE = "db/templatetest.db"

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

    # Insert default
    cursor.execute("INSERT OR IGNORE INTO users (name) VALUES (?)", ('this is sample',))

    db.commit()
    db.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

# # Initialize database when blueprint is registered
# @templatetest_bp.before_app_request
# def setup():
#     init_db()
    
@templatetest_bp.route("/templatetest/initdb")
def initdb():
    try:
        init_db()
        return jsonify({"db initiated": "ehe"})
    except Exception as e:
        return jsonify({"db error": e})
    

#---------------------------------------------


@templatetest_bp.route("/templatetest")
def main():
    return render_template("templatetest.html")

#dashboard-------------------------------------
@templatetest_bp.route('/templatetest/handle', methods=['GET', 'POST'])
def handle():
    endpoint = "templatetest"
    dbloc = DB_FILE

    return render_template("dbviewer2.html", endpoint=endpoint, dbloc=dbloc)


@templatetest_bp.route('/templatetest/query', methods=['GET', 'POST'])
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