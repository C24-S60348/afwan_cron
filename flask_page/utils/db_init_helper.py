#utils/db_init_helper.py
"""
Unified database initialization for all Ular games
"""
import sqlite3
import os
from flask import g

def init_all_ular_databases():
    """
    Initialize all Ular game databases in one function
    This includes both /ular and /ularular games
    """
    print("\n" + "="*60)
    print("🎮 Initializing Ular Games Databases")
    print("="*60)
    
    # Initialize both databases
    init_ular_db()
    init_ularular_db()
    
    print("="*60)
    print("✅ All databases initialized successfully!")
    print("="*60 + "\n")


def init_ular_db():
    """Initialize static/db/ular.db (quiz-based game)"""
    from ..utils.db_helper import af_getdb
    
    dbloc = "static/db/ular.db"
    print(f"🔧 Initializing {dbloc}...")
    
    try:
        # Ensure directory exists
        os.makedirs("static/db", exist_ok=True)
        
        # Create conf table
        query = """CREATE TABLE IF NOT EXISTS conf (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start TEXT,
            end TEXT,
            type TEXT
        );"""
        af_getdb(dbloc, query, ())
        
        # Create room table
        query = """CREATE TABLE IF NOT EXISTS room (
            code TEXT PRIMARY KEY,
            turn TEXT,
            state TEXT,
            questionid TEXT,
            maxbox INTEGER,
            topic TEXT,
            dice INTEGER DEFAULT 0
        );"""
        af_getdb(dbloc, query, ())
        
        # Create players table
        query = """CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            player TEXT,
            pos INTEGER,
            color TEXT,
            questionright TEXT,
            questionget TEXT
        );"""
        af_getdb(dbloc, query, ())
        
        # Create questions table
        query = """CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            question TEXT,
            a1 TEXT,
            a2 TEXT,
            a3 TEXT,
            a4 TEXT,
            answer TEXT,
            topic TEXT
        );"""
        af_getdb(dbloc, query, ())
        
        # Check if conf table is empty and add sample data
        query = "SELECT COUNT(*) as count FROM conf;"
        result = af_getdb(dbloc, query, ())
        if isinstance(result, list) and len(result) > 0 and result[0].get('count', 0) == 0:
            query = """INSERT INTO conf (start, end, type) VALUES 
                ('3', '10', 'ladder'),
                ('6', '15', 'ladder'),
                ('12', '20', 'ladder'),
                ('18', '8', 'snake'),
                ('22', '12', 'snake'),
                ('25', '5', 'snake');"""
            af_getdb(dbloc, query, ())
            print("  ✅ Added sample ladder/snake configurations")
        
        # Check if questions table is empty and add sample data
        query = "SELECT COUNT(*) as count FROM questions;"
        result = af_getdb(dbloc, query, ())
        if isinstance(result, list) and len(result) > 0 and result[0].get('count', 0) == 0:
            query = """INSERT INTO questions (id, question, a1, a2, a3, a4, answer, topic) VALUES 
                ('1', 'What is the formula for force?', 'F=ma', 'F=mv', 'F=mgh', 'F=1/2mv^2', 'a1', 'fizik'),
                ('2', 'What is the speed of light in vacuum?', '3x10^6 m/s', '3x10^7 m/s', '3x10^8 m/s', '3x10^9 m/s', 'a3', 'fizik'),
                ('3', 'What is Newton''s first law about?', 'Force', 'Inertia', 'Acceleration', 'Momentum', 'a2', 'fizik'),
                ('4', 'What is the unit of energy?', 'Newton', 'Watt', 'Joule', 'Pascal', 'a3', 'fizik'),
                ('5', 'What is the powerhouse of the cell?', 'Nucleus', 'Ribosome', 'Mitochondria', 'Chloroplast', 'a3', 'biologi'),
                ('6', 'What is the process by which plants make food?', 'Respiration', 'Photosynthesis', 'Digestion', 'Fermentation', 'a2', 'biologi'),
                ('7', 'What is DNA?', 'A protein', 'A genetic material', 'A carbohydrate', 'A lipid', 'a2', 'biologi'),
                ('8', 'What is the largest organ in the human body?', 'Heart', 'Liver', 'Brain', 'Skin', 'a4', 'biologi');"""
            af_getdb(dbloc, query, ())
            print("  ✅ Added sample questions")
        
        print(f"  ✅ {dbloc} initialized")
        
    except Exception as e:
        print(f"  ❌ Error initializing {dbloc}: {e}")


def init_ularular_db():
    """Initialize ularular.db (simple game without questions)"""
    dbloc = "ularular.db"
    print(f"🔧 Initializing {dbloc}...")
    
    try:
        # Get or create database connection
        if "db" in g:
            db = g.db
        else:
            db = sqlite3.connect(dbloc)
            db.row_factory = sqlite3.Row
        
        cursor = db.cursor()
        
        # Create tables
        cursor.executescript("""
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
        
        # Only close if we created a new connection
        if "db" not in g:
            db.close()
        
        print(f"  ✅ {dbloc} initialized")
        
    except Exception as e:
        print(f"  ❌ Error initializing {dbloc}: {e}")
        if "db" not in g and 'db' in locals():
            db.rollback()
            db.close()
