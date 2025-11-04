#models/habitmultiplayer.py

from flask import request
from ..utils.crud_helper import *
from ..utils.html_helper import *
from ..utils.csv_helper import *
from datetime import datetime

habitcsv = "static/db/habit/habit.csv"
notescsv  = "static/db/habit/notes.csv"
playerscsv = "static/db/habit/players.csv"

def getpostget(name="habitid"):
    if request.method == 'POST':
        return af_requestpostfromjson(name, "")
    
    else:
        return af_requestget(name, "")
    
    
# def createhabit(data={}):
    
#     data['csv'] = habitcsv
#     result = create(data)

#     return result


# def readonehabit(data={}):
#     targetname = data['targetname'] #"id"
#     targetdata = data['targetdata'] #"4"
#     datacsv = af_getcsvdict(habitcsv)
#     for d in datacsv:
#         if d[targetname] == targetdata:
#             if d["deleted_at"] == "":
#                 return d 
#     return []

# def readhabit():
#     result = []
#     datacsv = af_getcsvdict(habitcsv)
#     for d in datacsv:
#         if d["deleted_at"] == "":
#             result.append(d)
#     return result

# def updatehabit(data={}):
#     targetname = data['targetname'] #"id"
#     targetdata = data['targetdata'] #"4"

#     newname = data['newname'] #"name"
#     newdata = data['newdata'] #"afwan"
#     new_data = {newname:newdata}

#     af_replacecsv2(habitcsv, targetname, targetdata, new_data)   

# def deletehabit(data={}):
#     targetcolumn = data['targetcolumn'] #"id"
#     targetdata = data['targetdata'] #"4"
#     datacsv = af_getcsvdict(habitcsv)
#     for d in datacsv:
#         if d[targetcolumn] == targetdata:
#             deleted_at = datetime.now()
#             d['deleted_at'] = deleted_at
#             new_data = {"deleted_at": deleted_at}
#             af_replacecsv2(habitcsv, targetcolumn, targetdata, new_data)
#             return d