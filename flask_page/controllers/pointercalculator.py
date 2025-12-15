from flask import Blueprint, request, jsonify, g
from datetime import datetime
import sqlite3
import random
import hashlib
import os

pointercalculator_bp = Blueprint("pointercalculator", __name__, url_prefix="/pointercalculator")

DB_FILE = "pointercalculator.db"

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database tables"""
    db = get_db()
    cursor = db.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            is_student TEXT NOT NULL DEFAULT 'true',
            created_at TEXT NOT NULL
        )
    ''')

    # Create grades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            semester TEXT NOT NULL,
            stem TEXT NOT NULL,
            mentor TEXT NOT NULL,
            course_name TEXT NOT NULL,
            grade TEXT NOT NULL,
            credit_hours TEXT NOT NULL,
            grade_point TEXT NOT NULL,
            total_points TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create stem_options table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stem_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create mentor_options table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mentor_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Insert default STEM options if not exists
    cursor.execute("INSERT OR IGNORE INTO stem_options (name) VALUES (?)", ('A',))
    cursor.execute("INSERT OR IGNORE INTO stem_options (name) VALUES (?)", ('B (Tanpa biologi)',))
    cursor.execute("INSERT OR IGNORE INTO stem_options (name) VALUES (?)", ('B (Tanpa fizik)',))
    cursor.execute("INSERT OR IGNORE INTO stem_options (name) VALUES (?)", ('B (Tanpa Kimia)',))

    # Insert default mentor options if not exists
    cursor.execute("INSERT OR IGNORE INTO mentor_options (name) VALUES (?)", ('Pn Mimi Syazwani',))
    cursor.execute("INSERT OR IGNORE INTO mentor_options (name) VALUES (?)", ('Pn Shida',))

    db.commit()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

# Initialize database when blueprint is registered
@pointercalculator_bp.before_app_request
def setup():
    init_db()

@pointercalculator_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        user_id = data.get('id', '').strip()
        password = data.get('password', '').strip()
        is_student = str(data.get('isStudent', True)).lower()

        if not user_id or not password:
            return jsonify({'success': False, 'message': 'ID and password are required'}), 400

        db = get_db()
        cursor = db.cursor()

        cursor.execute('''
            SELECT id, name, email, password_hash, is_student
            FROM users
            WHERE id = ? AND is_student = ?
        ''', (user_id, is_student))

        user = cursor.fetchone()

        if user and verify_password(password, user['password_hash']):
            # Generate a simple token (in production, use JWT)
            token = hashlib.sha256(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()

            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email'],
                    'is_student': user['is_student'] == 'true'
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@pointercalculator_bp.route('/register', methods=['POST'])
def register():
    """Student registration endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        matric_no = data.get('matricNo', '').strip()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not all([matric_no, name, email, password]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

        db = get_db()
        cursor = db.cursor()

        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE id = ?', (matric_no,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'User already exists'}), 409

        # Insert new user
        cursor.execute('''
            INSERT INTO users (id, name, email, password_hash, is_student, created_at)
            VALUES (?, ?, ?, ?, 'true', ?)
        ''', (matric_no, name, email, hash_password(password), datetime.now().isoformat()))

        db.commit()

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': matric_no,
                'name': name,
                'email': email
            }
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@pointercalculator_bp.route('/results/<user_id>', methods=['GET'])
def get_semester_results(user_id):
    """Get semester results for a user"""
    try:
        db = get_db()
        cursor = db.cursor()

        # Get all semesters with their calculations
        cursor.execute('''
            SELECT
                semester,
                SUM(CAST(credit_hours AS REAL)) as total_credits,
                SUM(CAST(total_points AS REAL)) as total_points
            FROM grades
            WHERE user_id = ?
            GROUP BY semester
            ORDER BY semester
        ''', (user_id,))

        semesters = cursor.fetchall()
        results = []

        for semester in semesters:
            total_credits = float(semester['total_credits'] or 0)
            total_points = float(semester['total_points'] or 0)
            png = total_points / total_credits if total_credits > 0 else 0

            results.append({
                'semester': int(semester['semester']),
                'png': round(png, 2) if total_credits > 0 else None,
                'totalCredits': int(total_credits)
            })

        return jsonify({
            'success': True,
            'results': results
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@pointercalculator_bp.route('/stem', methods=['GET'])
def get_stem_options():
    """Get all STEM options"""
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT id, name FROM stem_options ORDER BY name')
        stem_options = cursor.fetchall()

        result = [{'id': row['id'], 'name': row['name']} for row in stem_options]

        return jsonify({
            'success': True,
            'stem': result
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@pointercalculator_bp.route('/mentors', methods=['GET'])
def get_mentor_options():
    """Get all mentor options"""
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT id, name FROM mentor_options ORDER BY name')
        mentor_options = cursor.fetchall()

        result = [{'id': row['id'], 'name': row['name']} for row in mentor_options]

        return jsonify({
            'success': True,
            'mentors': result
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@pointercalculator_bp.route('/grades', methods=['POST'])
def submit_grades():
    """Submit grade calculations"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        user_id = data.get('userId', '').strip()
        semester = str(data.get('semester', ''))
        stem = data.get('stem', '').strip()
        mentor = data.get('mentor', '').strip()
        courses = data.get('courses', [])

        if not all([user_id, semester, stem, mentor]) or not courses:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        db = get_db()
        cursor = db.cursor()

        # Insert each course grade
        for course in courses:
            cursor.execute('''
                INSERT INTO grades (
                    user_id, semester, stem, mentor,
                    course_name, grade, credit_hours, grade_point, total_points, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, semester, stem, mentor,
                course.get('name', ''),
                course.get('grade', ''),
                str(course.get('creditHours', 0)),
                str(course.get('gradePoint', 0.0)),
                str(course.get('total', 0.0)),
                datetime.now().isoformat()
            ))

        db.commit()

        return jsonify({
            'success': True,
            'message': 'Grades submitted successfully'
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

# Health check endpoint
@pointercalculator_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200
