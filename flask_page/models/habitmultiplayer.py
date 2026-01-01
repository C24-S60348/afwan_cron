#models/habitmultiplayer.py

from flask import request
from ..utils.html_helper import *
from datetime import datetime

habitcsv = "static/db/habit/habit.csv"
notescsv  = "static/db/habit/notes.csv"
playerscsv = "static/db/habit/players.csv"

def getpostget(name="habitid"):
    if request.method == 'POST':
        return af_requestpostfromjson(name, "")
    
    else:
        return af_requestget(name, "")
