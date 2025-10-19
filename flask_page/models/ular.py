#models/ular.py
from flask import jsonify
from ..utils.csv_helper import *
from ..utils.html_helper import *
import random
import string

ularconfcsv = "static/db/ular/ularconf.csv"
ularroomcsv = "static/db/ular/ularroom.csv"
ularplayerscsv = "static/db/ular/ularplayers.csv"

def modelgetcsvconf():
    data = af_getcsvdict(ularconfcsv)
    return data

def modelgetcsvroom():
    data = af_getcsvdict(ularroomcsv)
    return data

def modelgetcsvplayers(code=""):
    data = af_getcsvdict(ularplayerscsv)
    result = []
    for d in data:
        if d["code"] == code:
            result.append(d)
    return result

def modelgenerateroomcode(length=4):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))




def adddataroom(code="", turn="", state=""):
    af_addcsv(ularroomcsv, [
        code, turn, state
    ])

def adddataplayer(code="", player="", pos=0):
    af_addcsv(ularplayerscsv, [
        code, player, pos
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

def playeralreadyavailable(player="", code=""):
    data = modelgetcsvplayers(code)
    for d in data:
        if (d["player"] == player):
            return True
    
    return False