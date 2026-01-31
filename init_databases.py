#!/usr/bin/env python3
"""
Database Initialization Script for Ular Games
This script initializes both ular.db and ularular.db with the correct schema and sample data.
Run this script to set up or reset the databases.

Usage:
    python3 init_databases.py
"""

import sqlite3
import os
import sys

# Add the project root to the path so we can import Flask modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_ular_db():
    """Initialize static/db/ular.db with correct schema and sample data"""
    db_path = "static/db/ular.db"
    
    print(f"🔧 Initializing {db_path}...")
    
    if not os.path.exists("static/db"):
        os.makedirs("static/db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create conf table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conf (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start TEXT,
                end TEXT,
                type TEXT
            );
        """)
        
        # Create room table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS room (
                code TEXT PRIMARY KEY,
                turn TEXT,
                state TEXT,
                questionid TEXT,
                maxbox INTEGER,
                topic TEXT,
                dice INTEGER DEFAULT 0
            );
        """)
        
        # Create players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT,
                player TEXT,
                pos INTEGER,
                color TEXT,
                questionright TEXT,
                questionget TEXT
            );
        """)
        
        # Create questions table with multiple choice fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                question TEXT,
                a1 TEXT,
                a2 TEXT,
                a3 TEXT,
                a4 TEXT,
                answer TEXT,
                topic TEXT
            );
        """)
        
        # Check if conf table is empty and add sample data
        cursor.execute("SELECT COUNT(*) FROM conf;")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO conf (start, end, type) VALUES (?, ?, ?)",
                [
                    ('3', '12', 'ladder'),
                    ('8', '21', 'ladder'),
                    ('18', '25', 'ladder'),
                    ('16', '28', 'ladder'),
                    ('15', '2', 'snake'),
                    ('17', '11', 'snake'),
                    ('23', '10', 'snake'),
                    ('9', '4', 'snake'),
                ]
            )
            print("  ✅ Added sample ladder/snake configurations")
        
        # Check if questions table is empty and add sample data
        cursor.execute("SELECT COUNT(*) FROM questions;")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO questions (id, question, a1, a2, a3, a4, answer, topic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    ('1', 'What is the formula for force?', 'F=ma', 'F=mv', 'F=mgh', 'F=1/2mv^2', 'a1', 'fizik'),
                    ('2', 'What is the speed of light in vacuum?', '3x10^6 m/s', '3x10^7 m/s', '3x10^8 m/s', '3x10^9 m/s', 'a3', 'fizik'),
                    ('3', 'What is Newton\'s first law about?', 'Force', 'Inertia', 'Acceleration', 'Momentum', 'a2', 'fizik'),
                    ('4', 'What is the unit of energy?', 'Newton', 'Watt', 'Joule', 'Pascal', 'a3', 'fizik'),
                    ('5', 'What is the powerhouse of the cell?', 'Nucleus', 'Ribosome', 'Mitochondria', 'Chloroplast', 'a3', 'biologi'),
                    ('6', 'What is the process by which plants make food?', 'Respiration', 'Photosynthesis', 'Digestion', 'Fermentation', 'a2', 'biologi'),
                    ('7', 'What is DNA?', 'A protein', 'A genetic material', 'A carbohydrate', 'A lipid', 'a2', 'biologi'),
                    ('8', 'What is the largest organ in the human body?', 'Heart', 'Liver', 'Brain', 'Skin', 'a4', 'biologi'),
                ]
            )
            print("  ✅ Added sample questions")
        
        conn.commit()
        print(f"✅ {db_path} initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing {db_path}: {e}")
        conn.rollback()
    finally:
        conn.close()


def init_ularular_db():
    """Initialize ularular.db with correct schema"""
    db_path = "ularular.db"
    
    print(f"🔧 Initializing {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create rooms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                code TEXT PRIMARY KEY,
                turn TEXT,
                state TEXT
            );
        """)
        
        # Create players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                room_code TEXT,
                player TEXT,
                pos INTEGER,
                PRIMARY KEY (room_code, player)
            );
        """)
        
        # Create moves table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_code TEXT,
                player TEXT,
                dice INTEGER,
                pos INTEGER,
                time TEXT
            );
        """)
        
        conn.commit()
        print(f"✅ {db_path} initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing {db_path}: {e}")
        conn.rollback()
    finally:
        conn.close()


def verify_databases():
    """Verify that all tables exist and have correct structure"""
    print("\n📋 Verifying databases...")
    
    # Verify ular.db
    db_path = "static/db/ular.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  {db_path} tables: {', '.join(tables)}")
        
        # Count records
        for table in tables:
            if table != 'sqlite_sequence':
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"    - {table}: {count} records")
        conn.close()
    else:
        print(f"  ❌ {db_path} not found")
    
    # Verify ularular.db
    db_path = "ularular.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  {db_path} tables: {', '.join(tables)}")
        
        # Count records
        for table in tables:
            if table != 'sqlite_sequence':
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"    - {table}: {count} records")
        conn.close()
    else:
        print(f"  ❌ {db_path} not found")


if __name__ == "__main__":
    print("=" * 60)
    print("🎮 ULAR GAMES DATABASE INITIALIZATION")
    print("=" * 60)
    print()
    
    # Option 1: Use Flask app context (preferred - ensures consistency)
    try:
        from flask import Flask
        from flask_page.utils.db_init_helper import init_all_ular_databases
        
        app = Flask(__name__)
        with app.app_context():
            init_all_ular_databases()
    except Exception as e:
        print(f"⚠️  Flask initialization failed: {e}")
        print("   Falling back to direct database initialization...")
        
        # Option 2: Direct initialization (fallback)
        init_ular_db()
        print()
        init_ularular_db()
    
    # Verify
    verify_databases()
    
    print()
    print("=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("  1. On your server, run: python3 init_databases.py")
    print("  2. Or let the app auto-initialize on startup (already configured)")
    print("  3. Restart your Flask app: sudo systemctl restart afwanapp")
    print()
