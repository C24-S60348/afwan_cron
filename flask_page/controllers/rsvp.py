#controllers/rsvp.py

from flask import abort, jsonify, request, Blueprint, render_template, render_template_string, session


from ..utils.crud_helper import *
from ..utils.adminhandle_helper import *
from ..utils.html_helper import *
from ..utils.excel_helper import *
from ..utils.login_helper import *
from ..utils.checker_helper import *

import json

datacsv = "static/db/rsvp/data.csv"

rsvp_blueprint = Blueprint('rsvp', __name__, url_prefix="/api/rsvp")

@rsvp_blueprint.route('', methods=['GET', 'POST'])
def rsvp():
    
    uniquename = getpostget("uniquename")
    print ("aa"+uniquename)

    name1 = ""
    name2 = ""
    name3 = ""
    name4 = ""
    email = ""
    message = ""

    if uniquename != "" and uniquename != None:
        data = {}
        data['csv'] = datacsv
        data['targetname'] = 'uniquename'
        data['targetdata'] = uniquename
        readdata = cread(data)
        # print(readdata)
        mydata = readdata[0]['mydata']
        print(mydata)
        mydata2 = json.loads(mydata)
        name1 = mydata2['name1']
        name2 = mydata2['name2']
        name3 = mydata2['name3']
        name4 = mydata2['name4']
        email = mydata2['email']
        message = mydata2['message']
    
    

    return render_template(
        "rsvp/main.html",
        name1=name1,
        name2=name2,
        name3=name3,
        name4=name4,
        email=email,
        message=message,
        uniquename=uniquename,
          
        )

@rsvp_blueprint.route('/2', methods=['GET', 'POST'])
def rsvp2():
    
    

    return render_template(
        "rsvp/main2.html",

        )
@rsvp_blueprint.route('/3', methods=['GET', 'POST'])
def rsvp3():
    
    

    return render_template(
        "rsvp/main3.html",

        )
@rsvp_blueprint.route('/4', methods=['GET', 'POST'])
def rsvp4():
    
    

    return render_template(
        "rsvp/main4.html",

        )

@rsvp_blueprint.route('/cudrsvp', methods=['GET', 'POST'])
def cudrsvp():
    uniquename = getpostget("uniquename")
    mydata = getpostget("mydata")

    print (uniquename)
    print (mydata)
    
    if inputnotvalidated(uniquename):
        return jsonifynotvalid("uniquename")
    if inputnotvalidated(mydata):
        return jsonifynotvalid("mydata")
    
    data = {}
    data['csv'] = datacsv
    data['targetname'] = "uniquename"
    data['targetdata'] = str(uniquename)
    data['newname'] = "mydata"
    data['newdata'] = str(mydata)

    if mydata == "deletedeletedelete":
        deletedata = cdelete(data)
        return jsonify(
            {
                "status": "ok",
                "message": "rsvp deleted",
                "data": deletedata
            }
        )
    else:
        updateddata = cupdate(data)
        if updateddata:
            readdata = cread(data)
            return jsonify(
                {
                    "status": "ok",
                    "message": "rsvp updated",
                    "data": readdata
                }
            )
        else:
            
            data = {}
            data['csv'] = datacsv
            data['uniquename'] = uniquename
            data['mydata'] = mydata
            data['created_at'] = datetime.now()
            data['deleted_at'] = ""
            createdata = ccreate(data)

            return jsonify(
                {
                    "status": "ok",
                    "message": "rsvp created",
                    "data": createdata
                }
            )