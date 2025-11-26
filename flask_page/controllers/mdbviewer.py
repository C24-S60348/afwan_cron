#controllers/mdbviewer.py
from ..utils.mdb_helper import *
from ..utils.html_helper import *
from flask import abort, jsonify, request, Blueprint, render_template, render_template_string, session

mdbviewer_bp = Blueprint('mdbviewer', __name__, url_prefix="/mdbviewer")

@mdbviewer_bp.route('/', methods=['GET', 'POST'])
def db_ui_web():
    
    dbloc = "static/db/flangelist2003.mdb" #default
    tables = af_gettablemdb(dbloc)

    

    return render_template("mdb_ui_helper.html", tables=tables)

@mdbviewer_bp.route('/gettable', methods=['GET', 'POST'])
def db_ui_gettable():

    dbloc = getpostget("dbloc")
    tables = af_gettablemdb(dbloc)
    
    return jsonify(tables)

@mdbviewer_bp.route('/query', methods=['GET', 'POST'])
def db_ui_query():

    dbloc = getpostget("dbloc")
    query = getpostget("query")
    params = getpostget("parameter")
    secretkey = getpostget("secretkey")
    if secretkey != "afwan":
        return jsonify({"error": "invalid secretkey"})
    
    dbdata = af_getmdb(dbloc, query, params)
    return jsonify(dbdata)