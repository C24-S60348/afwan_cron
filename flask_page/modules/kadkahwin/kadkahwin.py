"""
flask_page/modules/kadkahwin/kadkahwin.py
Kad Kahwin Designer Blueprint — integrated into afwanhaziq.my
Route:
  GET /kadkahwin/  → Wedding card designer single-page app
"""
import os
from flask import Blueprint, send_from_directory

kadkahwin_bp = Blueprint('kadkahwin', __name__, url_prefix='/kadkahwin')

_STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')


@kadkahwin_bp.route('/')
@kadkahwin_bp.route('')
def index():
    return send_from_directory(_STATIC_DIR, 'index.html')
