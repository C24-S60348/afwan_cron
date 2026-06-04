import os
import json
from flask import Blueprint, request, jsonify, send_from_directory, Response, abort, redirect

catalogbaju_bp = Blueprint('catalogbaju', __name__, url_prefix='/catalogbaju')

_MODULE_DIR  = os.path.dirname(__file__)
_STATIC_DIR  = os.path.realpath(os.path.join(_MODULE_DIR, 'static'))
_JS_DIR      = os.path.join(_STATIC_DIR, 'js')
_DATA_DIR    = os.path.join(_MODULE_DIR, 'data')

_CATALOG_FILE     = os.path.join(_DATA_DIR, 'catalog_items.json')
_ASK_OWNER_FILE   = os.path.join(_DATA_DIR, 'ask_owner_requests.json')
_GUEST_CARTS_FILE = os.path.join(_DATA_DIR, 'guest_carts.json')

_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.avif'}

_PLACEHOLDER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
  <rect width="300" height="300" rx="14" fill="#0f172a"/>
  <path d="M95,95 L45,130 L70,145 L70,235 L230,235 L230,145 L255,130 L205,95 Q175,110 150,125 Q125,110 95,95 Z"
        fill="#1e293b" stroke="#334155" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M125,110 Q150,125 175,110" fill="none" stroke="#475569" stroke-width="2" stroke-linecap="round"/>
  <text x="150" y="268" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif"
        font-size="13" fill="#475569">No image</text>
</svg>"""


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
    appsettings_path = os.path.join(_STATIC_DIR, 'appsettings.json')
    try:
        with open(appsettings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        items = data.get('catalog', {}).get('items', [])
        return items if isinstance(items, list) else []
    except Exception:
        return []


def _seed_catalog_if_empty():
    if not _read_json(_CATALOG_FILE, []):
        defaults = _load_default_catalog()
        if defaults:
            _write_json(_CATALOG_FILE, defaults)


# ── Static file serving ───────────────────────────────────────────────

@catalogbaju_bp.route('')
def index_no_slash():
    # Redirect /catalogbaju → /catalogbaju/ so relative URLs (CSS, JS, API) work correctly
    return redirect('/catalogbaju/', 308)


@catalogbaju_bp.route('/')
def index():
    _seed_catalog_if_empty()
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


# ── API: Catalog ──────────────────────────────────────────────────────

@catalogbaju_bp.route('/api/catalog', methods=['GET'])
def get_catalog():
    return jsonify({'items': _read_json(_CATALOG_FILE, [])})


@catalogbaju_bp.route('/api/catalog', methods=['PUT', 'POST'])
def save_catalog():
    data = request.get_json(silent=True) or {}
    items = data.get('items')
    if not isinstance(items, list):
        return jsonify({'error': 'Expected JSON body: {"items": [...]}'}), 400
    _write_json(_CATALOG_FILE, items)
    return jsonify({'ok': True})


# ── API: Ask-owner ────────────────────────────────────────────────────

@catalogbaju_bp.route('/api/ask-owner', methods=['GET'])
def get_ask_owner():
    return jsonify({'items': _read_json(_ASK_OWNER_FILE, [])})


@catalogbaju_bp.route('/api/ask-owner', methods=['PUT', 'POST'])
def save_ask_owner():
    data = request.get_json(silent=True) or {}
    items = data.get('items')
    if not isinstance(items, list):
        return jsonify({'error': 'Expected JSON body: {"items": [...]}'}), 400
    _write_json(_ASK_OWNER_FILE, items)
    return jsonify({'ok': True})


# ── API: Guest carts ──────────────────────────────────────────────────

@catalogbaju_bp.route('/api/guest-carts', methods=['GET'])
def get_guest_carts():
    return jsonify({'items': _read_json(_GUEST_CARTS_FILE, {})})


@catalogbaju_bp.route('/api/guest-carts', methods=['PUT', 'POST'])
def save_guest_carts():
    data = request.get_json(silent=True) or {}
    items = data.get('items')
    if not isinstance(items, dict):
        return jsonify({'error': 'Expected JSON body: {"items": {...}}'}), 400
    _write_json(_GUEST_CARTS_FILE, items)
    return jsonify({'ok': True})
