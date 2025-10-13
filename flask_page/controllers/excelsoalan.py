#apps/controllers/excelsoalan.py
import time
from flask import jsonify, request, Blueprint, render_template, render_template_string
import requests
from ..utils.html_helper import *
import threading

excelsoalan_blueprint = Blueprint('excelsoalan', __name__)

@excelsoalan_blueprint.route("/excelsoalan")
def excelsoalan():
    data = af_requestpostfromjson("data")

    #test here
    write_to_sheet(data, data.excelname)
    
    threading.Thread(
        target=write_to_sheet, args=(data, )
    ).start()
    return jsonify({"status": "queued", "data": data})

def write_to_sheet(data, excelname, retries=3, delay=2):
    for attempt in range(1, retries + 1):
        try:
            excelname = data.excelname
            link = ""
            if (excelname == "testPostData"):
                link = "https://script.google.com/macros/s/AKfycbzinbTaU4Jg-VOWdVfM5APzlHsqIGvpDofiXQMgVruLUWsZjnV0f1aXcdhdeTFbsSmQ/exec"

            r = requests.post(link, json=data)
            r.raise_for_status()
            return r.json()
            
            print(f"✅ Data written successfully: {data}")
            return
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                print(f"❌ Failed after {retries} attempts. Data lost: {data}")