#controllers/ulardashboard.py
from flask import jsonify, request, Blueprint, render_template, render_template_string
from ..utils.html_helper import *
from ..models.ular import *

ulardashboard_bp = Blueprint('ulardashboard', __name__, url_prefix="/ulardashboard")

dbloc = "static/db/ular.db"
dbcolumn = "habit"

@ulardashboard_bp.route('/', methods=['GET', 'POST'])
def db_ui_web():
    endpoint = "ulardashboard"

    return render_template("dbviewer2.html", endpoint=endpoint)


@ulardashboard_bp.route('/query', methods=['GET', 'POST'])
def db_ui_query():

    # dbloc = getpostget("dbloc")
    query = getpostget("query")
    params = getpostget("parameter")
    # secretkey = "afwan"
    # if secretkey != "afwan":
    #     return jsonify({"error": "invalid secretkey"})
    
    dbdata = af_getdb(dbloc, query, params)
    return jsonify(dbdata)