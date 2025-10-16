import time
from flask import jsonify, request, Blueprint
import requests
from ..utils.html_helper import *
import threading

excelsoalan_blueprint = Blueprint('excelsoalan', __name__)

#excelsoalansubmit
@excelsoalan_blueprint.route("/api/excelsoalan", methods=["POST"])
def excelsoalan():
    data = af_requestpostfromjson("data")
    if not data or not isinstance(data, dict):
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    # Queue writing to sheet in a background thread only
    threading.Thread(
        target=write_to_sheet, args=(data, )
    ).start()
    if data.get("excelname", "") != "":
        return jsonify({"status": "success", "message": "Data queued for writing"}), 200
    else:
        return jsonify({"status": "error", "message": "No destination link for excelname"}), 400
    # return jsonify({"status": "queued", "data": data})

def write_to_sheet(data, retries=3, delay=2):
    for attempt in range(1, retries + 1):
        try:
            excelname = data.get("excelname", "")
            link = ""
            if excelname == "testPostData":
                link = "https://script.google.com/macros/s/AKfycbzinbTaU4Jg-VOWdVfM5APzlHsqIGvpDofiXQMgVruLUWsZjnV0f1aXcdhdeTFbsSmQ/exec"
            if not link:
                print(f"❌ No destination link for excelname: {excelname}")
                return

            r = requests.post(link, json=data)
            r.raise_for_status()
            print(f"✅ Data written successfully: {data}")
            return
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                print(f"❌ Failed after {retries} attempts. Data lost: {data}")