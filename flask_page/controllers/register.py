#controllers/register.py

from flask import abort, jsonify, request, Blueprint, render_template, render_template_string, session
from ..utils.adminhandle_helper import *
from ..utils.html_helper import *
from ..utils.excel_helper import *
from ..models.register import *

users = modeluser()

register_blueprint = Blueprint('register', __name__)

@register_blueprint.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        passwordrepeat = request.form['passwordrepeat']
        passwordadmin = request.form['passwordadmin']
        
        #check username 
        message = modelregister(username, password, passwordrepeat, passwordadmin)

        flash(message)
        if message == "Successfully registered, now please login":
            return redirect(url_for('login.login'))
        else:
            return redirect(url_for('register.register'))
        
    return render_template('register/register.html')

@register_blueprint.route('/api/register', methods=['GET', 'POST'])
def registerapi():

    if request.method == 'POST':
        username = af_requestpostfromjson("username")
        password = af_requestpostfromjson("password")
        passwordrepeat = af_requestpostfromjson("passwordrepeat")
        passwordadmin = af_requestpostfromjson("passwordadmin")
    
    elif request.method == 'GET':
        username = af_requestget("username")
        password = af_requestget("password")
        passwordrepeat = af_requestget("passwordrepeat")
        passwordadmin = af_requestget("passwordadmin")

    message = modelregister(username, password, passwordrepeat, passwordadmin)
    if message == "Successfully registered, now please login":
        return jsonify({"status":"ok", "result":message})
    else:
        return jsonify({"status":"error", "result":message})