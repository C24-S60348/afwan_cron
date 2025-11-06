#controllers/habitmultiplayer.py

from flask import abort, jsonify, request, Blueprint, render_template, render_template_string, session


from ..utils.crud_helper import *
from ..utils.adminhandle_helper import *
from ..utils.html_helper import *
from ..utils.excel_helper import *
from ..utils.login_helper import *
from ..models.habitmultiplayer import *
from ..utils.checker_helper import *

habitcsv = "static/db/habit/habit.csv"
notescsv  = "static/db/habit/notes.csv"
playerscsv = "static/db/habit/players.csv"
userscsv = "static/db/habit/users.csv"
historycsv = "static/db/habit/history.csv"

"""
Nota:
-Register
-Login

Habit
-Create 
-Read one
-Read all
-Update 
-Delete

Note
-Read
-Update/Add

Member
-Add/Update/Delete username 

History
-Read
-Update/Add

Todo:
-history
-implement

Additional:
-addmember - should not guest


---All based on token, if no token, == "guest"

"""

#http://127.0.0.1:5001/api/habit/register?username=afwanhaziq&password=12345&passwordadmin=afwan&passwordrepeat=12345
#http://127.0.0.1:5001/api/habit/login?username=afwanhaziq&password=12345&keeptoken=yes

#habit
#http://127.0.0.1:5001/api/habit/createhabit?url=ayammm&name=ikan23
#http://127.0.0.1:5001/api/habit/readhabit?targetname=id&targetdata=6
#http://127.0.0.1:5001/api/habit/readhabit
#http://127.0.0.1:5001/api/habit/updatehabit?targetname=id&targetdata=2&newname=name&newdata=afwan
#http://127.0.0.1:5001/api/habit/deletehabit?targetname=id&targetdata=1

#note
#http://127.0.0.1:5001/api/habit/readnote?habitid=2
#http://127.0.0.1:5001/api/habit/updatenote?habitid=2&notes=heyyoo

#member
#http://127.0.0.1:5001/api/habit/addmember?habitid=4&member=afwanhaziq

#history
#http://127.0.0.1:5001/api/habit/readhistory?habitid=1
#http://127.0.0.1:5001/api/habit/updatehistory?habitid=1&historydate=2025-10-11&historystatus=-1


habitmultiplayer_blueprint = Blueprint('habitmultiplayer', __name__, url_prefix="/api/habit")

@habitmultiplayer_blueprint.route('/register', methods=['GET', 'POST'])
def registerapi():

    username = getpostget("username")
    password = getpostget("password")
    passwordrepeat = getpostget("passwordrepeat")
    passwordadmin = getpostget("passwordadmin")

    message = modelregister(username, password, passwordrepeat, passwordadmin, userscsv)
    if message == "Successfully registered, now please login":
        return jsonify({"status":"ok", "result":message})
    else:
        return jsonify({"status":"error", "result":message})

@habitmultiplayer_blueprint.route('/login', methods=['GET', 'POST'])
def loginapi():

    username = getpostget("username")
    password = getpostget("password")
    keeptoken = getpostget("keeptoken")
        
    
    if username == "" and password == "":
        return jsonify({"status":"ok", "result":"please enter login details"})
    
    if modelloginhash(username, password, userscsv):
        result = {}
        result['token'] = modelgettokenbasedonkeeptoken(username, keeptoken, userscsv)
        result['username'] = username
        return jsonify({"status":"ok", "result":result})
    else:
        return jsonify({"status":"error", "result":"Wrong username or password"})

@habitmultiplayer_blueprint.route('/logout', methods=['GET', 'POST'])
def logoutapi():
    token = getpostget("token")
    
    if modellogout(token, userscsv) == "":
        return jsonify({"status":"ok", "result":f"Logged out"})
    else:
        return jsonify({"status":"error", "result":f"No user with token {token}"})
    
@habitmultiplayer_blueprint.route('/createhabit', methods=['GET', 'POST'])
def createhabitapi():
    url = getpostget("url")
    name = getpostget("name")
    token = getpostget("token")
    
    if inputnotvalidated(url):
        return jsonifynotvalid("url")
    if inputnotvalidated(name):
        return jsonifynotvalid("name")
    
    if token == "" or token == None:
        username = 'guest'
        data = {}
        data['csv'] = habitcsv
        data['username'] = username
        data['url'] = url
        data['name'] = name
        data['created_at'] = datetime.now()
        data['deleted_at'] = ""
        data['member'] = ""
        createdata = ccreate(data)

        return jsonify({
            "status": "ok",
            "message": "habit careated",
            "data" : createdata
        })

    mydata = modelchecktokendata(token, userscsv)
    if mydata:
        username = mydata['username']
        data = {}
        data['csv'] = habitcsv
        data['username'] = username
        data['url'] = url
        data['name'] = name
        data['created_at'] = datetime.now()
        data['deleted_at'] = ""
        createdata = ccreate(data)

        return jsonify(
            {
                "status": "ok",
                "message": "habit careated",
                "data": createdata
            }
        )
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )

