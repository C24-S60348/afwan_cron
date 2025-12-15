#models/ular.py
from flask import jsonify
# from ..utils.csv_helper import *
from ..utils.html_helper import *
from ..utils.db_helper import *
import random
import string

confcsv = "static/db/ular/conf.csv"
roomcsv = "static/db/ular/room.csv"
playerscsv = "static/db/ular/players.csv"
dbloc = "static/db/ular.db"
maxbox = 28

def modelgetcsvconf():
    query = "SELECT * FROM conf;"
    params = ()
    data = af_getdb(dbloc,query,params)
    # data = af_getcsvdict(confcsv)
    return data

def modelgetcsvroom():
    query = "SELECT * FROM room;"
    params = ()
    data = af_getdb(dbloc,query,params)
    # data = af_getcsvdict(roomcsv)
    return data

def modelgetcsvplayers(code=""):
    query = "SELECT * FROM players;"
    params = ()
    data = af_getdb(dbloc,query,params)
    # data = af_getcsvdict(playerscsv)
    result = []
    for d in data:
        if d["code"] == code:
            result.append(d)
    return result

def playerdata(code="", player=""):
    query = "SELECT * FROM players;"
    params = ()
    data = af_getdb(dbloc,query,params)
    # data = af_getcsvdict(playerscsv)
    result = []
    for d in data:
        if d["code"] == code and d["player"] == player:
            result.append(d)
    return result

def modelgenerateroomcode(length=4):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def startroom(code=""):
    # new_data = {"state":"playing"}
    query = "UPDATE room SET state = ? WHERE code = ?;"
    params = ("playing", code,)
    data = af_getdb(dbloc,query,params)
    # af_replacecsv2(roomcsv, "code", code, new_data)



def adddataroom(code="", turn="", state="", maxbox=maxbox, topic="biologi"):
    query = "INSERT INTO room (code,turn,state,questionid,maxbox,topic) VALUES (?,?,?,?,?,?);"
    params = (code, turn, state, "", maxbox, topic)
    data = af_getdb(dbloc,query,params)
    # af_addcsv(roomcsv, [
    #     code, turn, state, "", maxbox, topic
    # ])

def adddataplayer(code="", player="", pos=0, color="white"):
    query = "INSERT INTO players (code,player,pos,color,questionright,questionget) VALUES (?,?,?,?,?,?);"
    params = (code, player, pos, color, "", "")
    data = af_getdb(dbloc,query,params)
    # af_addcsv(playerscsv, [
    #     code, player, pos, color, "", ""
    # ])


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
    maxbox = 0
    data = modelgetcsvroom()
    for d in data:
        maxbox = d["maxbox"]
        if maxbox == "" or maxbox == None:
            maxbox = 0
        else:
            maxbox = int(maxbox)

        if (d["code"] == code):
            return d
    
    return {
        "state": "",
        "turn": "",
        "questionid": "",
        "maxbox": maxbox,
        "topic": ""
    }

def modelnextturn(code="", currentplayer=""):
    players = modelgetcsvplayers(code)
    lengtharray = len(players)
    turn = ""
    pnum = 0
    for p in players:
        if p['player'] == currentplayer:
            if (pnum+1 > lengtharray-1):
                turn = players[0]['player'] 
            else:
                turn = players[pnum+1]['player'] 
        pnum += 1
    query = "UPDATE room SET turn = ? WHERE code = ?;"
    params = (turn, code,)
    data = af_getdb(dbloc,query,params)
    # new_data = {"turn":turn}
    # af_replacecsv2(roomcsv, "code", code, new_data)
    return turn

def playerchangepos(code="", player="", newpos=""):
    query = "UPDATE players SET pos = ? WHERE code = ? AND player = ?;"
    params = (newpos, code, player,)
    data = af_getdb(dbloc,query,params)
    # new_data = {"pos":newpos}
    # af_replacecsvtwotarget(playerscsv, 
    #                        "player", player, "code", code, 
    #                        new_data)


def checkgameended(pos="", code="", maxbox=maxbox):
    ended = False
    if pos == str(maxbox) or pos == maxbox:
        endgame(code)
        ended = True
    
    return ended

