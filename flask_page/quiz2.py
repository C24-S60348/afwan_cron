import random
from flask import jsonify, request, Blueprint, render_template, render_template_string
from datetime import datetime
import pandas as pd
from utils.allfunction import *

quiz2_blueprint = Blueprint('quiz2', __name__)

soalancsv = "static/soalanDB.csv"
resultcsv = "static/soalanDBresult.csv"


@quiz2_blueprint.route("/api/quiz2", methods=["GET"])
def apiquiz2():

    #name,level,type,soalan,soalan2,soalan3,soalan4,soalan5,pilihan1,pilihan2,pilihan3,pilihan4,pilihan5,pilihanjwpn1,pilihanjwpn2,pilihanjwpn3,pilihanjwpn4,pilihanjwpn5,answer,nota,createdat
    name = af_requestget("name")
    dataraw = af_getcsvdict(soalancsv) #todo - get from sheet
    data2 = {}
    
    for dr in dataraw:
        if name == dr["name"]:
            data2[dr["level"]] = []
    
    for dr in dataraw:
        if name == dr["name"]:
            filtered = {k: v for k, v in dr.items() if v != ""}
            data2[dr["level"]].append(filtered)
    

    result = jsonify(data2)
    return result

@quiz2_blueprint.route("/api/quiz2/result/submit", methods=["POST"])
def apiquiz2resultsubmit():
    #nama,namauser,soalan,jawapan,jawapanbetul,createdat
    data = af_requestpostfromjson("data")

    if data != "":
        af_addcsv(resultcsv, data)
        #add into queue - to sheet
        return jsonify({"result": "success"})
    else:
        return jsonify({"result":"fail", "message":"no data submitted"})

@quiz2_blueprint.route("/api/quiz2/result", methods=["GET"])
def apiquiz2result():
    html = ""
    name = af_requestget("name")
    if name != "":
        data = af_getcsv(resultcsv)
        data2 = []
        html += """
                <style>
                table tr td {
                    border: 1px solid black;
                    padding: 3px;
                }
                </style>"""
        html += "<table>"
        count = 0
        for d in data:
            if name == d[0] or count == 0:
                html += "<tr>"
                html += f"<td>{d[0]}</td>"
                html += f"<td>{d[1]}</td>"
                html += f"<td>{d[2]}</td>"
                html += f"<td>{d[3]}</td>"
                html += f"<td>{d[4]}</td>"
                html += f"<td>{d[5]}</td>"
                html += "</tr>"
            count += 1

        html += "</table>"
        return render_template_string(html)
    else:
        return jsonify({"result":"fail", "message":"no name submitted"})
   
@quiz2_blueprint.route("/api/quiz2/result2", methods=["GET"])
def apiquiz2result2():
    name = af_requestget("name")
    if name != "":
        data = af_getcsvdict(resultcsv)
        data2 = []
        for d in data:
            if name == d["name"]:
                data2.append(d)
        return jsonify({"data": data2})
    else:
        return jsonify({"result":"fail", "message":"no name submitted"})