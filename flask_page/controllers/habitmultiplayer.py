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
membercsv = "static/db/habit/member.csv"

"""
Nota:
Habit
-Create     -Read one-Read all  -Update     -Delete
Note
-Read   -Update/Add
Member
-Add    -Delete
History
-Read   -Update/Add

Todo
-fix - orang baru tkleh add notes
-added member ada satu je data


---All based on token, if no token, == "guest"

"""


#habit
#http://127.0.0.1:5001/api/habit/createhabit?url=ayammm&name=ikan23
#http://127.0.0.1:5001/api/habit/readhabit?targetname=id&targetdata=6
#http://127.0.0.1:5001/api/habit/readhabit
#http://127.0.0.1:5001/api/habit/updatehabit?id=12&newname=name&newdata=afwan1234
#http://127.0.0.1:5001/api/habit/deletehabit?id=12

#note
#http://127.0.0.1:5001/api/habit/readnote?habitid=2
#http://127.0.0.1:5001/api/habit/updatenote?habitid=2&notes=heyyoo

#member
#http://127.0.0.1:5001/api/habit/addmember?habitid=4&member=afwanhaziq
#http://127.0.0.1:5001/api/habit/deletemember?habitid=4&member=afwanhaziq

#history
#http://127.0.0.1:5001/api/habit/readhistory?habitid=1
#http://127.0.0.1:5001/api/habit/updatehistory?habitid=1&historydate=2025-10-11&historystatus=-1

restrictmode = True
habitmultiplayer_blueprint = Blueprint('habitmultiplayer', __name__, url_prefix="/api/habit")


    
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
        if restrictmode:
            return jsonify(
            {
                "status": "error",
                "message": "Guest cannot perform this action. Please login."
            })
        username = 'guest'
        data = {}
        data['csv'] = habitcsv
        data['username'] = username
        data['url'] = url
        data['name'] = name
        data['created_at'] = datetime.now()
        data['deleted_at'] = ""
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

        data = {}
        data['csv'] = habitcsv
        data['targetname'] = "username"
        data['targetdata'] = username
        getdata = cread(data)

        data = {}
        data['csv'] = membercsv
        data['targetname'] = "member"
        data['targetdata'] = username
        getdata2 = cread(data)
        getdata3 = []
        getdata5 = []

        for g in getdata2:
            data = {}
            data['csv'] = habitcsv
            data['targetname'] = "id"
            data['targetdata'] = g["habitid"]
            getdata3 = cread(data)
            if getdata3 != []:
                getdata5.append(getdata3[0])
        
        getdata.extend(getdata5)

        for g in getdata:
            data = {}
            data['csv'] = membercsv
            data['targetname'] = "habitid"
            data['targetdata'] = g["id"]
            getdata4 = cread(data)
            g["members"] = getdata4

        return jsonify({
            "status": "ok",
            "message": "get habit",
            "data" : getdata,
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
            if restrictmode:
                return jsonify(
                {
                    "status": "error",
                    "message": "Guest cannot perform this action. Please login."
                })
        else:
            username = mydata['username']
        
        data = {}
        data['csv'] = habitcsv
        data['targetname'] = "id"
        data['targetdata'] = str(id)
        getdata = cread(data)
        #the data was user's data
        cango = False
        if getdata == []:
            return jsonify(
                {
                    "status": "error",
                    "message": "The habit is not available"
                }
            )
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
                    "message": "You are not the owner of this habit"
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
            if restrictmode:
                return jsonify(
                {
                    "status": "error",
                    "message": "Guest cannot perform this action. Please login."
                })
        else:
            username = mydata['username']
        
        data = {}
        data['csv'] = habitcsv
        data['targetname'] = "id"
        data['targetdata'] = str(id)
        getdata = cread(data)
        #the data was user's data
        cango = False
        if getdata == []:
            return jsonify(
                {
                    "status": "error",
                    "message": "The habit is not available"
                }
            )
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
                    "message": "You are not the owner of this habit"
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
            if restrictmode:
                return jsonify(
                {
                    "status": "error",
                    "message": "Guest cannot perform this action. Please login."
                })
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
        
        data = {}
        data['csv'] = notescsv
        data['targetname'] = "habitid"
        data['targetdata'] = habitid
        getdata = cread(data)

        data = {}
        data['csv'] = habitcsv
        data['targetname'] = "id"
        data['targetdata'] = habitid
        getdata3 = cread(data)
        owner = getdata3[0]['username']

        data = {}
        data['csv'] = membercsv
        data['targetname'] = "habitid"
        data['targetdata'] = habitid
        getdata4 = cread(data)

        return jsonify({
            "status": "ok",
            "message": "get notes",
            "data" : getdata,
            "members": getdata4,
            "owner": owner,
        })
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
        
        data = {}
        data['csv'] = historycsv
        data['targetname'] = "habitid"
        data['targetdata'] = habitid
        getdata = cread(data)

        data = {}
        data['csv'] = habitcsv
        data['targetname'] = "id"
        data['targetdata'] = habitid
        getdata3 = cread(data)
        owner = getdata3[0]['username']

        data = {}
        data['csv'] = membercsv
        data['targetname'] = "habitid"
        data['targetdata'] = habitid
        getdata4 = cread(data)

        return jsonify({
            "status": "ok",
            "message": "get history",
            "data" : getdata,
            "members": getdata4,
            "owner": owner,
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