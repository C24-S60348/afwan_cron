#controllers/celiktafsir.py

from flask import abort, jsonify, request, Blueprint, render_template, render_template_string, session

from ..utils.html_helper import *
from ..utils.checker_helper import *
from ..utils.db_helper import *

import requests
from bs4 import BeautifulSoup
from datetime import datetime

dbloc = "static/db/celiktafsir.db"

restrictmode = True
celiktafsir_blueprint = Blueprint('celiktafsir', __name__, url_prefix="/api/celiktafsir")
    
@celiktafsir_blueprint.route('/test', methods=['GET', 'POST'])
def test():
    return render_template("main.html")

@celiktafsir_blueprint.route('/', methods=['GET', 'POST'])
def main():
    query = "SELECT * FROM settings;"
    params = ()
    data = af_getdb(dbloc, query, params)

    return jsonify(data)

@celiktafsir_blueprint.route('/checkver', methods=['GET', 'POST'])
def checkver():

    #settings -> id,name,value,desc,link,message

    version = getpostget("version")
    name = getpostget("name")

    if inputnotvalidated(version):
        return jsonifynotvalid("version")
    if inputnotvalidated(name):
        return jsonifynotvalid("name")

    query = "SELECT * FROM settings WHERE CAST(value AS REAL) > ? AND name = ?;"
    params = (version, name,)
    data = af_getdb(dbloc, query, params)
    type = "pass"
    message = ""
    link = ""
    if data :
        message = data[0]['message']
        link = data[0]['link']


    return jsonify({"status": "ok",
                   "data": data,
                   "type": type,
                   "message": message,
                   "link": link
                   })


@celiktafsir_blueprint.route('/fetcher', methods=['GET', 'POST'])
def fetcher():

    #html -> id,name,plain_html,surah,created_at

    url = 'https://www.google.com/'
    response = requests.get(url)
    title = ""
    plain_html = ""
    link1 = ""

    if response.status_code == 200:

        print(response.text)
        
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('title').text
        print(f'Title of the page: {title}')

        for link in soup.find_all('a'):
            print(link.get('href'))

        link1 = soup.find('a').text

        html = response.text
        plain_html = soup.get_text()
        
        query = "INSERT INTO html (name,plain_html,surah,created_at) VALUES (?,?,?,?);"
        params = (title,plain_html,link1,datetime.now())
        data = af_getdb(dbloc, query, params)
    else:
        print(f'Failed to fetch the page. Status code: {response.status_code}')

    
    output = {
        "status": "ok",
        "message": "uploaded",
        "name": title,
        "plain_html": plain_html,
        "link": link1,
        "created_at": datetime.now() 
    }

    return jsonify(output)