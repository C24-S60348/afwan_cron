#models/register.py
from ..utils.auth_helper import *

def modelregister(username= "", password = "", passwordrepeat = "", passwordadmin=""):
    if passwordadmin == "afwan":
        
        if password == passwordrepeat:
            
            if modelgetusernameisexist(username):
                return "The username is already exist!"
            else:
                #register user
                modelregisteruser(username, password)
                return "Successfully registered, now please login"
            
        else:
            return "Password is not same with Repeat password!"
        
    return "Wrong Password Admin!"

def modelregisteruser(username="", password=""):
    af_addcsv(modelgetuserspath(), [
        username,
        hash_password_sha256(password)
    ])

def modelgetusernameisexist(username=""):

    users = modeluser()

    for u in users:
        if username == u['username']:
            return True
        
    return False