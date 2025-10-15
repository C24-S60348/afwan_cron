#models/login.py

import secrets
from ..utils.csv_helper import *
from ..utils.auth_helper import *

def modelchecktokenwebsite(session):
    if modelchecktoken(session.get('token')):
        return True
    return False

def modelputtokenandgettoken(username=""):
    token = generate_token()
    return modelupdatetoken(username, token)

def modelgettoken(username=""):
    return modelgettokenbyusername(username)

def modelgettokenbasedonkeeptoken(username="", keeptoken=""):
    token = ""
    if keeptoken == "yes":
        tokenget = modelgettoken(username)
        if (tokenget == "" or tokenget == None):
            token = modelputtokenandgettoken(username)
        else:
            token = modelgettoken(username)
    else:
        token = modelputtokenandgettoken(username)
    return token

def modellogout(token=""):
    new_data = {"token": ""}

    # Update the user's row with the new token
    if af_replacecsv_withtoken(file_path, token, new_data):
        print(f"Successfully logged out. {token}")
        token = ""
        return token
    else:
        print(f"Failed to update the token. {token}")
        return False

def modellogoutremovetoken(username=""):
    token = ""
    return modelupdatetoken(username, token)

def modelupdatetoken(username, token):
    new_data = {"token": token}

    # Update the user's row with the new token
    if af_replacecsv(file_path, username, new_data):
        print(f"Successfully updated the token for {username}. {token}")
        return token
    else:
        print(f"Failed to update the token for {username}. {token}")
        return False

def modellogin(username="", password=""):
    users = modeluser()
    for u in users:
        if username == u['username']:
            if password == u['password']:
                return True
    
    return False


def modelloginhash(username="", password=""):
    users = modeluser()
    for u in users:
        if username == u['username']:
            print (hash_password_sha256(password))
            if hash_password_sha256(password) == u['password']:
                return True
    
    return False

def generate_token():
    return secrets.token_hex(16)