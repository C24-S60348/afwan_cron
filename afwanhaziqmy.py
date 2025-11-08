#sudo nano /etc/systemd/system/afwanapp.service

"""
source venv/bin/activate

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable afwanapp
sudo systemctl start afwanapp
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_page.utils.csv_helper import *
from datetime import datetime
import os
import secrets
import httpx
import variables
import traceback


app = Flask(
    __name__, 
    template_folder=os.path.join('flask_page', 'templates')
    )

# Generate a secure secret key if not set in environment
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    secret_key = secrets.token_hex(32)  # Generate a 64-character hex string
    print(f"Warning: No SECRET_KEY environment variable set. Generated temporary key: {secret_key}")
    print("Set SECRET_KEY environment variable for production use.")

app.secret_key = secret_key

# CORS configuration to allow all origins
CORS(app, supports_credentials=True,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"]
)

@app.errorhandler(Exception)
def handle_exception(e):

    errorname = str(e)
    type = e.__class__.__name__
    datetimeget = str(datetime.now())
    url = request.url
    method = request.method
    # headers = request.headers
    data = None

    # Safely try to get JSON body, if it exists
    try:
        data = request.get_json()
    except:
        pass

    if method == "POST":
        data = request.form.to_dict()

    errormessage = f"""Have error on {url}.
    message: {errorname}
    type: {type}
    traceback: {traceback.format_exc()}
    """

    send_telegram_error(errormessage)

    #If url not found, dont log
    if type != "NotFound":
        new_data = [
            type,
            errorname,
            datetimeget,
            url,
            method,
            # str(headers),
            str(data)
        ]
        #log here
        af_addcsv("static/db/error/error.csv", new_data)
    
    return jsonify({
        "status" : "error",
        "message": errorname,
        "type": type
    })


def send_telegram_error(error_message):
    try:
        bot_token = variables.tb_token_server
        chat_id = "-1002864663247"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": f"🚨 ERROR ALERT 🚨\n\n{error_message}",
            "parse_mode": "HTML"
        }

        with httpx.Client() as client:
            response = client.post(url, data=data)

        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

from flask_page.controllers.apitest import apitest_bp
from flask_page.controllers.connect_to_db import connect_to_db
from flask_page.controllers.api_bp import api_bp
from flask_page.controllers.home import home_bp
from flask_page.controllers.croncheck import croncheck_bp
from flask_page.controllers.executejsonv2 import executejsonv2_bp
from flask_page.controllers.pelajar_data import pelajar_data_bp
from flask_page.controllers.admin import admin_bp
from flask_page.controllers.ularular import ularular_bp, ularular_init_db
from flask_page.controllers.ularulargame import ularulargame_bp
from flask_page.controllers.ularulargame2 import ularulargame2_bp
from flask_page.controllers.postman import postman_bp
from flask_page.controllers.bbcode import bbcode_bp
from flask_page.controllers.quiz import quiz_blueprint
from flask_page.controllers.quiz2 import quiz2_blueprint
from flask_page.controllers.takedata import takedata_blueprint
from flask_page.controllers.purgo import purgo_bp
from flask_page.controllers.tanam import tanam_blueprint
from flask_page.controllers.excelsoalan import excelsoalan_blueprint
from flask_page.controllers.login import login_blueprint
from flask_page.controllers.register import register_blueprint
from flask_page.controllers.possystem import possystem_blueprint
from flask_page.controllers.ular import ular_blueprint
from flask_page.controllers.ularquestions import ularq_blueprint
from flask_page.controllers.habitmultiplayer import habitmultiplayer_blueprint

# from flask_page.controllers.publicvar import last_run_timesitest_bp)
app.register_blueprint(apitest_bp)
app.register_blueprint(api_bp)
app.register_blueprint(home_bp)
app.register_blueprint(croncheck_bp)
app.register_blueprint(executejsonv2_bp)
app.register_blueprint(pelajar_data_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(ularular_bp)
app.register_blueprint(ularulargame_bp)
app.register_blueprint(ularulargame2_bp)
app.register_blueprint(postman_bp)
app.register_blueprint(bbcode_bp)
app.register_blueprint(quiz_blueprint)
app.register_blueprint(quiz2_blueprint)
app.register_blueprint(takedata_blueprint)
app.register_blueprint(purgo_bp)
app.register_blueprint(tanam_blueprint)
app.register_blueprint(excelsoalan_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(register_blueprint)
app.register_blueprint(possystem_blueprint)
app.register_blueprint(ular_blueprint)
app.register_blueprint(ularq_blueprint)
app.register_blueprint(habitmultiplayer_blueprint)

with app.app_context():
    ularular_init_db()  # ✅ Auto-create tables if not found

# Start the app using Uvicorn
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)