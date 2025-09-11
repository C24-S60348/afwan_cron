#sudo nano /etc/systemd/system/quartapp.service

#this server folder is at afwan_server

#edit then
'''
To Restart server:

sudo systemctl daemon-reload
sudo systemctl restart quartapp
sudo systemctl status quartapp
sudo systemctl enable quartapp
'''

from quart import Quart, request, jsonify, render_template, render_template_string, Response
from quart_cors import cors

from afwan_server_page.home import home_bp
from afwan_server_page.proxy import proxy_bp
from afwan_server_page.database_connection import database_connection_bp

import requests
import asyncpg
import os
import datetime
import json
import variables
import traceback
import httpx  # async HTTP client
from functools import wraps

app = Quart(__name__)
app = cors(app, allow_origin="*")
app.register_blueprint(home_bp)
app.register_blueprint(proxy_bp, url_prefix="/proxy")
app.register_blueprint(database_connection_bp, url_prefix="/database_connection")



if __name__ == "__main__":
    app.run()