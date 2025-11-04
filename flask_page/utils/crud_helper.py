#utils/crud_helper.py
from ..utils.csv_helper import *
from datetime import datetime

def ccreate(data={}):
    linkcsv = data['csv']
    #and other data including created_at, deleted_at

    idlast = 0
    datacsv = af_getcsvdict(linkcsv)
    for d in datacsv:
        idlast = d["id"]
    
    idadd = int(idlast)
    idadd += 1

    #here --------------
    new_row = [idadd]
    for key, value in data.items():
        if key != "csv":
            new_row.append(value)
    
    af_addcsv(linkcsv, new_row)

    return {
        "id" : idadd,
    }

def cread(data={}):
    linkcsv = data['csv']
    targetname = data['targetname'] #"id"
    targetdata = data['targetdata'] #"4"

    datacsv = af_getcsvdict(linkcsv)
    if targetname == None or targetname == "":
        result = []
        for d in datacsv:
            if d["deleted_at"] == "" or d["deleted_at"] == None or d["deleted_at"] == "null":
                result.append(d)
        return result 
    else:
        result = []
        for d in datacsv:
            if d[targetname] == targetdata:
                if d["deleted_at"] == "" or d["deleted_at"] == None or d["deleted_at"] == "null":
                    result.append(d)
        return result
    
def cread2(data={}):
    linkcsv = data['csv']
    targetname = data['targetname'] #"habitid"
    targetdata = data['targetdata'] #"4"
    targetname2 = data['targetname2'] #"username"
    targetdata2 = data['targetdata2'] #"afwan"

    datacsv = af_getcsvdict(linkcsv)
    if targetname == None or targetname == "":
        result = []
        for d in datacsv:
            if d["deleted_at"] == "" or d["deleted_at"] == None or d["deleted_at"] == "null":
                result.append(d)
        return result 
    else:
        result = []
        for d in datacsv:
            if d[targetname] == targetdata:
                if d[targetname2] == targetdata2:
                    if d["deleted_at"] == "" or d["deleted_at"] == None or d["deleted_at"] == "null":
                        result.append(d)
        return result

def creadboth(data={}):
    linkcsv = data['csv']
    targetname = data['targetname'] #"habitid"
    targetdata = data['targetdata'] #"4"
    targetname2 = data['targetname2'] #"username"
    targetdata2 = data['targetdata2'] #"afwan"

    datacsv = af_getcsvdict(linkcsv)
    if targetname == None or targetname == "":
        result = []
        for d in datacsv:
            if d["deleted_at"] == "" or d["deleted_at"] == None or d["deleted_at"] == "null":
                result.append(d)
        return result 
    else:
        result = []
        for d in datacsv:
            if d[targetname] == targetdata:
                if d["deleted_at"] == "" or d["deleted_at"] == None or d["deleted_at"] == "null":
                    result.append(d)
            elif d[targetname2] == targetdata2:
                if d["deleted_at"] == "" or d["deleted_at"] == None or d["deleted_at"] == "null":
                    result.append(d)
        return result

def cupdate(data={}):
    linkcsv = data['csv']
    targetname = data['targetname'] #"id"
    targetdata = data['targetdata'] #"4"

    
    
    newname = data['newname'] #"name"
    newdata = data['newdata'] #"afwan"
    if newname == None or newname == "":
        return
    if newdata == None or newdata == "":
        return
    
    new_data = {newname:newdata}

    af_replacecsv2(linkcsv, targetname, targetdata, new_data)

def cupdate2(data={}):
    linkcsv = data['csv']
    targetname = data['targetname'] #"habitid"
    targetdata = data['targetdata'] #"4"
    targetname2 = data['targetname2'] #"username"
    targetdata2 = data['targetdata2'] #"afwan"

    
    
    newname = data['newname'] #"name"
    newdata = data['newdata'] #"afwan"
    if newname == None or newname == "":
        return False
    if newdata == None or newdata == "":
        return False
    
    new_data = {newname:newdata}

    result = af_replacecsvtwotarget(linkcsv, targetname, targetdata, targetname2, targetdata2, new_data)
    if result:
        return True
    else:
        return False

def cdelete(data={}):
    linkcsv = data['csv']
    targetname = data['targetname'] #"id"
    targetdata = data['targetdata'] #"4"
    datacsv = af_getcsvdict(linkcsv)
    for d in datacsv:
        if d[targetname] == targetdata:
            deleted_at = datetime.now()
            d['deleted_at'] = deleted_at
            new_data = {"deleted_at": deleted_at}
            af_replacecsv2(linkcsv, targetname, targetdata, new_data)
            return d
    
    return []