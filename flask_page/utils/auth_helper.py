#utils/auth_helper.py

from .csv_helper import *
import hashlib

file_path = "static/db/users.csv"
def modelgetuserspath():
    return file_path

def hash_password_sha256(password):
    # Create a SHA-256 hash of the password
    sha_signature = hashlib.sha256(password.encode()).hexdigest()
    return sha_signature

def modeluser():
    return af_getcsvdict(file_path)

def modelgetusernamebytoken(token=""):
    username = ""
    users = modeluser()
    for u in users:
        if token == u['token']:
            username = u['username']
            return username

    return username

def modelchecktoken(token=""):
    if token != None and token != "":
        users = modeluser()
        for u in users:
            if token == u['token']:
                return True
    
    return False

def modelgettokenbyusername(username=""):
    token = ""
    users = modeluser()
    for u in users:
        if username == u['username']:
            token = u['token']
            return token

    return token

def modelchecktokenwithusername(token="", username=""):
    users = modeluser()
    for u in users:
        if token == u['token']:
            if username == u['username']:
                return True
    
    return False