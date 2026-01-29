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
import os
import sqlite3

dbloc = "static/db/habit.db"

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

restrictmode = False
habitmultiplayer_blueprint = Blueprint('habitmultiplayer', __name__, url_prefix="/api/habit")

@habitmultiplayer_blueprint.route('/healthcheck', methods=['GET', 'POST'])
def healthcheck():
    return jsonify({
        "status": "ok",
        "message": "healthcheck"
    })

@habitmultiplayer_blueprint.route('/initdb', methods=['GET', 'POST'])
def initdb():
    """
    Initialize Habit Multiplayer SQLite database (create db file + required tables).
    This endpoint is idempotent (safe to call multiple times).
    """
    # Ensure folder exists (and DB file will be created on first connect)
    db_dir = os.path.dirname(dbloc)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(dbloc)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        # users: used by habitmultiplayer.py + habitmultiplayer2.py
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT,
                token TEXT,
                name TEXT,
                forgotpassword TEXT,
                created_at DATETIME,
                deleted_at DATETIME
            );
            """
        )

        # habit: used by habitmultiplayer.py
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS habit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                url TEXT,
                name TEXT,
                created_at DATETIME,
                deleted_at DATETIME
            );
            """
        )

        # member: used by habitmultiplayer.py + habitmultiplayer2.py
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS member (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habitid INTEGER NOT NULL,
                member TEXT NOT NULL,
                created_at DATETIME,
                deleted_at DATETIME
            );
            """
        )

        # notes: used by habitmultiplayer.py
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                habitid INTEGER NOT NULL,
                notes TEXT,
                created_at DATETIME,
                deleted_at DATETIME
            );
            """
        )

        # history: used by habitmultiplayer.py
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                habitid INTEGER NOT NULL,
                historydate TEXT,
                historystatus TEXT,
                created_at DATETIME,
                deleted_at DATETIME
            );
            """
        )

        # deleteaccount: used by habitmultiplayer2.py
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS deleteaccount (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT,
                created_at DATETIME,
                deleted_at DATETIME
            );
            """
        )

        # Helpful indexes for common lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_token ON users(token);")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_habit_username ON habit(username);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_member_habitid ON member(habitid);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_member_member ON member(member);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_habitid ON notes(habitid);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_habitid ON history(habitid);")

        conn.commit()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
        tables = [r[0] for r in cursor.fetchall()]
        return jsonify({
            "status": "ok",
            "message": "initdb done",
            "db": dbloc,
            "tables": tables,
        })
    finally:
        conn.close()
    
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
    alluser = getpostget("alluser")
    
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
        
        if alluser == "yes":
            username = "alluser"
        
        
        query = f"SELECT * FROM notes WHERE habitid = ? AND username = ? AND deleted_at IS NULL"
        params = (habitid,username,)
        dbdata = af_getdb(dbloc, query, params)
        
        if dbdata:
            query = f"UPDATE notes SET notes = ? WHERE habitid = ? AND username = ?"
            params = (notes, habitid, username,)
            dbdata = af_getdb(dbloc, query, params)

        else:
            
            query = f"INSERT INTO notes (username,habitid,notes,created_at) VALUES (?,?,?,?)"
            params = (username,habitid,notes,datetime.now(),)
            dbdata = af_getdb(dbloc, query, params)
        
        query = f"SELECT * FROM notes WHERE habitid = ? AND username = ? AND deleted_at IS NULL"
        params = (habitid,username,)
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

