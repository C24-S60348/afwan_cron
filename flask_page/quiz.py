import random
from flask import jsonify, request, Blueprint, render_template, render_template_string
from datetime import datetime
import pandas as pd
from utils.allfunction import *
import os

quiz_blueprint = Blueprint('quiz', __name__)

@quiz_blueprint.route("/quiz", methods=["POST", "GET"])
def quiz_main():
    html = ""
    html += "viewer<br/><br/>"
    html += "<table>"
    data = af_getcsv("static/soalanDB.csv")
    for d in data:
        html += "<tr>"
        html += "<td>" + d[0] + "</td>"
        html += "<td>" + d[1] + "</td>"
        html += "<td>" + d[2] + "</td>"
        html += "<td>" + d[3] + "</td>"
        html += "<td>" + d[4] + "</td>"
        html += "<td>" + d[5] + "</td>"
        html += "<td>" + d[6] + "</td>"
        html += "<td>" + d[7] + "</td>"
        html += "<td>" + d[8] + "</td>"
        html += "<td>" + d[9] + "</td>"
        html += "<td>" + d[10] + "</td>"
        html += "<td>" + d[11] + "</td>"
        html += "<td>" + d[12] + "</td>"
        html += "<td>" + d[13] + "</td>"
        html += "<td>" + d[14] + "</td>"
        html += "<td>" + d[14] + "</td>"
        html += "<td>" + d[15] + "</td>"
        html += "<td>" + d[16] + "</td>"
        html += "<td>" + d[17] + "</td>"
        html += "<td>" + d[18] + "</td>"
        html += "</tr>"
    return af_template_html(html, "Quiz", "")

#   http://127.0.0.1:5001/api/quiz
#   {"name":"funderive"}
@quiz_blueprint.route("/api/quiz", methods=["GET", "POST"])
def quizapi():
    #return json of the selected name(game name)
    name = af_requestpostfromjson("name")
    dataraw = af_getcsvdict("static/soalanDB.csv")
    data = []
    #filter  = ""  value
    for dr in dataraw:
        if dr["name"] == name or name == "all":
            filtered = {k: v for k, v in dr.items() if v != ""}
            data.append(filtered)
    
    #kumpulkan
    data3 = []
    temp = "1"
    dk = []
    for d in data:
        level = d["level"]
        if temp != level:
            temp = level
            data3.append(dk)
            dk = []
            dk.append(d)
        else:
            dk.append(d)
    data3.append(dk)
    
    # shuffle
    data4 = []
    for d in data3:
        if len(d) > 1:
            #if shuffle, then shuffle
            random.shuffle(d)
        data4.append(d)

    result = jsonify({"data": data})
    return result

@quiz_blueprint.route("/api/quiz/construct", methods=["GET", "POST"])
def quizapiconstruct():
    try:
        if request.method == "POST":
            name = af_requestpostfromjson("name")
            file = af_requestpostfromjson("file", "testConstruct.csv")
        else:
            name = af_requestget("name")
            file = af_requestget("file")

        if not name:
            name = "all"
        if not file:
            file = "testConstruct.csv"

        dataraw = af_getcsvdict("static/" + file)
        data = []
        for dr in dataraw:
            filtered = {k: v for k, v in dr.items() if v != ""}
            data.append(filtered)

        return jsonify({"data": data})
    except Exception as e:
        # Log the error if you have logging set up, or print for debugging
        import traceback
        print("Error in quizapiconstruct:", e)
        traceback.print_exc()
        return jsonify({"result": "fail", "message": str(e)}), 500

@quiz_blueprint.route("/api/quiz/construct/synclatest", methods=["GET", "POST"])
def quizapiconstructsynclatest():
    import requests

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTgOUJLC-Q2Rp8cXBJOPI4TIwUia_hjziJBCn0NRg0QT6OleHnG7LGK7Vnz502Yoz2fM8s3xM5Qin6x/pub?gid=0&single=true&output=csv"

    try:
        r = requests.get(url)
        r.raise_for_status()
        csv_content = r.content.decode("utf-8")

        # Specify the file name you want to save to
        file_name = "testConstruct.csv"  # or "funderiveanim.csv"
        file_path = os.path.join("static", file_name)

        # Write the CSV content to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(csv_content)

        return jsonify({"result": "success", "message": f"Latest version fetched and saved to {file_name}"})
    except Exception as e:
        return jsonify({"result": "fail", "message": str(e)})

@quiz_blueprint.route("/quiz/handle")
def quiz_handle():
    return af_htmlhandletemplate("/quiz/download", "/quiz/upload", "", "soalanDB.csv", "/quiz")

@quiz_blueprint.route("/quiz/download")
def quiz_download():
    return af_downloadfile("static", "soalanDB.csv")

@quiz_blueprint.route("/quiz/upload", methods=["POST"])
def quiz_upload():
    return af_uploadfile("quiz.quiz_handle", "static", "soalanDB.csv", {'csv'})

  
#   http://127.0.0.1:5001/api/quiz/result/submit
#   data = ["ikan", "ayam"]
#   [namaapp, namauser, soalan, jawapan, jawapanbetul]

@quiz_blueprint.route("/api/quiz/result/submit", methods=["POST"])
def quizresultsubmit():
    data = af_requestpostfromjson("data")
    if data != "":
        af_addcsv("static/soalanDBresult.csv", data)
        return jsonify({"result": "success"})
    else:
        return jsonify({"result":"fail", "message":"no data submitted"})
    

#   "namaapp" = "afwan"
@quiz_blueprint.route("/api/quiz/result", methods=["POST"])
def quizresult():
    namaapp = af_requestpostfromjson("namaapp")
    if namaapp != "":
        data = af_getcsv("static/soalanDBresult.csv")
        data2 = []
        for d in data:
            if d[0] == namaapp:
                data2.append(d)
        return jsonify({"data": data2})
    else:
        return jsonify({"result":"fail", "message":"no namaapp submitted"})
   
    # data["data"]
    

@quiz_blueprint.route("/api/quiz/result/download", methods=["GET", "POST"])
def quizdownload():
    return af_downloadfile("static","soalanDBresult.csv")