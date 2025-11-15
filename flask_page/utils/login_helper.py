#utils/login_helper.py

import secrets
from .csv_helper import *
import hashlib
import re
import string

#login --------------------

def modelupdateprofile(username="", name="", file_path="static/db/users.csv"):
    users = modeluser(file_path)
    for u in users:
        if username == u['username']:
            new_data = { "name": name }
            af_replacecsv(file_path, username, new_data)
            return True
    
    return False

def modelforgottedpassword(username="", file_path="static/db/users.csv"):
    users = modeluser(file_path)
    for u in users:
        if username == u['username']:
            if u['forgotpassword'] == "yes":
                return True
    
    return False

def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def modelsendforgotpasswordemail(email, file_path="static/db/users.csv"):
    newpassword = generate_random_password(12)
    new_data = { "password": hash_password_sha256(newpassword) }
    af_replacecsv(file_path, email, new_data)
    new_data = { "forgotpassword": "yes" }

    # Update the user's row with the new token
    if af_replacecsv(file_path, email, new_data):
        modelsendemail(email, newpassword)
        print(f'password has been changed to {newpassword}')
        return True
    else:
        return False

def modelsendemail(email, newpassword):
    print(f'password has been changed to {newpassword}')
    send_telegram_message(f'password {email} has been changed to {newpassword}')
    #todo - send email brevo
    return True

def modelcheckemail(email="test@test.com"):
    # Regular expression pattern for a general valid email
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    # pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def modelchecktokenwebsite(session, file_path="static/db/users.csv"):
    if modelchecktoken(session.get('token'), file_path):
        return True
    return False

def modelputtokenandgettoken(username="", file_path="static/db/users.csv"):
    token = generate_token()
    return modelupdatetoken(username, token, file_path)

def modelgettoken(username="", file_path="static/db/users.csv"):
    return modelgettokenbyusername(username, file_path)

def modelgettokenbasedonkeeptoken(username="", keeptoken="", file_path="static/db/users.csv"):
    token = ""
    if keeptoken == "yes":
        tokenget = modelgettoken(username, file_path)
        if (tokenget == "" or tokenget == None):
            token = modelputtokenandgettoken(username, file_path)
        else:
            token = modelgettoken(username, file_path)
    else:
        token = modelputtokenandgettoken(username, file_path)
    return token

def modellogout(token="", file_path="static/db/users.csv"):
    new_data = {"token": ""}

    # Update the user's row with the new token
    if af_replacecsv_withtoken(file_path, token, new_data):
        print(f"Successfully logged out. {token}")
        token = ""
        return token
    else:
        print(f"Failed to update the token. {token}")
        return False

def modellogoutremovetoken(username="", file_path="static/db/users.csv"):
    token = ""
    return modelupdatetoken(username, token, file_path)

def modelupdatetoken(username, token, file_path="static/db/users.csv"):
    new_data = {"token": token}

    # Update the user's row with the new token
    if af_replacecsv(file_path, username, new_data):
        print(f"Successfully updated the token for {username}. {token}")
        return token
    else:
        print(f"Failed to update the token for {username}. {token}")
        return False

def modellogin(username="", password="", file_path="static/db/users.csv"):
    users = modeluser(file_path)
    for u in users:
        if username == u['username']:
            if password == u['password']:
                return True
    
    return False


def modelloginhash(username="", password="", file_path="static/db/users.csv"):
    users = modeluser(file_path)
    for u in users:
        if username == u['username']:
            print (hash_password_sha256(password))
            if hash_password_sha256(password) == u['password']:
                return True
    
    return False

def generate_token():
    return secrets.token_hex(16)

#register --------------

def modelregister(username= "", password = "", passwordrepeat = "", passwordadmin="", file_path="static/db/users.csv"):
    if passwordadmin == "afwan":
        
        if password == passwordrepeat:
            
            if modelgetusernameisexist(username, file_path):
                return "The username is already exist!"
            else:
                #register user
                modelregisteruser(username, password, file_path)
                return "Successfully registered, now please login"
            
        else:
            return "Password is not same with Repeat password!"
        
    return "Wrong Password Admin!"

def modelregisteruser(username="", password="", file_path="static/db/users.csv"):
    af_addcsv(modelgetuserspath(file_path), [
        username,
        hash_password_sha256(password),
        "",
        ""
    ])


def modelgetusernameisexist(username="", file_path="static/db/users.csv"):

    users = modeluser(file_path)

    for u in users:
        if username == u['username']:
            return True
    
#helper lagi ----------------------
def modelgetuserspath(file_path="static/db/users.csv"):
    return file_path

def hash_password_sha256(password):
    # Create a SHA-256 hash of the password
    sha_signature = hashlib.sha256(password.encode()).hexdigest()
    return sha_signature

def modeluser(file_path="static/db/users.csv"):
    return af_getcsvdict(file_path)

def modelgetusernamebytoken(token="", file_path="static/db/users.csv"):
    username = ""
    users = modeluser(file_path)
    for u in users:
        if token == u['token']:
            username = u['username']
            return username

    return username

def modelchecktoken(token="", file_path="static/db/users.csv"):
    if token != None and token != "":
        users = modeluser(file_path)
        for u in users:
            if token == u['token']:
                return True
    
    return False

def modelchecktokendata(token="", file_path="static/db/users.csv"):
    if token != None and token != "":
        users = modeluser(file_path)
        for u in users:
            if token == u['token']:
                return u
    
    return False

def modelgettokenbyusername(username="", file_path="static/db/users.csv"):
    token = ""
    users = modeluser(file_path)
    for u in users:
        if username == u['username']:
            token = u['token']
            return token

    return token

def modelchecktokenwithusername(token="", username="", file_path="static/db/users.csv"):
    users = modeluser(file_path)
    for u in users:
        if token == u['token']:
            if username == u['username']:
                return True
    
    return False