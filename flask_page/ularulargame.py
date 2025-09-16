from flask import Blueprint, render_template

ularulargame_bp = Blueprint("ularulargame", __name__, url_prefix="/ularulargame")

@ularulargame_bp.route("/")
def index():
    # this will render templates/ularulargame.html
    return render_template("ularulargame.html")