@habitmultiplayer_blueprint.route('/readhabit', methods=['GET', 'POST'])
def readhabitapi():

    token = getpostget("token")

    mydata = modelchecktokendata(token, userscsv)
    if mydata or inputnotvalidated(token):
        if inputnotvalidated(token):
            username = "guest"
        else:
            username = mydata['username']
        print(username)
        data = {}
        data['csv'] = habitcsv
        data['targetname'] = "username"
        data['targetdata'] = username
        data['targetname2'] = "member"
        data['targetdata2'] = username
        getdata = creadboth(data)

        return jsonify({
            "status": "ok",
            "message": "get habit",
            "data" : getdata
        })
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )
 

@habitmultiplayer_blueprint.route('/updatehabit', methods=['GET', 'POST'])
def updatehabitapi():
    newname = getpostget("newname")
    newdata = getpostget("newdata")
    token = getpostget("token")
    id = getpostget("id")
    
    if inputnotvalidated(id):
        return jsonifynotvalid("id")
    if inputnotvalidated(newname):
        return jsonifynotvalid("newname")
    if inputnotvalidated(newdata):
        return jsonifynotvalid("newdata")
    
    
    mydata = modelchecktokendata(token, userscsv)
    if mydata or inputnotvalidated(token):

        if inputnotvalidated(token):
            username = "guest"
        else:
            username = mydata['username']
        
        data = {}
        data['csv'] = habitcsv
        data['targetname'] = "id"
        data['targetdata'] = str(id)
        getdata = cread(data)
        #the data was user's data
        cango = False
        for g in getdata:
            if g['username'] == username:
                cango = True

        if cango:
            data = {}
            data['csv'] = habitcsv
            data['targetname'] = "id"
            data['targetdata'] = str(id)
            data['newname'] = newname
            data['newdata'] = newdata

            cupdate(data)
            readdata = cread(data)

            return  jsonify({
                "status": "ok",
                "message": "updated",
                "data": readdata
            })
        else:
            return jsonify(
                {
                    "status": "error",
                    "message": "The id was not your habit"
                }
            )
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )

@habitmultiplayer_blueprint.route('/deletehabit', methods=['GET', 'POST'])
def deletehabitapi():
    id = getpostget("id")
    token = getpostget("token")

    mydata = modelchecktokendata(token, userscsv)
    if mydata or inputnotvalidated(token):

        if inputnotvalidated(token):
            username = "guest"
        else:
            username = mydata['username']
        
        data = {}
        data['csv'] = habitcsv
        data['targetname'] = "id"
        data['targetdata'] = str(id)
        getdata = cread(data)
        #the data was user's data
        cango = False
        for g in getdata:
            if g['username'] == username:
                cango = True

        if cango:

            data = {}
            data['csv'] = habitcsv
            data['targetname'] = "id"
            data['targetdata'] = str(id)
            getdata = cdelete(data)

            return jsonify({
                "status": "ok",
                "message": "deleted",
                "deleted_at" : getdata['deleted_at'],
            })
        
        else:
            return jsonify(
                {
                    "status": "error",
                    "message": "The id was not your habit"
                }
            )
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )


#create/update notes
#habitid,notes,username
@habitmultiplayer_blueprint.route('/updatenote', methods=['GET', 'POST'])
def updatenote():
    habitid = getpostget("habitid")
    notes = getpostget("notes")
    token = getpostget("token")
    
    if inputnotvalidated(habitid):
        return jsonifynotvalid("habitid")
    if inputnotvalidated(notes):
        return jsonifynotvalid("notes")
    

    mydata = modelchecktokendata(token, userscsv)
    if mydata or inputnotvalidated(token):
        if inputnotvalidated(token):
            username = "guest"
        else:
            username = mydata['username']
        
        data = {}
        data['csv'] = notescsv
        data['targetname'] = "habitid"
        data['targetdata'] = str(habitid)
        data['targetname2'] = "username"
        data['targetdata2'] = str(username)
        data['newname'] = "notes"
        data['newdata'] = str(notes)
        updateddata = cupdate2(data)
        if updateddata:
            readdata = cread2(data)
            return jsonify(
                {
                    "status": "ok",
                    "message": "noteds updated",
                    "data": readdata
                }
            )
        else:
            
            data = {}
            data['csv'] = notescsv
            data['username'] = username
            data['habitid'] = habitid
            data['notes'] = notes
            data['created_at'] = datetime.now()
            data['deleted_at'] = ""
            createdata = ccreate(data)

            return jsonify(
                {
                    "status": "ok",
                    "message": "noteds careated",
                    "data": createdata
                }
            )
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )



