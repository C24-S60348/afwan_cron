#apps/utils/checker_helper.py
import os

from flask import jsonify


def af_image_exists(image_path="static/images/employees/afwan.png"):
    # Check if the file exists and is a file (not a directory)
    return os.path.isfile(image_path)

def inputnotvalidated(input=""):
    if input == "" or input == None:
        return True
    return False

def jsonifynotvalid(input=""):
    return jsonify({
        "status": "error",
        "message": f"{input} is not valid"
    })