#controllers/ular.py
from flask import jsonify, request, Blueprint, render_template, render_template_string
from ..utils.html_helper import *
from ..utils.csv_helper import *
from ..models.ular import *

ular_blueprint = Blueprint('ular', __name__)

@ular_blueprint.route("/ular")
def ular():
    html = "afwan"
    return render_template("ular/main.html", html=html)

@ular_blueprint.route("/ular/game")
def ular_game():
    html = "afwan"
    return render_template("ular/game.html", html=html, title="Snakey")

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
    color = af_requestget("color")

    if inputnotvalidated(player):
        return jsonifynotvalid("player")
    if inputnotvalidated(color):
        return jsonifynotvalid("color")
    
    state = "waiting"
    pos = 0

    adddataroom(code, player, state)
    adddataplayer(code, player, pos, color)

    return jsonify({
        "status": "ok",
        "code": code,
        "player": player,
        "color": color,
        "state": state,
        "pos": pos,
        "message": f"Game {code} created!"
    })

@ular_blueprint.route("/api/ular/joinroom")
def apiular_joinroom():
    code = af_requestget("code")
    player = af_requestget("player")
    color = af_requestget("color")
    
    if inputnotvalidated(code):
        return jsonifynotvalid("code")
    if inputnotvalidated(player):
        return jsonifynotvalid("player")
    if inputnotvalidated(color):
        return jsonifynotvalid("color")
    
    rstatus = roomstatus(code)

    if rstatus == "waiting":

        if playeralreadyavailable(player, code) == False:
            pos = 0
            adddataplayer(code, player, pos, color)
        else:
            return jsonify({
                "status": "ok",
                "message": f"player {player} is already available",
                "code": code,
                "player": player
                # "players": modelgetcsvplayers(code)
            })
        
        return jsonify({
            "status": "ok",
            "code": code,
            "player": player,
            # "players": modelgetcsvplayers(code),
            "message": f"Joined {code} successfully!"
            # "state": rstatus
        })
    elif rstatus == "playing":
        players = modelgetcsvplayers(code)
        playerexistingame = False
        for p in players:
            if p["player"] == player:
                playerexistingame = True
        
        #player yang lain dan status is not offline (masuk balik)
        if playerexistingame:
            return jsonify({
                "status": "ok",
                "message": f"Rejoin",
                "state": rstatus,
                "code": code,
                "player": player
            })
        else:
            #if joinroom was the existing player, rejoin
            return jsonify({
                "status": "ok",
                "message": f"The room already started, do you want to spectate instead?",
                "state": rstatus,
                "code": code,
                "player": player
            })
    elif rstatus == "ended":
        return jsonify({
            "status": "ok",
            "message": f"The room already ended!",
            "state": rstatus,
            "code": code,
            "player": player
        })
    else:
        return jsonify({
            "status": "error",
            "message": "room is not available"
        })
    

@ular_blueprint.route("/api/ular/startgame")
def apiular_startgame():
    code = af_requestget("code")
    questions_per_game = af_requestget("questions_per_game")
    difficulty = af_requestget("difficulty")
    
    if inputnotvalidated(code):
        return jsonifynotvalid("code")
    
    rstatus = roomstatus(code)

    if rstatus == "waiting":

        startroom(code)
        
        return jsonify({
            "status": "ok",
            "code": code,
            "players": modelgetcsvplayers(code),
            "message": f"Room {code} started!",
            "state": "playing"
        })
    elif rstatus == "playing" or rstatus == "ended":
        return jsonify({
            "status": "error",
            "message": "room already started"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "room is not available"
        })
    
@ular_blueprint.route("/api/ular/spectate")
def apiular_spectate():
    code = af_requestget("code")
    player = af_requestget("player")
    
    if inputnotvalidated(code):
        return jsonifynotvalid("code")
    if inputnotvalidated(player):
        return jsonifynotvalid("player")
    
    rstatus = roomstatus(code)

    if rstatus == "waiting" or rstatus == "playing":
        return jsonify({
            "status": "ok",
            "code": code,
            "players": modelgetcsvplayers(code),
            "message": f"Spectating",
            "state": rstatus
        })
    else:
        return jsonify({
            "status": "error",
            "message": "room is not available or already ended!"
        })
    
