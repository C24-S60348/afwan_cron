#controllers/habitmultiplayer.py

from flask import abort, jsonify, request, Blueprint, render_template, render_template_string, session


from ..utils.crud_helper import *
from ..utils.adminhandle_helper import *
from ..utils.html_helper import *
from ..utils.excel_helper import *
from ..utils.login_helper import *
from ..models.habitmultiplayer import *
from ..utils.checker_helper import *
from ..utils.db_helper import *

dbloc = "static/db/habit/mydb.db"

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

---All based on token, if no token, == "guest"


"""


#habit
#http://127.0.0.1:5001/api/habit/createhabit?url=ayammm&name=ikan23
#http://127.0.0.1:5001/api/habit/readhabit
#http://127.0.0.1:5001/api/habit/updatehabit?id=12&newname=name&newdata=afwan1234
#http://127.0.0.1:5001/api/habit/deletehabit?id=12

#note
#http://127.0.0.1:5001/api/habit/readnote?habitid=2
#http://127.0.0.1:5001/api/habit/updatenote?habitid=2&notes=heyyoo

#history
#http://127.0.0.1:5001/api/habit/readhistory?habitid=1
#http://127.0.0.1:5001/api/habit/updatehistory?habitid=1&historydate=2025-10-11&historystatus=-1

restrictmode = True
habitmultiplayer_blueprint = Blueprint('habitmultiplayer', __name__, url_prefix="/api/habit")


    
@habitmultiplayer_blueprint.route('/test', methods=['GET', 'POST'])
def test():
    
    query = "SELECT * FROM habit WHERE (deleted_at IS NULL or deleted_at = '');"
    params = ()

    # query = "INSERT INTO habit (name, username, created_at) VALUES (?, ?, ?)"
    # params = ("ayam", "ikan", datetime.now())

    query = "UPDATE habit SET username = ? WHERE id = ?"
    params = ("ayam", 4)

    #Get all tables list
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    params = ()

    dbdata = af_getdb("my_database.db", query, params)

    return jsonify({
        "status": "ok",
        "message": dbdata
    })
    
    
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
        
        query = "INSERT INTO habit (username,url,name,created_at) VALUES (?,?,?,?);"
        params = (username,url,name,datetime.now(),)
        dbdata = af_getdb(dbloc, query, params)

        return jsonify({
            "status": "ok",
            "message": "habit careated",
            "data" : dbdata
        })

    query = "SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
    params = (token,)
    dbdata = af_getdb(dbloc, query, params)

    if dbdata:
        username = dbdata[0]['username']
        query = "INSERT INTO habit (username,url,name,created_at) VALUES (?,?,?,?);"
        params = (username,url,name,datetime.now(),)
        dbdata = af_getdb(dbloc, query, params)

        return jsonify(
            {
                "status": "ok",
                "message": "habit careated",
                "data": dbdata
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

    query = "SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
    params = (token,)
    dbdata = af_getdb(dbloc, query, params)
    if dbdata or inputnotvalidated(token):
        if inputnotvalidated(token):
            username = "guest"
        else:
            username = dbdata[0]['username']
        
        query = "SELECT * FROM habit "
        query += "WHERE username = ? AND deleted_at IS NULL"
        params = (username,)
        dbdata = af_getdb(dbloc, query, params)

        # for g in dbdata:
        #     if g["member"] == None:
        #         g["member"] = []
        
        # query = "SELECT * FROM member "
        # query += "WHERE member = ? AND deleted_at IS NULL"
        # params = (username,)
        # dbdata = af_getdb(dbloc, query, params)

        # data = {}
        # data['csv'] = habitcsv
        # data['targetname'] = "username"
        # data['targetdata'] = username
        # getdata = cread(data)

        # data = {}
        # data['csv'] = membercsv
        # data['targetname'] = "member"
        # data['targetdata'] = username
        # getdata2 = cread(data)
        # getdata3 = []
        # getdata5 = []

        # for g in getdata2:
        #     data = {}
        #     data['csv'] = habitcsv
        #     data['targetname'] = "id"
        #     data['targetdata'] = g["habitid"]
        #     getdata3 = cread(data)
        #     if getdata3 != []:
        #         getdata5.append(getdata3[0])
        
        # getdata.extend(getdata5)

        # for g in getdata:
        #     data = {}
        #     data['csv'] = membercsv
        #     data['targetname'] = "habitid"
        #     data['targetdata'] = g["id"]
        #     getdata4 = cread(data)
        #     g["members"] = getdata4

        query = "SELECT * FROM habit "
        query += "INNER JOIN member ON habit.id = member.habitid "
        query += "WHERE member.member = ? AND member.deleted_at IS NULL"
        params = (username,)
        dbdata3 = af_getdb(dbloc, query, params)
        
        dbdata.extend(dbdata3)
        
        #get members
        for g in dbdata:
            query = "SELECT * FROM member "
            query += "WHERE habitid = ? AND deleted_at IS NULL"
            params = (g["id"],)
            dbdata2 = af_getdb(dbloc, query, params)
            g["members"] = dbdata2

        return jsonify({
            "status": "ok",
            "message": "get habit",
            "data" : dbdata,
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
    
    query = "SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
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
        
        query = "SELECT * FROM habit WHERE id = ? AND deleted_at IS NULL"
        params = (id,)
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
            query = f"UPDATE habit SET {newname} = ? WHERE id = ? "
            params = (newdata, id,)
            dbdata = af_getdb(dbloc, query, params)

            # cupdate(data)
            query = f"SELECT * FROM habit WHERE id = ? AND deleted_at IS NULL"
            params = (id,)
            dbdata = af_getdb(dbloc, query, params)
            # readdata = cread(data)

            return  jsonify({
                "status": "ok",
                "message": "updated",
                "data": dbdata
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

    query = "SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
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
        
        query = f"SELECT * FROM habit WHERE id = ? AND deleted_at IS NULL "
        params = (id,)
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

            query = f"UPDATE habit SET deleted_at = ? WHERE id = ?"
            params = (datetime.now(),id,)
            dbdata = af_getdb(dbloc, query, params)

            return jsonify({
                "status": "ok",
                "message": "deleted",
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
    

    query = "SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
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
        
        
        query = f"SELECT * FROM notes WHERE username = ? AND habitid = ? AND deleted_at IS NULL"
        params = (username,habitid,)
        dbdata = af_getdb(dbloc, query, params)
        
        if dbdata:
            query = f"UPDATE notes SET notes = ? WHERE habitid = ? AND username = ?"
            params = (notes, habitid, username,)
            dbdata = af_getdb(dbloc, query, params)

        else:
            
            query = f"INSERT INTO notes (username,habitid,notes,created_at) VALUES (?,?,?,?)"
            params = (username,habitid,notes,datetime.now(),)
            dbdata = af_getdb(dbloc, query, params)
        
        query = f"SELECT * FROM notes WHERE username = ? AND habitid = ? AND deleted_at IS NULL"
        params = (username,habitid,)
        dbdata = af_getdb(dbloc, query, params)

        return jsonify(
                {
                    "status": "ok",
                    "message": "noteds updated",
                    "data": dbdata
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

    query = "SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
    params = (token,)
    dbdata = af_getdb(dbloc, query, params)
    if dbdata or inputnotvalidated(token):
        if inputnotvalidated(token):
            username = "guest"
        else:
            username = dbdata[0]['username']
        
        query = f"SELECT * FROM notes WHERE habitid = ? AND deleted_at IS NULL"
        params = (habitid,)
        dbdata = af_getdb(dbloc, query, params)

        #get members
        query = f"SELECT * FROM member WHERE habitid = ? AND deleted_at IS NULL"
        params = (habitid,)
        dbdata2 = af_getdb(dbloc, query, params)

        #get owner
        query = f"SELECT * FROM habit WHERE id = ? "
        params = (habitid,)
        dbdata3 = af_getdb(dbloc, query, params)
        owner = dbdata3[0]['username']

        return jsonify({
            "status": "ok",
            "message": "get notes",
            "data" : dbdata,
            "members": dbdata2,
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

    query = "SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
    params = (token,)
    dbdata = af_getdb(dbloc, query, params)
    if dbdata or inputnotvalidated(token):
        if inputnotvalidated(token):
            username = "guest"
        else:
            username = dbdata[0]['username']
        

        query = f"SELECT * FROM history WHERE habitid = ? AND deleted_at IS NULL"
        params = (habitid,)
        dbdata = af_getdb(dbloc, query, params)

        #get members
        query = f"SELECT * FROM member WHERE habitid = ? AND deleted_at IS NULL"
        params = (habitid,)
        dbdata2 = af_getdb(dbloc, query, params)

        #get owner
        query = f"SELECT * FROM habit WHERE id = ? "
        params = (habitid,)
        dbdata3 = af_getdb(dbloc, query, params)
        owner = dbdata3[0]['username']

        return jsonify({
            "status": "ok",
            "message": "get history",
            "data" : dbdata,
            "members": dbdata2,
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
    

    query = "SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
    params = (token,)
    dbdata = af_getdb(dbloc, query, params)
    if dbdata or inputnotvalidated(token):
        if inputnotvalidated(token):
            username = "guest"
        else:
            username = dbdata[0]['username']
        
        query = f"SELECT * FROM history WHERE habitid = ? AND username = ? AND historydate = ?"
        params = (habitid,username,historydate,)
        dbdata = af_getdb(dbloc, query, params)
        
        if dbdata:
            query = f"UPDATE history SET historystatus = ? WHERE habitid = ? AND username = ? AND historydate = ?"
            params = (historystatus,habitid,username,historydate,)
            dbdata3 = af_getdb(dbloc, query, params)
        else:
            query = f"INSERT INTO history (username,habitid,historydate,historystatus,created_at) VALUES (?,?,?,?,?) "
            params = (username,habitid,historydate,historystatus,datetime.now(),)
            dbdata3 = af_getdb(dbloc, query, params)

        query = f"SELECT * FROM history WHERE habitid = ?"
        params = (habitid,)
        dbdata = af_getdb(dbloc, query, params)
        return jsonify(
            {
                "status": "ok",
                "message": "history updated",
                "data": dbdata
            }
        )
    else:
        return jsonify(
        {
            "status": "error",
            "message": "Your token has expired"
        }
    )