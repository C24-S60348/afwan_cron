import os
import json
from flask import Blueprint, request, jsonify, send_from_directory, Response, abort, redirect
from flask_page.utils.db_helper import get_connection, ensure_tables

catalogbaju_bp = Blueprint('catalogbaju', __name__, url_prefix='/catalogbaju')

_MODULE_DIR = os.path.dirname(__file__)
_STATIC_DIR = os.path.realpath(os.path.join(_MODULE_DIR, 'static'))
_JS_DIR     = os.path.join(_STATIC_DIR, 'js')
_APP_NAME   = 'catalogbaju'

_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.avif'}

# Built-in SVG placeholder for missing product images
_PLACEHOLDER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
  <rect width="300" height="300" rx="14" fill="#0f172a"/>
  <path d="M95,95 L45,130 L70,145 L70,235 L230,235 L230,145 L255,130 L205,95 Q175,110 150,125 Q125,110 95,95 Z"
        fill="#1e293b" stroke="#334155" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M125,110 Q150,125 175,110" fill="none" stroke="#475569" stroke-width="2" stroke-linecap="round"/>
  <text x="150" y="268" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif"
        font-size="13" fill="#475569">No image</text>
</svg>"""

# Table names: projectname_tablename_db
_T_CATALOG     = 'catalogbaju_catalog_db'
_T_ASK_OWNER   = 'catalogbaju_askowoner_db'
_T_GUEST_CARTS = 'catalogbaju_guestcarts_db'


# ── DB init (called once on server start) ─────────────────────────────────────

def init_catalogbaju_db():
    """
    Create tables if they don't exist, then seed catalog from
    appsettings.json if the catalog table is empty.
    Called from afwanhaziqmy.py app context on startup.
    """
    ensure_tables(_APP_NAME, [
        f"""CREATE TABLE IF NOT EXISTS {_T_CATALOG} (
            id          INTEGER PRIMARY KEY,
            name        TEXT    NOT NULL DEFAULT '',
            price       TEXT             DEFAULT '',
            price_min   TEXT             DEFAULT '',
            price_max   TEXT             DEFAULT '',
            category    TEXT             DEFAULT '',
            description TEXT             DEFAULT '',
            image       TEXT             DEFAULT '',
            images      TEXT             DEFAULT '[]',
            sizes       TEXT             DEFAULT '[]'
        )""",
        f"""CREATE TABLE IF NOT EXISTS {_T_ASK_OWNER} (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id   TEXT DEFAULT '',
            name      TEXT DEFAULT '',
            image     TEXT DEFAULT '',
            timestamp TEXT DEFAULT ''
        )""",
        f"""CREATE TABLE IF NOT EXISTS {_T_GUEST_CARTS} (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_id           TEXT UNIQUE NOT NULL,
            cart               TEXT DEFAULT '[]',
            submitted_to_owner INTEGER  DEFAULT 0
        )""",
    ])
    _seed_catalog_if_empty()


def _load_default_catalog():
    try:
        with open(os.path.join(_STATIC_DIR, 'appsettings.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        items = data.get('catalog', {}).get('items', [])
        return items if isinstance(items, list) else []
    except Exception:
        return []


def _seed_catalog_if_empty():
    conn = get_connection(_APP_NAME)
    try:
        count = conn.execute(f'SELECT COUNT(*) FROM {_T_CATALOG}').fetchone()[0]
        if count == 0:
            for item in _load_default_catalog():
                conn.execute(
                    f"""INSERT OR IGNORE INTO {_T_CATALOG}
                        (id, name, price, price_min, price_max, category, description, image, images, sizes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        item.get('id'),
                        item.get('name', ''),
                        item.get('price', ''),
                        item.get('priceMin', ''),
                        item.get('priceMax', ''),
                        item.get('category', ''),
                        item.get('description', ''),
                        item.get('image', ''),
                        json.dumps(item.get('images', [])),
                        json.dumps(item.get('sizes', [])),
                    )
                )
            conn.commit()
    finally:
        conn.close()


# ── Row → dict helpers ────────────────────────────────────────────────────────

def _row_to_catalog_item(row):
    return {
        'id':          row['id'],
        'name':        row['name'],
        'price':       row['price'],
        'priceMin':    row['price_min'],
        'priceMax':    row['price_max'],
        'category':    row['category'],
        'description': row['description'],
        'image':       row['image'],
        'images':      json.loads(row['images'] or '[]'),
        'sizes':       json.loads(row['sizes']  or '[]'),
    }


def _row_to_ask_owner(row):
    return {
        'itemId':    row['item_id'],
        'name':      row['name'],
        'image':     row['image'],
        'timestamp': row['timestamp'],
    }


# ── Static file serving ───────────────────────────────────────────────────────

@catalogbaju_bp.route('')
def index_no_slash():
    # Redirect /catalogbaju → /catalogbaju/ so relative URLs resolve correctly
    return redirect('/catalogbaju/', 308)


@catalogbaju_bp.route('/')
def index():
    return send_from_directory(_STATIC_DIR, 'index.html')


