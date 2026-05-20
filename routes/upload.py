from flask import Blueprint, render_template, session


upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/upload", methods=["GET", "POST"])
def upload_page():
    return render_template("upload.html", username=session["username"])