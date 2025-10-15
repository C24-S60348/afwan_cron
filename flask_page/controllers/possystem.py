#apps/controllers/possystem.py
import random
from flask import jsonify, request, Blueprint, render_template, render_template_string
from datetime import datetime
from ..utils.adminhandle_helper import *
from ..utils.html_helper import *
from ..utils.excel_helper import *
from ..utils.checker_helper import *
from ..utils.csv_helper import *


possystem_blueprint = Blueprint('possystem', __name__)

@possystem_blueprint.route("/possystem")
def possystem():
    html = ""
    html += "calculator"
    html += "API call"


    return render_template("main.html", title="possystem", html=html)

@possystem_blueprint.route("/api/possystem_calculator", methods=["GET", "POST"])
def possystem_calculator():
    
    total = 0
    estimatedtime = 0
    inq = af_requestpostfromjson("inq") #item and quantity
    name = af_requestpostfromjson("name") 
    printremarktokitchen = af_requestpostfromjson("printremarktokitchen") 
    # print(inq)
    for i in inq:
        item = i['item']
        price = i['price']
        quantity = i['quantity']
        etime = i['etime']
        total += (float(price) * float(quantity))
        estimatedtime += float(etime)
        # print(item)
        # print (quantity)
    
    gst = total * 6/100
    gst = round(gst, 2)

    total = round(total,2)
    remark = ""

    if printremarktokitchen == "":
        printremarktokitchen = "no"
    idorder = random.randint(100000, 999999) #need to be on DB's ID
    
    #Example
    """
    {
        "name": "afwan",
        "printremarktokitchen": "yes",
        "inq": [
            {
                "item" : "aa",
                "price" : 5.55,
                "quantity" : 2,
                "etime": 5
            },
            {
                "item" : "ikan",
                "price" : 6.55,
                "quantity" : 12,
                "etime": 5
            }

        ]
    }
    """
    
    return jsonify(
        {
            "total":f"RM {total}",
            "GST": f"RM {gst}",
            "remark": f"{remark}",
            "printremarktokitchen": f"{printremarktokitchen}",
            "idorder": f"#{idorder}",
            "estimatedtime": f"{estimatedtime} minutes",
            "nameorder": f"{name}"

        
        }
    )

@possystem_blueprint.route("/api/possystem_main", methods=["GET", "POST"])
def possystem_main():
    
    jsonitems = [
        {
            "item" : "air barli", 
            "type" : "air",
            "price" : "3.50"
        },
        {
            "item" : "air suam", 
            "type" : "air",
            "price" : "0.50"
        }
    ]
    
    
    
    return jsonify(
        {
            "items" : jsonitems
            
        
        }
    )