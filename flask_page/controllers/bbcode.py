from flask import Blueprint, request, render_template_string, jsonify
import requests
from ..utils.html_helper import *
from ..utils.csv_helper import *
from ..utils.adminhandle_helper import *
from ..utils.data_helper import *
from ..utils.excel_helper import *
import bbcode

bbcode_bp = Blueprint("bbcode", __name__)
parser = bbcode.Parser()

#   http://127.0.0.1:5001/api/bbcode
#   {"text":"ikan [b]ayam[/b]"}
@bbcode_bp.route("/api/bbcode", methods=["GET", "POST"])
def apibbcode():
    text = af_requestpostfromjson("text")
    parsed = parser.format(text)

    return render_template_string(parsed)