@catalogbaju_bp.route('/js/<path:filename>')
def js_files(filename):
    return send_from_directory(_JS_DIR, filename)


@catalogbaju_bp.route('/<path:filename>')
def static_files(filename):
    real_path = os.path.realpath(os.path.join(_STATIC_DIR, filename))
    if not real_path.startswith(_STATIC_DIR + os.sep):
        abort(403)
    if not os.path.isfile(real_path):
        ext = os.path.splitext(filename)[1].lower()
        if ext in _IMAGE_EXTENSIONS:
            return Response(
                _PLACEHOLDER_SVG,
                mimetype='image/svg+xml',
                headers={'Cache-Control': 'public, max-age=3600'},
            )
    return send_from_directory(_STATIC_DIR, filename)


# ── API: Catalog ──────────────────────────────────────────────────────────────

@catalogbaju_bp.route('/api/catalog', methods=['GET'])
def get_catalog():
    conn = get_connection(_APP_NAME)
    try:
        rows = conn.execute(f'SELECT * FROM {_T_CATALOG} ORDER BY id').fetchall()
    finally:
        conn.close()
    return jsonify({'items': [_row_to_catalog_item(r) for r in rows]})


@catalogbaju_bp.route('/api/catalog', methods=['PUT', 'POST'])
def save_catalog():
    data  = request.get_json(silent=True) or {}
    items = data.get('items')
    if not isinstance(items, list):
        return jsonify({'error': 'Expected {"items": [...]}'}), 400
    conn = get_connection(_APP_NAME)
    try:
        conn.execute(f'DELETE FROM {_T_CATALOG}')
        for item in items:
            conn.execute(
                f"""INSERT INTO {_T_CATALOG}
                    (id, name, price, price_min, price_max, category, description, image, images, sizes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item.get('id'),
                    item.get('name', ''),
                    item.get('price', ''),
                    item.get('priceMin', ''),
                    item.get('priceMax', ''),
                    item.get('category', ''),
                    item.get('description', ''),
                    item.get('image', ''),
                    json.dumps(item.get('images', [])),
                    json.dumps(item.get('sizes', [])),
                )
            )
        conn.commit()
    finally:
        conn.close()
    return jsonify({'ok': True})


# ── API: Ask-owner ────────────────────────────────────────────────────────────

@catalogbaju_bp.route('/api/ask-owner', methods=['GET'])
def get_ask_owner():
    conn = get_connection(_APP_NAME)
    try:
        rows = conn.execute(f'SELECT * FROM {_T_ASK_OWNER} ORDER BY id').fetchall()
    finally:
        conn.close()
    return jsonify({'items': [_row_to_ask_owner(r) for r in rows]})


@catalogbaju_bp.route('/api/ask-owner', methods=['PUT', 'POST'])
def save_ask_owner():
    data  = request.get_json(silent=True) or {}
    items = data.get('items')
    if not isinstance(items, list):
        return jsonify({'error': 'Expected {"items": [...]}'}), 400
    conn = get_connection(_APP_NAME)
    try:
        conn.execute(f'DELETE FROM {_T_ASK_OWNER}')
        for item in items:
            conn.execute(
                f'INSERT INTO {_T_ASK_OWNER} (item_id, name, image, timestamp) VALUES (?, ?, ?, ?)',
                (item.get('itemId', ''), item.get('name', ''), item.get('image', ''), item.get('timestamp', ''))
            )
        conn.commit()
    finally:
        conn.close()
    return jsonify({'ok': True})


# ── API: Guest carts ──────────────────────────────────────────────────────────

@catalogbaju_bp.route('/api/guest-carts', methods=['GET'])
def get_guest_carts():
    conn = get_connection(_APP_NAME)
    try:
        rows = conn.execute(f'SELECT * FROM {_T_GUEST_CARTS}').fetchall()
    finally:
        conn.close()
    result = {
        row['guest_id']: {
            'cart':              json.loads(row['cart'] or '[]'),
            'submittedToOwner': bool(row['submitted_to_owner']),
        }
        for row in rows
    }
    return jsonify({'items': result})


@catalogbaju_bp.route('/api/guest-carts', methods=['PUT', 'POST'])
def save_guest_carts():
    data  = request.get_json(silent=True) or {}
    items = data.get('items')
    if not isinstance(items, dict):
        return jsonify({'error': 'Expected {"items": {...}}'}), 400
    conn = get_connection(_APP_NAME)
    try:
        conn.execute(f'DELETE FROM {_T_GUEST_CARTS}')
        for guest_id, guest_data in items.items():
            conn.execute(
                f'INSERT INTO {_T_GUEST_CARTS} (guest_id, cart, submitted_to_owner) VALUES (?, ?, ?)',
                (
                    guest_id,
                    json.dumps(guest_data.get('cart', [])),
                    1 if guest_data.get('submittedToOwner') else 0,
                )
            )
        conn.commit()
    finally:
        conn.close()
    return jsonify({'ok': True})
