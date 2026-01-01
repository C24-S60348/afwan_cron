#controllers/habitmultiplayer2.py

from flask import abort, jsonify, request, Blueprint, render_template, render_template_string, session

from ..utils.db_helper import *
from ..utils.crud_helper import *
from ..utils.adminhandle_helper import *
from ..utils.html_helper import *
from ..utils.excel_helper import *
from ..models.habitmultiplayer import *
from ..utils.checker_helper import *
from ..utils.login_helper import *
from ..utils.outsource_helper import *
import secrets
import hashlib
import re
import string

dbloc = "static/db/habit.db"

#http://127.0.0.1:5001/api/habit/register?email=afwanhaziq%40yahoo.com&password=12345&passwordadmin=afwan&passwordrepeat=12345
#http://127.0.0.1:5001/api/habit/login?email=afwanhaziq%40yahoo.com&password=12345&keeptoken=yes

#member
#http://127.0.0.1:5001/api/habit/addmember?habitid=4&member=afwanhaziq
#http://127.0.0.1:5001/api/habit/deletemember?habitid=4&member=afwanhaziq

#http://127.0.0.1:5001/api/habit/forgotpassword?email=afwanhaziq%40yahoo.com
#http://127.0.0.1:5001/api/habit/changepassword?password=12345&token=992f69b6e5b4f39d9da4ad100c3848d7

#http://127.0.0.1:5001/api/habit/updateprofile?token=a2a6fca1a91a20cc974a895ecbb2afae&name=Afwan
#http://127.0.0.1:5001/api/habit/readprofile?usernames=afwanhaziq%40yahoo.com,ikan


"""
-Register   -Login

-Deleteaccount
-ForgotPassword
-Update Profile

"""
restrictmode = True
habitmultiplayer2_blueprint = Blueprint('habitmultiplayer2', __name__)

def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def modelcheckemail(email="test@test.com"):
    # Regular expression pattern for a general valid email
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    # pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def generate_token():
    return secrets.token_hex(16)