@habitmultiplayer_blueprint.route('/top3habits', methods=['GET', 'POST'])
def top3habits():
    """
    Get top 3 habits tracked in the last 5 days for the current user
    Returns habits sorted by number of check-ins (historystatus = 1) in last 5 days
    """
    token = getpostget("token")
    
    query = "SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
    params = (token,)
    dbdata = af_getdb(dbloc, query, params)
    
    if dbdata or inputnotvalidated(token):
        if inputnotvalidated(token):
            username = "guest"
        else:
            username = dbdata[0]['username']
        
        # Get date 5 days ago
        from datetime import datetime, timedelta
        five_days_ago = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        
        # Get all user's habits
        query = "SELECT * FROM habit WHERE username = ? AND deleted_at IS NULL"
        params = (username,)
        user_habits = af_getdb(dbloc, query, params)
        
        # Also get habits where user is a member
        query = """SELECT habit.* FROM habit 
                   INNER JOIN member ON habit.id = member.habitid 
                   WHERE member.member = ? AND member.deleted_at IS NULL"""
        params = (username,)
        member_habits = af_getdb(dbloc, query, params)
        
        # Combine both lists
        all_habits = user_habits + member_habits
        
        # For each habit, count check-ins in last 5 days
        habit_counts = []
        for habit in all_habits:
            habitid = habit['id']
            
            # Count positive check-ins (historystatus = 1) in last 5 days for this user
            query = """SELECT COUNT(*) as count FROM history 
                       WHERE habitid = ? AND username = ? 
                       AND historydate >= ? 
                       AND historystatus = '1'
                       AND deleted_at IS NULL"""
            params = (habitid, username, five_days_ago)
            count_result = af_getdb(dbloc, query, params)
            
            count = count_result[0]['count'] if count_result else 0
            
            habit_counts.append({
                'id': habit['id'],
                'name': habit['name'],
                'url': habit['url'],
                'count': count
            })
        
        # Sort by count descending and get top 3
        habit_counts.sort(key=lambda x: x['count'], reverse=True)
        top3 = habit_counts[:3]
        
        return jsonify({
            "status": "ok",
            "message": "top 3 habits",
            "data": top3
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Your token has expired"
        })

@habitmultiplayer_blueprint.route('/profilewithtop3', methods=['GET', 'POST'])
def profilewithtop3():
    """
    Combined API that returns profile info and top 3 habits in one call
    """
    token = getpostget("token")
    
    query = "SELECT * FROM users WHERE token = ? AND deleted_at IS NULL"
    params = (token,)
    dbdata = af_getdb(dbloc, query, params)
    
    if dbdata or inputnotvalidated(token):
        if inputnotvalidated(token):
            username = "guest"
            profile = {
                "username": username,
                "name": ""
            }
        else:
            username = dbdata[0]['username']
            profile = {
                "username": username,
                "name": dbdata[0].get('name', '')
            }
        
        # Get top 3 habits (same logic as top3habits endpoint)
        from datetime import datetime, timedelta
        five_days_ago = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        
        # Get all user's habits
        query = "SELECT * FROM habit WHERE username = ? AND deleted_at IS NULL"
        params = (username,)
        user_habits = af_getdb(dbloc, query, params)
        
        # Also get habits where user is a member
        query = """SELECT habit.* FROM habit 
                   INNER JOIN member ON habit.id = member.habitid 
                   WHERE member.member = ? AND member.deleted_at IS NULL"""
        params = (username,)
        member_habits = af_getdb(dbloc, query, params)
        
        # Combine both lists
        all_habits = user_habits + member_habits
        
        # For each habit, count check-ins in last 5 days
        habit_counts = []
        for habit in all_habits:
            habitid = habit['id']
            
            # Count positive check-ins (historystatus = 1) in last 5 days for this user
            query = """SELECT COUNT(*) as count FROM history 
                       WHERE habitid = ? AND username = ? 
                       AND historydate >= ? 
                       AND historystatus = '1'
                       AND deleted_at IS NULL"""
            params = (habitid, username, five_days_ago)
            count_result = af_getdb(dbloc, query, params)
            
            count = count_result[0]['count'] if count_result else 0
            
            habit_counts.append({
                'id': habit['id'],
                'name': habit['name'],
                'url': habit['url'],
                'count': count
            })
        
        # Sort by count descending and get top 3
        habit_counts.sort(key=lambda x: x['count'], reverse=True)
        top3 = habit_counts[:3]
        
        return jsonify({
            "status": "ok",
            "message": "profile with top 3 habits",
            "profile": profile,
            "top3habits": top3
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Your token has expired"
        })
 

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