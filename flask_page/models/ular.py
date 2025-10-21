#models/ular.py
from flask import jsonify
from ..utils.csv_helper import *
from ..utils.html_helper import *
import random
import string

confcsv = "static/db/ular/conf.csv"
roomcsv = "static/db/ular/room.csv"
playerscsv = "static/db/ular/players.csv"

def modelgetcsvconf():
    data = af_getcsvdict(confcsv)
    return data

def modelgetcsvroom():
    data = af_getcsvdict(roomcsv)
    return data

def modelgetcsvplayers(code=""):
    data = af_getcsvdict(playerscsv)
    result = []
    for d in data:
        if d["code"] == code:
            result.append(d)
    return result

def playerdata(code="", player=""):
    data = af_getcsvdict(playerscsv)
    result = []
    for d in data:
        if d["code"] == code and d["player"] == player:
            result.append(d)
    return result

def modelgenerateroomcode(length=4):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def startroom(code=""):
    new_data = {"state":"playing"}
    af_replacecsv2(roomcsv, "code", code, new_data)



def adddataroom(code="", turn="", state=""):
    af_addcsv(roomcsv, [
        code, turn, state
    ])

def adddataplayer(code="", player="", pos=0, color="white"):
    af_addcsv(playerscsv, [
        code, player, pos, color
    ])


def inputvalidated(input):
    if input == "" or input == None:
        return False
    return True

def inputnotvalidated(input=""):
    if input == "" or input == None:
        return True
    return False

def jsonifynotvalid(input=""):
    return jsonify({
        "status": "error",
        "message": f"{input} is not valid"
    })

def roomavailable(code=""):
    data = modelgetcsvroom()
    for d in data:
        if (d["code"] == code):
            return True
    
    return False

def roomstatus(code=""):
    data = modelgetcsvroom()
    for d in data:
        if (d["code"] == code):
            if (d["state"] == "waiting"):
                return "waiting"
            elif (d["state"] == "playing"):
                return "playing"
            else:
                return "finished"
    
    return "not exist"

def roomdata(code=""):
    data = modelgetcsvroom()
    for d in data:
        if (d["code"] == code):
            return {
                "state": d["state"],
                "turn": d["turn"]
            }
    
    return {
        "state": "room not exist",
        "turn": "room not exist"
    }

def rolldice(code="", player="", currentpos=0):
    dicenum = random.randint(1,6)
    newpos = currentpos + dicenum

    #changepos
    new_data = {"pos":newpos}
    af_replacecsvtwotarget(playerscsv, 
                           "player", player, "code", code, 
                           new_data)
    
    #turn
    players = modelgetcsvplayers(code)
    lengtharray = len(players)
    turn = ""
    pnum = 0
    for p in players:
        if p['player'] == player:
            if (pnum+1 > lengtharray-1):
                turn = players[0]['player'] 
            else:
                turn = players[pnum+1]['player'] 
        pnum += 1
    new_data = {"turn":turn}
    af_replacecsv2(roomcsv, "code", code, new_data)

    return {
        "player": player,
        "turn": turn,
        "beforepos": currentpos,
        "pos": newpos,
        "code": code
    }

def getsteps(before=0, after=3):
    results = []

    step = before
    for i in range(after-before):
        step += 1
        results.append(step)
        print(step)
    return results


def playeralreadyavailable(player="", code=""):
    data = modelgetcsvplayers(code)
    for d in data:
        if (d["player"] == player):
            return True
    
    return False