def hash_password_sha256(password):
    # Create a SHA-256 hash of the password
    sha_signature = hashlib.sha256(password.encode()).hexdigest()
    return sha_signature

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
            query = f"SELECT * FROM users WHERE username = ? AND deleted_at IS NULL"
            params = (username,)
            dbdata = af_getdb(dbloc, query, params)
            
            if dbdata and len(dbdata) > 0:
                profile = {
                    "username": username,
                    "name": dbdata[0].get('name', '') if 'name' in dbdata[0] else ''
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
    
    query = f"SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
    params = (token,)
    dbdata = af_getdb(dbloc, query, params)

    if dbdata:
        username = dbdata[0]['username']
        
        query = f"UPDATE users SET name = ? WHERE username = ? AND deleted_at IS NULL"
        params = (name,username,)
        dbdata = af_getdb(dbloc, query, params)

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
    
    newpassword = generate_random_password(12)
    query = f"UPDATE users SET forgotpassword = ?, password = ? WHERE username = ? AND deleted_at IS NULL"
    params = ("yes",hash_password_sha256(newpassword),username)
    dbdata = af_getdb(dbloc, query, params)
    print (newpassword)

    modelsendemail(username, newpassword)
    return jsonify({"status":"ok", "result":"If an account with this email exists, a password reset link will be sent."})
    
@habitmultiplayer2_blueprint.route('/api/habit/changepassword', methods=['GET', 'POST'])
def changepasswordapi():
    token = getpostget("token")
    password = getpostget("password")

    if token == "":
        return jsonify({"status":"ok", "result":"please enter token"})
    if password == "":
        return jsonify({"status":"ok", "result":"please enter password"})
    
    query = f"SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
    params = (token,)
    dbdata = af_getdb(dbloc, query, params)

    if dbdata:
        username = dbdata[0]['username']

        query = f"SELECT * FROM users WHERE username = ? AND forgotpassword = ? AND deleted_at IS NULL"
        params = (username,"yes",)
        dbdata = af_getdb(dbloc, query, params)

        if dbdata:
            query = f"UPDATE users SET forgotpassword = ?, password = ? WHERE username = ? AND deleted_at IS NULL"
            params = ("",hash_password_sha256(password),username,)
            dbdata = af_getdb(dbloc, query, params)

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

    query = f"SELECT * FROM users WHERE username = ? AND deleted_at IS NULL"
    params = (username,)
    dbdata = af_getdb(dbloc, query, params)

    
    
    password = getpostget("password")
    passwordrepeat = getpostget("passwordrepeat")
    passwordadmin = getpostget("passwordadmin")

    if passwordadmin != "afwan":
        message = "Wrong password admin!"
        return jsonify({"status":"error", "result":message})

    if password != passwordrepeat:
        message = "Password is not same with Repeat password!"
        return jsonify({"status":"error", "result":message})
    
    query = f"SELECT * FROM users WHERE username = ? AND deleted_at IS NULL"
    params = (username,)
    dbdata = af_getdb(dbloc, query, params)

    if dbdata:
        message = "The username is already exist!"
        return jsonify({"status":"error", "result":message})
    else:
        query = f"INSERT INTO users (username,password,created_at) VALUES (?,?,?)"
        params = (username,hash_password_sha256(password),datetime.now(),)
        dbdata = af_getdb(dbloc, query, params)

        message = "Successfully registered, now please login"
        return jsonify({"status":"ok", "result":message})
    

@habitmultiplayer2_blueprint.route('/api/habit/login', methods=['GET', 'POST'])
def loginapi():
    username = getpostget("email")
    password = getpostget("password")
    keeptoken = getpostget("keeptoken")
    
    if username == "" and password == "":
        return jsonify({"status":"ok", "result":"please enter login details"})
    
    query = f"SELECT * FROM users WHERE username = ? AND password = ? AND deleted_at IS NULL"
    params = (username,hash_password_sha256(password),)
    dbdata = af_getdb(dbloc, query, params)
    
    if dbdata:
        token = generate_token()
        result = {}
        result['username'] = username
        if dbdata[0]["token"]:
            result['token'] = dbdata[0]["token"]
        else:
            query = f"UPDATE users SET token = ? WHERE username = ? AND password = ? AND deleted_at IS NULL"
            params = (token,username,hash_password_sha256(password),)
            dbdata = af_getdb(dbloc, query, params)
            result['token'] = token

        return jsonify({"status":"ok", "result":result})
    else:
        return jsonify({"status":"error", "result":"Wrong username or password"})

@habitmultiplayer2_blueprint.route('/api/habit/logout', methods=['GET', 'POST'])
def logoutapi():
    token = getpostget("token")
    
    return jsonify({"status":"ok", "result":f"Logged out"})
    
    query = f"UPDATE users SET token = ? WHERE token = ? AND deleted_at IS NULL"
    params = ("",token,)
    dbdata = af_getdb(dbloc, query, params)
    
    if dbdata:
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
    
    query = f"SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
    params = (token,)
    dbdata = af_getdb(dbloc, query, params)

    if dbdata or inputnotvalidated(token):

        if inputnotvalidated(token):
            username = "guest"
            if restrictmode:
                return jsonify(
                {
                    "status": "error",
                    "message": "Guest cannot perform this action. Please login."
                })
        else:
            username = dbdata[0]['username']
            if username == member:
                return jsonify(
                    {
                        "status": "error",
                        "message": "You cannot add yourself as member!"
                    }
                )
        
        query = f"SELECT * FROM habit WHERE id = ? AND deleted_at IS NULL"
        params = (habitid,)
        dbdata = af_getdb(dbloc, query, params)
        
        #the data was user's data
        cango = False
        if dbdata == []:
            return jsonify(
                {
                    "status": "error",
                    "message": "The habit is not available"
                }
            )
        for g in dbdata:
            if g['username'] == username:
                cango = True
        
        #check if the user already member
        query = f"SELECT * FROM member WHERE habitid = ? AND member = ? AND deleted_at IS NULL"
        params = (habitid,member,)
        dbdata = af_getdb(dbloc, query, params)

        if dbdata == []:       

            if cango:
                query = f"INSERT INTO member (habitid,member,created_at) VALUES (?,?,?)"
                params = (habitid,member,datetime.now(),)
                dbdata = af_getdb(dbloc, query, params)

                return jsonify(
                    {
                        "status": "ok",
                        "message": f"member {member} added"
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
    
    query = f"SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
    params = (token,)
    dbdata = af_getdb(dbloc, query, params)

    if dbdata or inputnotvalidated(token):

        if inputnotvalidated(token):
            username = "guest"
            if restrictmode:
                return jsonify(
                {
                    "status": "error",
                    "message": "Guest cannot perform this action. Please login."
                })
        else:
            username = dbdata[0]['username']
        
        query = f"SELECT * FROM habit WHERE id = ? AND deleted_at IS NULL"
        params = (habitid,)
        dbdata = af_getdb(dbloc, query, params)

        #the data was user's data
        cango = False
        if dbdata == []:
            return jsonify(
                {
                    "status": "error",
                    "message": "The habit is not available"
                }
            )
        for g in dbdata:
            if g['username'] == username:
                cango = True

        if cango:

            query = f"UPDATE member SET deleted_at = ? WHERE habitid = ? AND member = ? AND deleted_at IS NULL"
            params = (datetime.now(),habitid,member,)
            dbdata = af_getdb(dbloc, query, params)

            return jsonify({
                "status": "ok",
                "message": f"member {member} deleted",
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
    
    query = f"SELECT * FROM users WHERE username = ? AND password = ? AND deleted_at IS NULL"
    params = (username,hash_password_sha256(password),)
    dbdata = af_getdb(dbloc, query, params)
    
    if dbdata:
        query = f"INSERT INTO deleteaccount (username,password,created_at) VALUES (?,?,?)"
        params = (username,password,datetime.now(),)
        dbdata = af_getdb(dbloc, query, params)

        message = f"{username} is just submitted to delete their account for Habit Multiplayer"
        modelsendtelegrammessage(message)
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