@ular_blueprint.route("/api/ular/state")
def apiular_state():
    code = af_requestget("code")
    
    if inputnotvalidated(code):
        return jsonifynotvalid("code")
    
    rdata = roomdata(code)
    rstate = rdata["state"]
    rturn = rdata["turn"]
    rquestionid = rdata["questionid"]
    question = []
    if rquestionid != "":
        question = getquestion(rquestionid)
    

    if rstate == "waiting" or rstate == "playing" or rstate == "ended":

        if rstate == "waiting":
            message = f"Waiting players..."
        elif rstate == "ended":
            message = f"The game already ended"
        else:
            if question == []:
                message = f"{rturn}'s turn"
            else:
                message = f"{rturn}'s turn, Please answer question"

        return jsonify({
            "status": "ok",
            "code": code,
            "players": modelgetcsvplayers(code),
            "message": message,
            "turn": rturn,
            "question": question,
            "questionid": rquestionid,
            "state": rstate
        })
    else:
        return jsonify({
            "status": "error",
            "message": "room is not available!"
        })
    
@ular_blueprint.route("/api/ular/rolldice")
def apiular_rolldice():
    code = af_requestget("code")
    player = af_requestget("player")
    
    if inputnotvalidated(code):
        return jsonifynotvalid("code")
    if inputnotvalidated(player):
        return jsonifynotvalid("player")
    
    rdata = roomdata(code)
    rstate = rdata["state"]
    rturn = rdata["turn"]
    rquestionid = rdata["questionid"]

    pdata = playerdata(code, player)
    if pdata == []:
        return jsonify({
            "status": "error",
            "message": f"Please insert correct player"
        })
    ppos = pdata[0]["pos"]
    ppos = int(ppos)

    if rquestionid != "":
        #tengah menjawab soalan
        return jsonify({
            "status": "error",
            "message": f"Please answer question first!"
        })
    
    else:

        if rstate == "playing":

            if rturn == player:
                rdice = rolldice(code, player, ppos)
                rdata = roomdata(code)
                rstate = rdata["state"]
                rturn = rdata["turn"]

                ended = checkgameended(rdice["pos"], code)

                if ended == True:
                    message = f"The game already ended"

                else:
                    if rdice["question"] == []:
                        message = f"Roll dice: {rdice["dice"]}, Turn now: {rdice["turn"]}"
                    else:
                        message = f"Roll dice: {rdice["dice"]}, Turn now: {rdice["turn"]}, Please answer question"

                return jsonify({
                    "status": "ok",
                    "code": code,
                    "beforepos": rdice["beforepos"],
                    "pos": rdice["pos"],
                    "players": modelgetcsvplayers(code),
                    "message": message,
                    "turn": rdice["turn"],
                    "question": rdice["question"],
                    "questionid": rdice["questionid"],
                    "state": rstate,
                    "steps": getstepsdice(int(rdice["beforepos"]), int(rdice["dice"])),
                    "dice": rdice["dice"],
                    "ended": ended
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": f"It is not your turn!"
                })
        elif rstate == "waiting":
            return jsonify({
                "status": "error",
                "message": "room is not started yet!"
            })
        elif rstate == "ended":
            return jsonify({
                "status": "error",
                "message": "room is already ended!"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "room is not available!"
            })

    
@ular_blueprint.route("/api/ular/steps")
def apiular_teststeps():
    before = int(af_requestget("before"))
    dice = int(af_requestget("dice"))

    return getstepsdice(before, dice)

@ular_blueprint.route("/api/ular/endgame")
def apiular_endgame():
    code = af_requestget("code")

    endgame(code)

    return jsonify({
        "status":"ok",
        "message": f"game {code} ended" 
    })