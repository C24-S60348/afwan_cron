#sudo nano /etc/systemd/system/afwanapp.service

"""
source venv/bin/activate

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable afwanapp
sudo systemctl start afwanapp
"""

from flask import Flask
from flask_cors import CORS
import os
import secrets

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

with app.app_context():
    ularular_init_db()  # ✅ Auto-create tables if not found

# Start the app using Uvicorn
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)