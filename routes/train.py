from flask import Blueprint, render_template, session
from utils import helpers


train_bp = Blueprint("train", __name__)

@train_bp.route("/train")
@helpers.session_required
def train_page():
    

    return render_template("train.html", username=session["username"])