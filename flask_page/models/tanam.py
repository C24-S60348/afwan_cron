#apps/models/tanam.py
from ..utils.csv_helper import af_getcsvdict
from ..utils.html_helper import *

def gettanamcsv():
    return af_getcsvdict("static/db/tanam.csv")

def modeltanamgetcards():
    result = gettanamcsv()
    html = ""
    cards = ""
    count = 0
    for r in result:
        #r["imgsrc"]
        cards += "<div class='mx-2' style='text-align:center;display: flex;flex-direction: column;justify-content: space-between;'>"
        cards += af_htmlcards("/tanam_desc?pokok="+r["nameid"], r["imgsrc"], r["name"])

        cards += "<div>"
        cards += "<div>Kesukaran</div>"
        cards += af_htmlbuttonlink("Mudah", "primary", "#")
        cards += af_htmlbuttonlink("Sederhana", "secondary", "#")
        cards += af_htmlbuttonlink("Belajar", "warning", "#")
        cards += "</div>"
        cards += "</div>"

        count+=1
        if (count % 3 == 0):
            html += af_htmlcard(cards)
            cards = ""

    return html

def modelpilihanslides():
    html = ""
    html += """

    <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        width: 80%;
        margin: 0 auto;
    ">
        <button onclick="slideLeft()" style="margin-right: 10px;"> < </button>
        <div id="carousel" style="
            display: flex;
            overflow: hidden;
            width: 360px; 
        ">
            <div class="card-container" style="
                display: flex;
                transition: transform 0.5s ease-in-out;
            ">
                """ + modeltanamgetcards() + """
            </div>
        </div>
        <button onclick="slideRight()" style="margin-left: 10px;"> > </button>
    </div>
    """
    return html

def modeldesc(pokok="pokok"):
    html = ""
    cards = ""
    htmlbawah = ""
    result = gettanamcsv()
    for r in result:
        if r["nameid"] == pokok:
            cards += af_htmlcards("/tanam_desc?pokok="+r["nameid"], r["imgsrc"], r["name"])
            htmlbawah += "<p style='color:white;'>Desc: " + r["desc"] + "</p>"
            htmlbawah += "<p style='color:white;'>Soil: " + r["soil"] + "</p>"
            htmlbawah += "<p style='color:white;'>sunlight: " + r["sunlight"] + "</p>"
            htmlbawah += "<p style='color:white;'>water: " + r["water"] + "</p>"
            htmlbawah += "<p style='color:white;'>harvest: " + r["harvest"] + "</p>"
    
    html += af_htmlcard(cards)
    html += htmlbawah
    return html

def modelmula(pokok="pokok"):
    html = ""
    cards = ""
    htmlatas = ""
    htmlbawah = ""
    result = gettanamcsv()
    for r in result:
        if r["nameid"] == pokok:
            htmlatas = "<img src='/static/images/tanam/matahari.png' style='height: 40px; width: 40px;' />"
            cards += af_htmlcards("/tanam_desc?pokok="+r["nameid"], r["imgsrc"], r["name"])
            htmlbawah += "<div style='text-align:center;'>"
            htmlbawah += af_htmlbutton("Siram Air 💧", "primary", "siram();")
            htmlbawah += af_htmlbutton("Letak Baja 🌾", "primary", "baja();")
            htmlbawah += af_htmlbutton("Cahaya ☀️", "primary", "cahaya();")
            htmlbawah += "</div>"
    
    html += htmlatas
    html += af_htmlcard(cards)
    html += htmlbawah
    return html