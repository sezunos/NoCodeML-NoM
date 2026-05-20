from flask import Blueprint, render_template, session, request
from utils import helpers
from werkzeug.utils import secure_filename
import magic
import os
from db import db
import time


upload_bp = Blueprint("upload", __name__)
permitted_mimes = ["text/plain", "text/csv"]
path_to_dir = r"C:\Users\user\NoM\data\session_datasets"

@upload_bp.route("/upload", methods=["GET", "POST"])
@helpers.session_required
def upload_page():
    if request.headers.get("HX-Request") and request.method == "POST":
        file = request.files["file"]
        file_part = file.read(2048)

        real_type = magic.from_buffer(file_part, mime=True)
        if real_type not in permitted_mimes:
            return "Not permitted file type. You should upload .csv"
        
        file.seek(0)
        filename = secure_filename(file.filename)
        random_prefix = os.urandom(5).hex()
        full_filename = random_prefix + filename
        path_to_file = os.path.join(path_to_dir, full_filename)
        file.save(path_to_file)
        db.add_session_dataset(full_filename, path_to_file, time.time())
        return "Данные успешно загружены"

    return render_template("upload.html", username=session["username"])