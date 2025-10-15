#controllers/login.py

from flask import abort, jsonify, request, Blueprint, render_template, render_template_string, session
from ..utils.adminhandle_helper import *
from ..utils.html_helper import *
from ..utils.excel_helper import *
from ..models.login import *

users = modeluser()

login_blueprint = Blueprint('login', __name__)

@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():

    #check already have session
    token = session.get('token')
    if modelchecktoken(token):
        username = modelgetusernamebytoken(token)
        return render_template('login/logout.html', username=username)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        keeptoken = ""
        
        # Authenticate user
        print (users)
        if modelloginhash(username, password):
            session['token'] = modelgettokenbasedonkeeptoken(username, keeptoken)
            session['username'] = username
            return redirect(url_for('login.login'))
        else:
            flash("Wrong username or password")
            return redirect(url_for('login.login'))
        
    return render_template('login/login.html')

@login_blueprint.route('/protected')
def protected():
    token = session.get('token')
    if modelchecktoken(token):
        return "You are logged in!"
    return redirect(url_for('login.login'))

@login_blueprint.route('/logout')
def logout():
    token = session.get('token')
    modellogout(token)
    session.pop('token', None)

    flash("You have logged out")
    return redirect(url_for('login.login'))

@login_blueprint.route('/api/login', methods=['GET', 'POST'])
def loginapi():

    if request.method == 'POST':
        username = af_requestpostfromjson("username")
        password = af_requestpostfromjson("password")
        keeptoken = af_requestpostfromjson("keeptoken")
    
    else:
        username = af_requestget("username")
        password = af_requestget("password")
        keeptoken = af_requestget("keeptoken")
        
    
    if username == "" and password == "":
        return jsonify({"status":"ok", "result":"please enter login details"})
    
    # Authenticate user
    print (users)
    if modelloginhash(username, password):
        result = {}
        result['token'] = modelgettokenbasedonkeeptoken(username, keeptoken)
        result['username'] = username
        return jsonify({"status":"ok", "result":result})
    else:
        return jsonify({"status":"error", "result":"Wrong username or password"})

@login_blueprint.route('/api/logout')
def logoutapi():
    if request.method == 'POST':
        token = af_requestpostfromjson("token")
    
    elif request.method == 'GET':
        token = af_requestget("token")
    
    if modellogout(token) == "":
        return jsonify({"status":"ok", "result":f"Logged out"})
    else:
        return jsonify({"status":"error", "result":f"No user with token {token}"})