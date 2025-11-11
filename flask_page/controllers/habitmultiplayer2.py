#controllers/habitmultiplayer2.py

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
deleteaccountcsv = "static/db/habit/deleteaccount.csv"

#http://127.0.0.1:5001/api/habit/register?username=afwanhaziq&password=12345&passwordadmin=afwan&passwordrepeat=12345
#http://127.0.0.1:5001/api/habit/login?username=afwanhaziq&password=12345&keeptoken=yes

"""
-Register   -Login

-Deleteaccount


"""
restrictmode = True
habitmultiplayer2_blueprint = Blueprint('habitmultiplayer2', __name__)

@habitmultiplayer2_blueprint.route('/api/habit/register', methods=['GET', 'POST'])
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

@habitmultiplayer2_blueprint.route('/api/habit/login', methods=['GET', 'POST'])
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

@habitmultiplayer2_blueprint.route('/api/habit/logout', methods=['GET', 'POST'])
def logoutapi():
    token = getpostget("token")
    
    if modellogout(token, userscsv) == "":
        return jsonify({"status":"ok", "result":f"Logged out"})
    else:
        return jsonify({"status":"error", "result":f"No user with token {token}"})
    
#add member / update / delete = ""
#habitid,memberusername
# -> habit -> member --> afwan;
@habitmultiplayer2_blueprint.route('/api/habit/addmember', methods=['GET', 'POST'])
def addmember():
    member = getpostget("member")
    token = getpostget("token")
    habitid = getpostget("habitid")
    
    if inputnotvalidated(habitid):
        return jsonifynotvalid("habitid")
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
            if restrictmode:
                return jsonify(
                {
                    "status": "error",
                    "message": "Guest cannot perform this action. Please login."
                })
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
        
        #check if the user already member
        data = {}
        data['csv'] = membercsv
        data['targetname'] = "habitid"
        data['targetdata'] = str(habitid)
        data['targetname2'] = "member"
        data['targetdata2'] = member
        getdata = cread2(data)
        if getdata == []:       

            if cango:
                data = {}
                data['csv'] = membercsv
                data['habitid'] = habitid
                data['member'] = member
                data['created_at'] = datetime.now()
                data['deleted_at'] = ""
                createdata = ccreate(data)

                return jsonify(
                    {
                        "status": "ok",
                        "message": "member added",
                        "data": createdata
                    }
                )
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
                    "message": "The member already exist"
                }
            )
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )

@habitmultiplayer2_blueprint.route('/api/habit/deletemember', methods=['GET', 'POST'])
def deletemember():
    member = getpostget("member")
    token = getpostget("token")
    habitid = getpostget("habitid")

    if inputnotvalidated(habitid):
        return jsonifynotvalid("habitid")
    if inputnotvalidated(member):
        return jsonifynotvalid("member")
    
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
        data['targetdata'] = str(habitid)
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
            data['csv'] = membercsv
            data['targetname'] = "habitid"
            data['targetdata'] = str(habitid)
            data['targetname2'] = "member"
            data['targetdata2'] = str(member)
            getdata = cdelete2(data)

            if getdata == []:
                return jsonify({
                    "status": "ok",
                    "message": f"member {member} already deleted",
                })
            else:

                return jsonify({
                    "status": "ok",
                    "message": f"member {member} deleted",
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

@habitmultiplayer2_blueprint.route('/api/habit/deleteaccount', methods=['GET', 'POST'])
def deleteaccount():
    username = getpostget("username")
    password = getpostget("password")

    if inputnotvalidated(username):
        return jsonifynotvalid("username")
    if inputnotvalidated(password):
        return jsonifynotvalid("password")
    
    if modelloginhash(username, password, userscsv):
        data = {}
        data['csv'] = deleteaccountcsv
        data['username'] = username
        data['password'] = password
        data['created_at'] = datetime.now()
        data['deleted_at'] = ""
        createdata = ccreate(data)

        message = f"{username} is just submitted to delete their account for Habit Multiplayer"
        #todo - send telegram message
        return jsonify({
            "status": "ok",
            "message": f"Your account is submitted to be deleted. Thankyou for using our app",
        })
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Invalid username and password combination!"
        })


@habitmultiplayer2_blueprint.route('/habit/deleteaccount', methods=['GET', 'POST'])
def deleteaccounthtml():
    return render_template("habit/deleteaccount.html")