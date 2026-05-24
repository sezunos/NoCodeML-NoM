from flask import Blueprint, request
from utils import helpers


navigator_bp = Blueprint("navigator", __name__)

@navigator_bp.route("/navigator", methods=["POST"])
def navigator():
    if request.headers.get("HX-Request") and request.method == "POST":
        redirect_to = request.headers.get("HX-Trigger")
        return helpers.htmx_redirect('/' + redirect_to)