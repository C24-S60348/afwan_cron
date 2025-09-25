from flask import Blueprint, request, render_template_string, jsonify
import requests
from utils.allfunction import *
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