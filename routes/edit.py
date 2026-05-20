from flask import Blueprint, render_template, session
from utils import helpers


edit_bp = Blueprint("edit", __name__)

@edit_bp.route("/edit")
@helpers.session_required
def edit_page():
    return render_template("edit.html", username=session["username"])