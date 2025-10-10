#sudo nano /etc/systemd/system/afwanapp.service

#sudo systemctl daemon-reexec
#sudo systemctl daemon-reload
#sudo systemctl enable afwanapp
#sudo systemctl start afwanapp

from flask import Flask
from flask_cors import CORS
import os

app = Flask(
    __name__, 
    template_folder=os.path.join('flask_page', 'templates')
    )

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
from flask_page.controllers.ularular import ularular_bp, ularular_init_db, ularular_get_db
from flask_page.controllers.ularulargame import ularulargame_bp
from flask_page.controllers.ularulargame2 import ularulargame2_bp
from flask_page.controllers.postman import postman_bp
from flask_page.controllers.bbcode import bbcode_bp
from flask_page.controllers.quiz import quiz_blueprint
from flask_page.controllers.quiz2 import quiz2_blueprint
from flask_page.controllers.takedata import takedata_blueprint
from flask_page.controllers.purgo import purgo_bp
from flask_page.controllers.tanam import tanam_blueprint

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

with app.app_context():
    ularular_init_db()  # ✅ Auto-create tables if not found


# Start the app using Uvicorn
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)