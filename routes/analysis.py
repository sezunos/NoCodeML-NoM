from flask import Blueprint, render_template, session
from utils import helpers


analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/analysis")
@helpers.session_required
def analysis_page():
    return render_template("analysis.html", username=session["username"])