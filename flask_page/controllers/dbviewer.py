#controllers/dbviewer.py
from ..utils.db_helper import *
from ..utils.html_helper import *
from flask import abort, jsonify, request, Blueprint, render_template, render_template_string, session

dbviewer_bp = Blueprint('dbviewer', __name__, url_prefix="/dbviewer")

@dbviewer_bp.route('/', methods=['GET', 'POST'])
def db_ui_web():
    
    dbloc = "static/db/habit/mydb.db" #default
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    params = ()
    tables = af_getdb(dbloc, query, params)
    # print (tables)

    return render_template("db_ui_helper.html", tables=tables)


@dbviewer_bp.route('/query', methods=['GET', 'POST'])
def db_ui_query():

    dbloc = getpostget("dbloc")
    query = getpostget("query")
    params = getpostget("parameter")
    secretkey = getpostget("secretkey")
    if secretkey != "afwan":
        return jsonify({"error": "invalid secretkey"})
    
    dbdata = af_getdb(dbloc, query, params)
    return jsonify(dbdata)