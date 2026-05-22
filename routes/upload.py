from flask import Blueprint, render_template, session, request
from utils import helpers, df_utils
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
        session_dataset_id = db.add_session_dataset(full_filename, path_to_file, time.time())

        session["session_dataset_id"] = session_dataset_id

        return helpers.htmx_redirect("/upload")

    min_idxs = 5
    max_idxs = 10
    df_html = ''
    session_dataset_id = session.get("session_dataset_id", None)
    print(session_dataset_id)
    if session_dataset_id is not None:
        df_html = df_utils.get_correct_df_html(session_dataset_id, min_idxs, max_idxs)

    return render_template("upload.html", username=session["username"], df_html= "<p>Current Dataset</p>" + df_html)