#read notes
#habitid
@habitmultiplayer_blueprint.route('/readnote', methods=['GET', 'POST'])
def readnote():

    token = getpostget("token")
    habitid = getpostget("habitid")

    if inputnotvalidated(habitid):
        return jsonifynotvalid("habitid")

    mydata = modelchecktokendata(token, userscsv)
    if mydata or inputnotvalidated(token):
        if inputnotvalidated(token):
            username = "guest"
        else:
            username = mydata['username']
        # print(username)
        data = {}
        data['csv'] = notescsv
        data['targetname'] = "habitid"
        data['targetdata'] = habitid
        # data['targetname2'] = "username"
        # data['targetdata2'] = username

        getdata = cread(data)
        # getdata = cread2(data)

        return jsonify({
            "status": "ok",
            "message": "get notes",
            "data" : getdata
        })
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )
 


#add member / update / delete = ""
#habitid,memberusername
# -> habit -> member --> afwan;
@habitmultiplayer_blueprint.route('/addmember', methods=['GET', 'POST'])
def addmember():
    newname = "member"
    member = getpostget("member")
    token = getpostget("token")
    habitid = getpostget("habitid")
    
    if inputnotvalidated(habitid):
        return jsonifynotvalid("habitid")
    if inputnotvalidated(newname):
        return jsonifynotvalid("newname")
    if inputnotvalidated(member):
        return jsonifynotvalid("member")
    
    # if member == "guest":
    #     return jsonify(
    #         {
    #             "status": "error",
    #             "message": "You cannot add guest as member"
    #         }
    #     )
    
    
    mydata = modelchecktokendata(token, userscsv)
    if mydata or inputnotvalidated(token):

        if inputnotvalidated(token):
            username = "guest"
            # return jsonify(
            #     {
            #         "status": "error",
            #         "message": "Guest cannot add member"
            #     }
            # )
        else:
            username = mydata['username']
            if username == member:
                return jsonify(
                    {
                        "status": "error",
                        "message": "You cannot add yourself as member!"
                    }
                )
        
        data = {}
        data['csv'] = habitcsv
        data['targetname'] = "id"
        data['targetdata'] = str(habitid)
        getdata = cread(data)
        #the data was user's data
        cango = False
        for g in getdata:
            if g['username'] == username:
                cango = True

        if cango:
            data = {}
            data['csv'] = habitcsv
            data['targetname'] = "id"
            data['targetdata'] = str(habitid)
            data['newname'] = newname
            data['newdata'] = member

            cupdate(data)
            data = cread(data)

            return  jsonify({
                "status": "ok",
                "message": "added member",
                "data": data
            })
        else:
            return jsonify(
                {
                    "status": "error",
                    "message": "The id was not your habit"
                }
            )
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )

@habitmultiplayer_blueprint.route('/readhistory', methods=['GET', 'POST'])
def readhistory():

    token = getpostget("token")
    habitid = getpostget("habitid")

    if inputnotvalidated(habitid):
        return jsonifynotvalid("habitid")

    mydata = modelchecktokendata(token, userscsv)
    if mydata or inputnotvalidated(token):
        if inputnotvalidated(token):
            username = "guest"
        else:
            username = mydata['username']
        # print(username)
        data = {}
        data['csv'] = historycsv
        data['targetname'] = "habitid"
        data['targetdata'] = habitid
        # data['targetname2'] = "username"
        # data['targetdata2'] = username

        getdata = cread(data)
        # getdata = cread2(data)

        return jsonify({
            "status": "ok",
            "message": "get history",
            "data" : getdata
        })
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )
 

@habitmultiplayer_blueprint.route('/updatehistory', methods=['GET', 'POST'])
def updatehistory():
    habitid = getpostget("habitid")
    historydate = getpostget("historydate")
    historystatus = getpostget("historystatus")
    token = getpostget("token")
    
    if inputnotvalidated(habitid):
        return jsonifynotvalid("habitid")
    if inputnotvalidated(historydate):
        return jsonifynotvalid("historydate")
    if inputnotvalidated(historystatus):
        return jsonifynotvalid("historystatus")
    

    mydata = modelchecktokendata(token, userscsv)
    if mydata or inputnotvalidated(token):
        if inputnotvalidated(token):
            username = "guest"
        else:
            username = mydata['username']
        
        data = {}
        data['csv'] = historycsv
        data['targetname'] = "habitid"
        data['targetdata'] = str(habitid)
        data['targetname2'] = "username"
        data['targetdata2'] = str(username)
        data['targetname3'] = "historydate"
        data['targetdata3'] = str(historydate)
        data['newname'] = "historystatus"
        data['newdata'] = str(historystatus)
        updateddata = cupdate3(data)
        if updateddata:
            readdata = cread2(data)
            return jsonify(
                {
                    "status": "ok",
                    "message": "history updated",
                    "data": readdata
                }
            )
        else:
            
            data = {}
            data['csv'] = historycsv
            data['username'] = username
            data['habitid'] = habitid
            data['historydate'] = historydate
            data['historystatus'] = historystatus
            data['created_at'] = datetime.now()
            data['deleted_at'] = ""
            createdata = ccreate(data)

            return jsonify(
                {
                    "status": "ok",
                    "message": "history careated",
                    "data": createdata
                }
            )
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )