from flask import Blueprint, request

from utils import helpers


navigator_bp = Blueprint("navigator", __name__)

@navigator_bp.route("/navigator", methods=["POST"])
def navigator():
    if helpers.is_htmx_req():
        redirect_to = request.headers.get("HX-Trigger")
        return helpers.htmx_redirect('/' + redirect_to)