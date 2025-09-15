#sudo nano /etc/systemd/system/afwanapp.service

#sudo systemctl daemon-reexec
#sudo systemctl daemon-reload
#sudo systemctl enable afwanapp
#sudo systemctl start afwanapp

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# CORS configuration to allow all origins
CORS(app, supports_credentials=True,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"]
)

from flask_page.apitest import apitest_bp
from flask_page.connect_to_db import connect_to_db
from flask_page.api_bp import api_bp
from flask_page.home import home_bp
from flask_page.croncheck import croncheck_bp
from flask_page.executejsonv2 import executejsonv2_bp
from flask_page.pelajar_data import pelajar_data_bp
from flask_page.admin import admin_bp
from flask_page.ularular import ularular_bp, ularular_init_db, ularular_get_db
from flask_page.postman import postman_bp


# from flask_page.publicvar import last_run_timesitest_bp)
app.register_blueprint(apitest_bp)
app.register_blueprint(api_bp)
app.register_blueprint(home_bp)
app.register_blueprint(croncheck_bp)
app.register_blueprint(executejsonv2_bp)
app.register_blueprint(pelajar_data_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(ularular_bp)
app.register_blueprint(postman_bp)

with app.app_context():
    ularular_init_db()  # ✅ Auto-create tables if not found


# Start the app using Uvicorn
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)