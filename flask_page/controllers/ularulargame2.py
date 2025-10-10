from flask import Blueprint, render_template

ularulargame2_bp = Blueprint("ularulargame2", __name__, url_prefix="/ularulargame2")

@ularulargame2_bp.route("/")
def index():
    # this will render templates/ularulargame.html
    return render_template("ularulargame2.html")