def rolldice(code="", player="", currentpos=0, maxbox=maxbox):
    dicenum = random.randint(1,6)
    turn = player
    newpos = currentpos + dicenum
    questionid = ""
    if newpos > maxbox:
        newpos = maxbox - (newpos - maxbox)

    #changepos
    playerchangepos(code, player, newpos)
    
    #if has question, get question
    qqid = gquestion(newpos, code)
    question = qqid["question"]
    questionid = qqid["questionid"]

    if question == []:
        turn = modelnextturn(code, player)

    return {
        "player": player,
        "turn": turn,
        "beforepos": currentpos,
        "pos": newpos,
        "code": code,
        "dice": dicenum,
        "question": question,
        "questionid": questionid
    }

def gquestion(newpos="", code=""):
    #endpos = getendbystartladdersnake(newpos)
    rdata = roomdata(code)
    topic = rdata["topic"]
    if getendbystartladdersnake(newpos) == 0:
        question = []
        questionid = ""
    else:
        question = getrandomquestiontopic(topic)
        questionid = question[0]["id"]
    
    query = "UPDATE room SET questionid = ? WHERE code = ?;"
    params = (questionid, code,)
    data = af_getdb(dbloc,query,params)

    # new_data = {
    #     "questionid": questionid
    # }
    # #room's questionid => number
    # af_replacecsv2(roomcsv, "code", code, new_data)

    return {
        "question": question,
        "questionid": questionid
    }

def getsteps(before=0, after=3):
    results = []

    move = "forward"
    step = before
    hasreached = False

    for i in range(0,6):
        if step < after:
            step += 1
       
        if step != after:
            results.append(step)
        else:
            if hasreached == False:
                hasreached = True
                results.append(step)


    return results

def getstepsdice(before=0, dice=3, maxbox=maxbox):
    results = []

    step = before
    move = "forward"

    for i in range(0,dice):
        if step >= maxbox:
            move = "backward"

        if move == "forward":
            step += 1
        else:
            step -= 1
       
        results.append(step)


    return results


def playeralreadyavailable(player="", code=""):
    data = modelgetcsvplayers(code)
    for d in data:
        if (d["player"] == player):
            return True
    
    return False

def modelgetcsvquestion():
    query = "SELECT * FROM questions;"
    params = ()
    data = af_getdb(dbloc,query,params)
    # data = af_getcsvdict("static/db/ular/questions.csv")
    return data

def getquestions():
    data = modelgetcsvquestion()
    return data

def getquestion(id=""):
    data = modelgetcsvquestion()
    result = []
    for d in data:
        if d["id"] == id:
            result.append(d)
    
    return result

def getquestionstopic(topic=""):
    data = modelgetcsvquestion()
    result = []
    for d in data:
        if d["topic"] == topic:
            result.append(d)
    
    return result

def getrandomquestiontopic(topic=""):
    data = modelgetcsvquestion()
    result = []
    for d in data:
        if d["topic"] == topic:
            result.append(d)

    return random.choices(result)

def getrandomquestion():
    data = modelgetcsvquestion()
    return random.choices(data)

def submitanswer(id="", answer=""):
    data = modelgetcsvquestion()
    
    for d in data:
        if d["id"] == id:
            if d["answer"] == answer:
                return {
                    "status": "ok",
                    "answer": True
                }
            else:
                return {
                    "status": "ok",
                    "answer": False
                }

    return {
        "status": "error",
        "message": "question not found"
    }

def getendbystartladdersnake(start=0):

    end = 0
    data = modelgetcsvconf()
    for d in data:
        if d["start"] == str(start):
            return int(d["end"])
    return end

def getladdersnakeinfo(start=0):

    ladderorsnake = ""

    end = 0
    data = modelgetcsvconf()
    for d in data:
        if d["start"] == str(start):
            end = int(d["end"])
            if int(start) > int(end):
                ladderorsnake = "snake"
            else:
                ladderorsnake = "ladder"
            
            return {
                "end": end,
                "ladderorsnake": ladderorsnake
            }
    return {
        "end": end,
        "ladderorsnake": ladderorsnake
    }

def endgame(code=""):
    query = "UPDATE room SET state = ? WHERE code = ?;"
    params = ("ended", code,)
    data = af_getdb(dbloc,query,params)
    # new_data = {"state":"ended"}
    # af_replacecsv2(roomcsv, "code", code, new_data)