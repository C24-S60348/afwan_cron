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
profilecsv = "static/db/habit/profile.csv"

#http://127.0.0.1:5001/api/habit/register?username=afwanhaziq&password=12345&passwordadmin=afwan&passwordrepeat=12345
#http://127.0.0.1:5001/api/habit/login?username=afwanhaziq&password=12345&keeptoken=yes

#http://127.0.0.1:5001/api/habit/forgotpassword?email=afwanhaziq%40yahoo.com
#http://127.0.0.1:5001/api/habit/changepassword?password=afwan&token=065ac561757cdb4eb06b68f6883a2c61

#http://127.0.0.1:5001/api/habit/updateprofile?token=a2a6fca1a91a20cc974a895ecbb2afae&name=Afwan


"""
-Register   -Login

-Deleteaccount
-ForgotPassword
-Update Profile

todo:
-send email using brevo

"""
restrictmode = True
habitmultiplayer2_blueprint = Blueprint('habitmultiplayer2', __name__)

@habitmultiplayer2_blueprint.route('/api/habit/readprofile', methods=['GET', 'POST'])
def readprofile():
    usernames = getpostget("usernames")  # Comma-separated list of usernames
    
    if inputnotvalidated(usernames):
        return jsonifynotvalid("usernames")
    
    # Get profile data for requested usernames
    username_list = []
    if usernames:
        username_list = [u.strip() for u in usernames.split(',') if u.strip()]
    
    profiles = []
    if username_list:
        for username in username_list:
            data = {}
            data['csv'] = userscsv
            data['targetname'] = "username"
            data['targetdata'] = username
            userdata = cread(data)
            if userdata and len(userdata) > 0:
                profile = {
                    "username": username,
                    "name": userdata[0].get('name', '') if 'name' in userdata[0] else ''
                }
                profiles.append(profile)
    
    return jsonify({
        "status": "ok",
        "data": profiles
    })

@habitmultiplayer2_blueprint.route('/api/habit/updateprofile', methods=['GET', 'POST'])
def updateprofile():
    name = getpostget("name")
    token = getpostget("token")
    
    if inputnotvalidated(name):
        return jsonifynotvalid("name")
    if inputnotvalidated(token):
        return jsonifynotvalid("token")

    mydata = modelchecktokendata(token, userscsv)
    if mydata:
        username = mydata['username']
        
        modelupdateprofile(username, name, userscsv)
        return jsonify(
            {
                "status": "ok",
                "message": "profile updated"
            }
        )
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )


@habitmultiplayer2_blueprint.route('/api/habit/forgotpassword', methods=['GET', 'POST'])
def forgotpasswordapi():
    username = getpostget("email")
    
    if username == "":
        return jsonify({"status":"ok", "result":"please enter email"})
    
    modelsendforgotpasswordemail(username, userscsv)
    return jsonify({"status":"ok", "result":"If an account with this email exists, a password reset link will be sent."})
    # if modelgetusernameisexist(username, userscsv):
    #     if modelsendforgotpasswordemail(username, userscsv):
    #         return jsonify({"status":"ok", "result":"If an account with this email exists, a password reset link will be sent."})
    #     else:
    #         return jsonify({"status":"error", "result":"If an account with this email exists, a password reset link will be sent."})
    # else:
    #     return jsonify({"status":"error", "result":"The email doesn't exist on our app database."})
    
@habitmultiplayer2_blueprint.route('/api/habit/changepassword', methods=['GET', 'POST'])
def changepasswordapi():
    token = getpostget("token")
    password = getpostget("password")

    if token == "":
        return jsonify({"status":"ok", "result":"please enter token"})
    if password == "":
        return jsonify({"status":"ok", "result":"please enter password"})

    mydata = modelchecktokendata(token, userscsv)
    if mydata:
        username = mydata['username']
        if modelforgottedpassword(username, userscsv):
            new_data = {"forgotpassword":""}
            af_replacecsv2(userscsv, "username", username, new_data)
            new_data = {"password":hash_password_sha256(password)}
            af_replacecsv2(userscsv, "username", username, new_data)
            return jsonify({"status":"ok", "result":"Password updated."})
        else:
            return jsonify(
            {
                "status": "error",
                "message": "Your user didn't query for any forgotten password"
            })
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )

@habitmultiplayer2_blueprint.route('/api/habit/register', methods=['GET', 'POST'])
def registerapi():
    username = getpostget("email")
    if modelcheckemail(username) == False:
        message = "email is not valid"
        return jsonify({"status":"error", "result":message})
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
    username = getpostget("email")
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