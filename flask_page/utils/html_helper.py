#apps/utils/html_helper.py
from flask import redirect, request, url_for


def af_htmlcard(cards=None):
    if cards == None:
        cards = af_htmlcards()
    html = """
    <div class="d-flex align-center justify-content-center my-4">
        """+cards+"""
    </div>
    """
    return html
    # html += af_htmlcard(cards)

def af_htmlcards(href="/pms2", imgsrc="/static/images/pms.png", text="Manufacturing Execution System (MES) Design 2"):
    html = f"""
        <div class="card mx-1">
            <a href="{href}" style="text-decoration: none; color: inherit;">
                <img src="{imgsrc}" class="card-img-top" alt="{text}">
                <div class="card-body">
                    <p class="card-text">{text}</p>
                </div>
            </a>
        </div>
    """
    return html
    # cards += af_htmlcards("/tanam", "/static/images/pms.png", "Tanam")

def af_javascriptchangedropdown(id="style", link="/eqi/qa"):
    html = """
    document.getElementById('"""+id+"""').addEventListener('change', function() {
        // Get selected value
        var styleValue = this.value;
        // Redirect to the desired URL
        window.location.href = '"""+link+"""?"""+id+"""=' + styleValue;
    });
    """
    return html    

def af_htmlcardsuserside50(href="/pms2", imgsrc="/static/images/pms.png", text="Manufacturing Execution System (MES) Design 2"):
    html = f"""
        <div class="card mx-1 w-50">
            <a href="{href}" style="text-decoration: none; color: inherit;display:flex;">
                <img src="{imgsrc}" style="height:140px;width:auto;border-bottom-left-radius: 4px;" class="card-img-top" alt="{text}">
                <div class="card-body">
                    <p class="card-text">{text}</p>
                </div>
            </a>
        </div>
    """
    return html

def af_htmlcardsuserside50center(href="/pms2", imgsrc="/static/images/pms.png", text="Manufacturing Execution System (MES) Design 2"):
    html = f"""
        <div class="card mx-1 w-50">
            <a href="{href}" style="text-decoration: none; color: inherit;text-align:center;">
                <img src="{imgsrc}" style="height:140px;width:auto;border-radius: 4px;" class="card-img-top" alt="{text}">
                <div class="card-body">
                    <p class="card-text">{text}</p>
                </div>
            </a>
        </div>
    """
    return html

def af_htmlcardsuserside50centerfixed(href="/pms2", imgsrc="/static/images/pms.png", text="Manufacturing Execution System (MES) Design 2", width="200px"):
    html = f"""
        <div class="card mx-1" style="width:{width};">
            <a href="{href}" style="text-decoration: none; color: inherit;text-align:center;">
                <img src="{imgsrc}" style="height:140px;width:auto;border-radius: 4px;" class="card-img-top" alt="{text}">
                <div class="card-body">
                    <p class="card-text">{text}</p>
                </div>
            </a>
        </div>
    """
    return html

def af_htmltitle(text="Title"):
    html = f'<div class="title"><h1 class="text-center py-2 my-4">{text}</h1></div>'
    return html
    # html += af_htmltitle("Title")

def af_requestget(code="ikan", default=""):
    return request.args.get(code, default)
    
def af_requestpost(code="ikan", default=""):
    return request.form.get(code, default)

def af_requestpostfromjson(code="ikan", default=""):
    requestpost = request.json
    return requestpost.get(code, default)

def af_htmlselectoption(value="1", name="First option", selected=""):
    selectedDIV = ""
    if selected != "":
        selectedDIV = "selected"
    html = f"""
        <option value="{value}" {selectedDIV}>{name}</option>
    """
    return html

def af_htmlselectoptionempty():
    html = "<option></option>"
    return html

def af_htmlselect(id="mat", name="Material", options=af_htmlselectoptionempty()):
    html = f"""
    <div>
        <div>{name}:</div>
        <select id="{id}" name="{id}">
           {options}
        </select>
    </div>"""
    return html

def af_htmltextinput(name="ikan", id="ik", placeholder="Put ikan here"):
    html = f"""
        <div>
            <div>{name}</div>
            <input type="text" class="form-control" id="{id}" name="{id}" placeholder="{placeholder}">
        </div>"""
    return html

def af_htmlbutton(name="", typecolor="primary", onclick=""):
    classbtn = ""
    if name == "Back":
        onclick = "window.history.back(); return false;"
    
    if typecolor == "primary":
        classbtn = "btn-primary"
    else:
        classbtn = "btn-secondary"
        
    html = f"""
        <button class="btn {classbtn}" onclick="{onclick}">
            {name}
        </button>
    """
    return html

def af_htmlbuttonlink(name="", typecolor="primary", href=""):
    classbtn = ""
    classbtn = "btn-"+typecolor
        
    html = f"""
        <a href="{href}" class="btn {classbtn}">
            {name}
        </a>
    """
    return html

def af_htmlformsubmitbutton():
    html = """<button type="submit" class="btn btn-primary">Submit</button>"""
    return html

def af_htmlformstart(link="tanam_add/submit"):
    html = f"<form action='{link}' method='POST'>"
    return html

def af_htmlformend():
    html = "</form>"
    return html

def af_htmlformend2():
    html = ""
    html += af_htmlformsubmitbutton()
    html += "</form>"
    return html

def af_redirect(link="flangehandle.flangehandle"):
    return redirect(url_for(link))

def getpostget(name="habitid"):
    if request.method == 'POST':
        return af_requestpostfromjson(name, "")
    
    else:
        return af_requestget(name, "")