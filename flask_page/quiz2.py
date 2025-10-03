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
    import requests
    import csv
    from io import StringIO

    #name,level,type,soalan,soalan2,soalan3,soalan4,soalan5,pilihan1,pilihan2,pilihan3,pilihan4,pilihan5,pilihanjwpn1,pilihanjwpn2,pilihanjwpn3,pilihanjwpn4,pilihanjwpn5,answer,nota,createdat
    name = af_requestget("name")
    file = af_requestget("file")

    if name == "":
        return jsonify({"result":"fail", "message":"no name submitted - funderive"})
    if file == "":
        return jsonify({"result":"fail", "message":"no file submitted - csvanim or csvsoalan"})

    if file == "csvanim":
        url = af_afwangetdb("csvanim")
    elif file == "csvsoalan":
        url = af_afwangetdb("csvsoalan")

    try:
        r = requests.get(url)
        r.raise_for_status()
        csv_content = r.content.decode("utf-8")

        data = []
        reader = csv.DictReader(StringIO(csv_content))
        # return jsonify({"data": list(reader)})
        data2 = {}
        
        for dr in reader:
            if name == dr["name"]:
                filtered = {k: v for k, v in dr.items() if v != "" and k not in ["name", "level"]}
                if dr["level"] not in data2:
                    data2[dr["level"]] = []
                data2[dr["level"]].append(filtered)

        return jsonify(data2)

    except Exception as e:
        return jsonify({"result": "fail", "message": "'str' object has no attribute 'items'", "error": str(e)}), 500


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
                html += f"<td>{d[6]}</td>"
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