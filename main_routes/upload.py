import time
from pathlib import Path
import os

from flask import Blueprint, render_template, session, request
from werkzeug.utils import secure_filename
import magic

from db import db
from utils import helpers, df_utils


upload_bp = Blueprint("upload", __name__)
permitted_mimes = ["text/plain", "text/csv"]
path_to_dir = Path.cwd() / "data" / "datasets"
path_to_dir.mkdir(parents=True, exist_ok=True)

@upload_bp.route("/upload", methods=["GET", "POST"])
@helpers.session_required
def upload_page():
    if helpers.is_htmx_req():
        try:
            file = request.files["file"]
            file_part = file.read(2048)

            real_type = magic.from_buffer(file_part, mime=True)
            if real_type not in permitted_mimes:
                return "Не подходящий формат файла. Загрузите .csv"
            
            file.seek(0)
            filename = secure_filename(file.filename)
            random_prefix = os.urandom(5).hex()
            full_filename = f"{random_prefix}_{filename}"
            path_to_file = str(path_to_dir / full_filename)

            file.save(path_to_file)
            session_dataset_id = db.add_session_dataset(full_filename, path_to_file, time.time())

            session["session_dataset_id"] = session_dataset_id

            return helpers.htmx_redirect("/upload")
        except Exception as e:
            return "Произошла ошибка"

    df_html = df_utils.show_session_df_html()
    return render_template("upload.html", username=session["username"], df_html=df_html)