#controllers/ular.py
from flask import jsonify, request, Blueprint, render_template, render_template_string
from ..utils.html_helper import *
from ..utils.csv_helper import *
from ..models.ular import *

ular_blueprint = Blueprint('ular', __name__)

@ular_blueprint.route("/ular")
def ular():
    html = "afwan"
    return render_template("main.html", html=html)

@ular_blueprint.route("/api/ular")
def apiular():
    return jsonify({"ikan":"ayam"})
    return render_template("main.html", html=html)

@ular_blueprint.route("/api/ular/getconfig")
def apiular_getconfig():
    return jsonify(modelgetcsvconf())

@ular_blueprint.route("/api/ular/createroom")
def apiular_createroom():
    code = modelgenerateroomcode(4)
    player = af_requestget("player")

    if inputnotvalidated(player):
        return jsonifynotvalid(player)
    
    state = "waiting"
    pos = 0

    adddataroom(code, player, state)
    adddataplayer(code, player, pos)

    return jsonify({
        "status": "ok",
        "code": code,
        "player": player,
        "state": state,
        "pos": pos
        })

@ular_blueprint.route("/api/ular/joinroom")
def apiular_joinroom():
    code = af_requestget("code")
    player = af_requestget("player")
    
    if inputnotvalidated(code):
        return jsonifynotvalid("code")
    
    if inputnotvalidated(player):
        return jsonifynotvalid("player")

    if roomavailable(code):

        if playeralreadyavailable(player, code) == False:
            pos = 0
            adddataplayer(code, player, pos)
        
        return jsonify({
            "status": "ok",
            "code": code,
            "player": player,
            "players": modelgetcsvplayers(code)
        })
    else:
        return jsonify({
            "status": "error",
            "message": "room is not available"
        })