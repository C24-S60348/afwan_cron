#controllers/ularquestions.py
from flask import jsonify, request, Blueprint, render_template, render_template_string
from ..utils.html_helper import *
from ..utils.csv_helper import *
from ..models.ular import *

ularq_blueprint = Blueprint('ularq', __name__)

#questions
@ularq_blueprint.route("/api/ular/getquestions")
def apiular_getquestions():
    return jsonify(
        {
            "status": "ok",
            "message": "all questions",
            "result": getquestions()
        }
    )

@ularq_blueprint.route("/api/ular/getquestionslevel")
def apiular_getquestionslevel():
    level = af_requestget("level")
    if inputnotvalidated(level):
        return jsonifynotvalid("level")
    
    return jsonify(
        {
            "status": "ok",
            "message": f"all questions level {level}",
            "result": getquestionslevel(level)
        }
    )

@ularq_blueprint.route("/api/ular/getquestion")
def apiular_getquestion():
    id = af_requestget("id")
    if inputnotvalidated(id):
        return jsonifynotvalid("id")
    
    return jsonify(
        {
            "status": "ok",
            "message": f"question id {id}",
            "result": getquestion(id)
        }
    )


   
@ularq_blueprint.route("/api/ular/getquestionlevel")
def apiular_getquestionlevel():
    level = af_requestget("level")
    if inputnotvalidated(level):
        return jsonifynotvalid("level")
    
    return jsonify(
        {
            "status": "ok",
            "message": f"get random question on level {level}",
            "result": getrandomquestionlevel(level)
        }
    )

# @ularq_blueprint.route("/api/ular/submitanswer")
# def apiular_submitanswer():
#     id = af_requestget("id")
#     answer = af_requestget("answer")

#     if inputnotvalidated(id):
#         return jsonifynotvalid("id")
#     if inputnotvalidated(answer):
#         return jsonifynotvalid("answer")
    
#     submitanswerd = submitanswer(id, answer)
    
#     if submitanswerd["answer"] == True:
#         return jsonify(
#             {
#                 "status": "ok",
#                 "message": f"Congrats! Your answer is right!",
#                 "answer": submitanswerd["answer"]
#             }
#         )
    
#     else:
#         return jsonify(
#             {
#                 "status": "ok",
#                 "message": f"Awww, you got wrong answer :(",
#                 "answer": submitanswerd["answer"]
#             }
#         )


@ularq_blueprint.route("/api/ular/submitanswer")
def apiular_submitanswer():
    answer = af_requestget("answer")
    code = af_requestget("code")
    player = af_requestget("player")

    if inputnotvalidated(answer):
        return jsonifynotvalid("answer")
    if inputnotvalidated(code):
        return jsonifynotvalid("code")
    if inputnotvalidated(player):
        return jsonifynotvalid("player")
    
    rdata = roomdata(code)
    rstate = rdata["state"]
    rturn = rdata["turn"]
    rquestionid = rdata["questionid"]

    if rquestionid != "":

        if player == rturn:
            submitanswerd = submitanswer(rquestionid, answer)
            new_data = {"questionid": ""}
            af_replacecsv2(roomcsv, "code", code, new_data)
            #todo - kalau tangga, naik, kalau ular, takde
            
            if submitanswerd["answer"] == True:
                return jsonify(
                    {
                        "status": "ok",
                        "message": f"Congrats! Your answer is right!",
                        "answer": submitanswerd["answer"]
                    }
                )
            
            else:
                return jsonify(
                    {
                        "status": "ok",
                        "message": f"Awww, you got wrong answer :(",
                        "answer": submitanswerd["answer"]
                    }
                )
        else:
            return jsonify(
                {
                    "status": "error",
                    "message": f"This is not your turn!"
                }
            )
    else:
        return jsonify(
            {
                "status": "error",
                "message": f"No question available!"
            }
        )