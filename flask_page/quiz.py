import random
from flask import jsonify, request, Blueprint, render_template, render_template_string
from datetime import datetime
import pandas as pd
from utils.allfunction import *

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

    result = jsonify(data)
    return result

@quiz_blueprint.route("/api/quiz/construct", methods=["GET", "POST"])
def quizapiconstruct():
    #return json of the selected name(game name)
    requestpost = request.json
    return jsonify("aaa")
    return requestpost.get("ayam")
    name = af_requestpostfromjson("name")
    file = af_requestpostfromjson("file","testConstruct.csv")
    return "file: " + file
    dataraw = af_getcsvdict("static/" + file)
    data = []
    #filter  = ""  value
    for dr in dataraw:
        if dr["group"] == name or name == "all":
            filtered = {k: v for k, v in dr.items() if v != ""}
            data.append(filtered)

    result = jsonify(data)
    return result

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