#apps/controllers/tanam.py
import random
from flask import jsonify, request, Blueprint, render_template, render_template_string
from datetime import datetime
import pandas as pd
from ..utils.adminhandle_helper import *
from ..utils.html_helper import *
from ..utils.excel_helper import *
from ..utils.checker_helper import *
from ..utils.csv_helper import *
from ..models.tanam import *

tanam_blueprint = Blueprint('tanam', __name__)

@tanam_blueprint.route("/tanam")
def tanam():
    return render_template("tanam/landing.html", title="Tanam-Tanam 🌱")

@tanam_blueprint.route("/tanam_pilih")
def tanam_pilih():
    plants = gettanamcsv()
    for p in plants:
        name = p.get("name", "")
        if "(" in name and ")" in name:
            parts = name.split("(", 1)
            p["primary_name"] = parts[0].strip()
            p["sub_name"] = "(" + parts[1].strip()
        else:
            p["primary_name"] = name
            p["sub_name"] = ""
            
    return render_template("tanam/pilih.html", title="Tanam-Tanam 🌱", plants=plants)

@tanam_blueprint.route("/tanam_add")
def tanam_add():
    html = ""
    html += "<div class='selectorDIV'>"
    html += af_htmlformstart("tanam_add/submit")
    html += af_htmltextinput("Tanam", "tanamtext", "Choose tanam")
    options = ""
    options += af_htmlselectoptionempty()
    options += af_htmlselectoption("carrot", "Carrot Name")
    options += af_htmlselectoption("tomato", "tomate Name")
    options += af_htmlselectoption("ayam", "ayam Name")

    html += af_htmlselect("tanamid", "Tanams", options)
    html += af_htmlformsubmitbutton()
    html += af_htmlformend()
    html += "</div>"

    return render_template("tanam/main.html", title="Tanam add", html=html)

@tanam_blueprint.route("/tanam_add/submit", methods=['POST'])
def tanam_add_submit():
    html = ""
    html += af_requestpost("tanamid")
    html += "<br/><br/>"
    html += af_requestpost("tanamtext")
    
    file_path = 'tanam.csv'
    new_row = [
        af_requestpost("tanamtext"),
        af_requestpost("tanamtext"),
        af_requestpost("tanamtext"),
        af_requestpost("tanamtext"),
        af_requestpost("tanamtext"),
        af_requestpost("tanamtext"),
        af_requestpost("tanamtext"),
        af_requestpost("tanamtext"),
        af_requestpost("tanamtext"),
        ]
    af_addcsv(file_path, new_row)
    html += "<br/><br/>"
    html += "<a href='/tanam'>back</a>"

    return render_template("tanam/main.html", title="Tanam add", html=html)

@tanam_blueprint.route("/tanam_desc")
def tanam_desc():
    pokok = af_requestget("pokok")

    html = ""
    html += af_htmltitle("Desc")
    html += modeldesc(pokok)
    html += "<div style='text-align:center;'>"
    html += af_htmlbuttonlink("Mula tanam", "primary", "/tanam_mula?pokok="+pokok)
    html += "</div>"

    return render_template("tanam/main.html", title="Tanam desc", html=html)


@tanam_blueprint.route("/tanam_mula")
def tanam_mula():
    pokok = af_requestget("pokok")

    html = ""
    html += af_htmltitle("Gameplay")
    html += modelmula(pokok)

    return render_template("tanam/mula.html", title="Tanam desc", html=html)