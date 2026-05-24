"""
flask_page/modules/catalogbaju/catalogbaju.py
Catalog Baju Blueprint — integrated into afwanhaziq.my

Routes:
  GET  /catalogbaju/                  → catalog viewer single-page app
  GET  /catalogbaju/<filename>        → static assets (styles.css, mybaju.png, appsettings.json, …)
  GET  /catalogbaju/js/<path>         → JavaScript ES-module files
  GET  /catalogbaju/api/catalog       → catalog items JSON
  PUT  /catalogbaju/api/catalog       → save catalog items
  GET  /catalogbaju/api/ask-owner     → ask-owner requests JSON
  PUT  /catalogbaju/api/ask-owner     → save ask-owner requests
  GET  /catalogbaju/api/guest-carts   → guest carts JSON
  PUT  /catalogbaju/api/guest-carts   → save guest carts

Data is persisted as JSON files inside flask_page/modules/catalogbaju/data/.
"""
import os
import json
from flask import Blueprint, request, jsonify, send_from_directory

catalogbaju_bp = Blueprint('catalogbaju', __name__, url_prefix='/catalogbaju')

_MODULE_DIR = os.path.dirname(__file__)
_STATIC_DIR = os.path.join(_MODULE_DIR, 'static')
_JS_DIR     = os.path.join(_MODULE_DIR, 'static', 'js')
_DATA_DIR   = os.path.join(_MODULE_DIR, 'data')

_CATALOG_FILE    = os.path.join(_DATA_DIR, 'catalog_items.json')
_ASK_OWNER_FILE  = os.path.join(_DATA_DIR, 'ask_owner_requests.json')
_GUEST_CARTS_FILE = os.path.join(_DATA_DIR, 'guest_carts.json')


# ── Helpers ────────────────────────────────────────────────────────────────

def _ensure_data_dir():
    os.makedirs(_DATA_DIR, exist_ok=True)


def _read_json(path, fallback):
    try:
        if not os.path.exists(path):
            return fallback
        with open(path, 'r', encoding='utf-8') as f:
            raw = f.read().strip()
        if not raw:
            return fallback
        return json.loads(raw)
    except Exception:
        return fallback


def _write_json(path, data):
    _ensure_data_dir()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_default_catalog():
    """Read default catalog items from the bundled appsettings.json."""
    appsettings_path = os.path.join(_STATIC_DIR, 'appsettings.json')
    try:
        with open(appsettings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        items = data.get('catalog', {}).get('items', [])
        return items if isinstance(items, list) else []
    except Exception:
        return []


def _seed_catalog_if_empty():
    """Auto-seed catalog from appsettings.json on first visit."""
    existing = _read_json(_CATALOG_FILE, [])
    if existing:
        return
    defaults = _load_default_catalog()
    if defaults:
        _write_json(_CATALOG_FILE, defaults)


# ── Static file serving ────────────────────────────────────────────────────

@catalogbaju_bp.route('/')
@catalogbaju_bp.route('')
def index():
    _seed_catalog_if_empty()
    return send_from_directory(_STATIC_DIR, 'index.html')


@catalogbaju_bp.route('/js/<path:filename>')
def js_files(filename):
    """Serve ES-module JS files from static/js/."""
    return send_from_directory(_JS_DIR, filename)


@catalogbaju_bp.route('/<path:filename>')
def static_files(filename):
    """Serve any other static asset (CSS, images, JSON…)."""
    return send_from_directory(_STATIC_DIR, filename)


# ── API: Catalog ───────────────────────────────────────────────────────────

@catalogbaju_bp.route('/api/catalog', methods=['GET'])
def get_catalog():
    items = _read_json(_CATALOG_FILE, [])
    return jsonify({'items': items})


@catalogbaju_bp.route('/api/catalog', methods=['PUT', 'POST'])
def save_catalog():
    data = request.get_json(silent=True) or {}
    items = data.get('items')
    if not isinstance(items, list):
        return jsonify({'error': 'Expected JSON body: {"items": [...]}'}), 400
    _write_json(_CATALOG_FILE, items)
    return jsonify({'ok': True})


# ── API: Ask-owner ─────────────────────────────────────────────────────────

@catalogbaju_bp.route('/api/ask-owner', methods=['GET'])
def get_ask_owner():
    items = _read_json(_ASK_OWNER_FILE, [])
    return jsonify({'items': items})


@catalogbaju_bp.route('/api/ask-owner', methods=['PUT', 'POST'])
def save_ask_owner():
    data = request.get_json(silent=True) or {}
    items = data.get('items')
    if not isinstance(items, list):
        return jsonify({'error': 'Expected JSON body: {"items": [...]}'}), 400
    _write_json(_ASK_OWNER_FILE, items)
    return jsonify({'ok': True})


# ── API: Guest carts ───────────────────────────────────────────────────────

@catalogbaju_bp.route('/api/guest-carts', methods=['GET'])
def get_guest_carts():
    items = _read_json(_GUEST_CARTS_FILE, {})
    return jsonify({'items': items})


@catalogbaju_bp.route('/api/guest-carts', methods=['PUT', 'POST'])
def save_guest_carts():
    data = request.get_json(silent=True) or {}
    items = data.get('items')
    if not isinstance(items, dict):
        return jsonify({'error': 'Expected JSON body: {"items": {...}}'}), 400
    _write_json(_GUEST_CARTS_FILE, items)
    return jsonify({'ok': True})
