#apps/controllers/takedata.py
import time
from flask import jsonify, request, Blueprint, render_template, render_template_string
from ..utils.html_helper import *
import threading

takedata_blueprint = Blueprint('takedata', __name__)

@takedata_blueprint.route("/takedata")
def takedata():
    data = af_requestget("data")
    threading.Thread(target=write_to_sheet, args=(data,)).start()
    return jsonify({"status": "queued", "data": data})

def write_to_sheet(data, retries=3, delay=2):
    for attempt in range(1, retries + 1):
        try:
            time.sleep(5) #here upload data
            print(f"✅ Data written successfully: {data}")
            return
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                print(f"❌ Failed after {retries} attempts. Data lost: {data}")