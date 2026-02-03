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

def init_ular_db():
    """Initialize the ular database tables if they don't exist"""
    try:
        # Create conf table
        query = """CREATE TABLE IF NOT EXISTS conf (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start TEXT,
            end TEXT,
            type TEXT
        );"""
        af_getdb(dbloc, query, ())
        
        # Create room table
        query = """CREATE TABLE IF NOT EXISTS room (
            code TEXT PRIMARY KEY,
            turn TEXT,
            state TEXT,
            questionid TEXT,
            maxbox INTEGER,
            topic TEXT,
            selectedanswer TEXT,
            answercorrect TEXT
        );"""
        af_getdb(dbloc, query, ())
        
        # Create players table
        query = """CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            player TEXT,
            pos INTEGER,
            color TEXT,
            questionright TEXT,
            questionget TEXT
        );"""
        af_getdb(dbloc, query, ())
        
        # Create questions table
        query = """CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            question TEXT,
            a1 TEXT,
            a2 TEXT,
            a3 TEXT,
            a4 TEXT,
            answer TEXT,
            topic TEXT
        );"""
        af_getdb(dbloc, query, ())
        
        # Check if conf table is empty and add sample data
        query = "SELECT COUNT(*) as count FROM conf;"
        result = af_getdb(dbloc, query, ())
        if isinstance(result, list) and len(result) > 0 and result[0].get('count', 0) == 0:
            # Add sample ladder and snake configurations
            query = """INSERT INTO conf (start, end, type) VALUES 
                ('3', '10', 'ladder'),
                ('6', '15', 'ladder'),
                ('12', '20', 'ladder'),
                ('18', '8', 'snake'),
                ('22', '12', 'snake'),
                ('25', '5', 'snake');"""
            af_getdb(dbloc, query, ())
            print("✅ Added sample ladder/snake configurations")
        
        # Check if questions table is empty and add sample data
        query = "SELECT COUNT(*) as count FROM questions;"
        result = af_getdb(dbloc, query, ())
        if isinstance(result, list) and len(result) > 0 and result[0].get('count', 0) == 0:
            # Add sample questions
            query = """INSERT INTO questions (id, question, a1, a2, a3, a4, answer, topic) VALUES 
                ('1', 'What is the formula for force?', 'F=ma', 'F=mv', 'F=mgh', 'F=1/2mv^2', 'a1', 'fizik'),
                ('2', 'What is the speed of light in vacuum?', '3x10^6 m/s', '3x10^7 m/s', '3x10^8 m/s', '3x10^9 m/s', 'a3', 'fizik'),
                ('3', 'What is Newton''s first law about?', 'Force', 'Inertia', 'Acceleration', 'Momentum', 'a2', 'fizik'),
                ('4', 'What is the unit of energy?', 'Newton', 'Watt', 'Joule', 'Pascal', 'a3', 'fizik'),
                ('5', 'What is the powerhouse of the cell?', 'Nucleus', 'Ribosome', 'Mitochondria', 'Chloroplast', 'a3', 'biologi'),
                ('6', 'What is the process by which plants make food?', 'Respiration', 'Photosynthesis', 'Digestion', 'Fermentation', 'a2', 'biologi'),
                ('7', 'What is DNA?', 'A protein', 'A genetic material', 'A carbohydrate', 'A lipid', 'a2', 'biologi'),
                ('8', 'What is the largest organ in the human body?', 'Heart', 'Liver', 'Brain', 'Skin', 'a4', 'biologi');"""
            af_getdb(dbloc, query, ())
            print("✅ Added sample questions")
        
        print("✅ Ular database tables initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing ular database: {e}")

def modelgetcsvconf():
    query = "SELECT * FROM conf;"
    params = ()
    data = af_getdb(dbloc,query,params)
    # data = af_getcsvdict(confcsv)
    # Handle case where af_getdb returns a string (error message)
    if isinstance(data, str):
        return []
    return data

def modelgetcsvroom():
    query = "SELECT * FROM room;"
    params = ()
    data = af_getdb(dbloc,query,params)
    # data = af_getcsvdict(roomcsv)
    # Handle case where af_getdb returns a string (error message)
    if isinstance(data, str):
        return []
    return data

def modelgetcsvplayers(code=""):
    query = "SELECT * FROM players;"
    params = ()
    data = af_getdb(dbloc,query,params)
    # data = af_getcsvdict(playerscsv)
    # Handle case where af_getdb returns a string (error message)
    if isinstance(data, str):
        return []
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
    # Handle case where af_getdb returns a string (error message)
    if isinstance(data, str):
        return []
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
    query = "INSERT INTO room (code,turn,state,questionid,maxbox,topic,dice) VALUES (?,?,?,?,?,?,?);"
    params = (code, turn, state, "", maxbox, topic, 0)
    data = af_getdb(dbloc,query,params)
    # Check if there was an error
    if isinstance(data, str) and ("error" in data.lower() or "Query executed" not in data):
        print(f"Error adding room: {data}")
    # af_addcsv(roomcsv, [
    #     code, turn, state, "", maxbox, topic
    # ])

def adddataplayer(code="", player="", pos=0, color="white"):
    query = "INSERT INTO players (code,player,pos,color,questionright,questionget) VALUES (?,?,?,?,?,?);"
    params = (code, player, pos, color, "", "")
    data = af_getdb(dbloc,query,params)
    # Check if there was an error
    if isinstance(data, str) and ("error" in data.lower() or "Query executed" not in data):
        print(f"Error adding player: {data}")
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


def update_room_dice(code="", dice=0):
    """Update the dice value in the room table"""
    query = "UPDATE room SET dice = ? WHERE code = ?;"
    params = (dice, code,)
    data = af_getdb(dbloc, query, params)
    if isinstance(data, str) and ("error" in data.lower() or "Query executed" not in data):
        print(f"Error updating room dice: {data}")


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
    
    # Update dice value in room
    update_room_dice(code, dicenum)
    
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
    # Handle case where af_getdb returns a string (error message)
    if isinstance(data, str):
        return []
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
            # Case-insensitive comparison and strip whitespace
            correct_answer = str(d["answer"]).strip().lower()
            submitted_answer = str(answer).strip().lower()
            
            if correct_answer == submitted_answer:
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