from flask import Blueprint, render_template, session, request, send_file
import pandas as pd

from utils import helpers, df_utils
from db import db


account_bp = Blueprint("account", __name__)

@account_bp.route("/account/model_page", methods=["GET", "POST"])
@helpers.session_required
def model_page():
    model_id = request.form.get("model_id")

    return helpers.htmx_redirect(f"/account/model_page/{model_id}")

@account_bp.route("/account/model_page/<int:model_id>", methods=["GET", "POST"])
@helpers.session_required
def download_model(model_id):
    path_to_model = db.get_model_data(model_id)[2]

    return send_file(path_to_model, as_attachment=True)

@account_bp.route("/account", methods=["GET", "POST"])
@helpers.session_required
def account_page():
    query = """
        SELECT m.name, m.model_type, ld.name, m.train_date, m.description, ld.id
        FROM models m
        INNER JOIN linked_datasets ld ON m.dataset_id = ld.id
        WHERE user_id = (?)
    """
    fetchall, lastrowid = db._execute(query, (session["user_id"],))
    cols = ["Название модели", "Тип модели", "Название датасета", "Дата обучения", "Описание", "hidden_id"]
    
    if fetchall:
        df = pd.DataFrame(fetchall, columns=cols)
        df["hidden_id"] = df["hidden_id"].apply(lambda x: f'<input type="hidden" name="model_id" value="{x}">')
        df["Дата обучения"] = pd.to_datetime(df["Дата обучения"], unit='s').dt.strftime(r"%d-%m-%Y %H:%M")
        df_size = len(df)
        df_html = df_utils.get_correct_df_html(dataset=df)
        df_html = df_html.replace('<tr>', '<tr hx-post="/account/model_page" hx-target="#dummy" hx-trigger="click" style="cursor:pointer;" hx-include="closest tr">')
    else:
        df_size = 0
        min_idxs = 5
        df_html = df_utils.get_correct_df_html(min_idxs=min_idxs, dataset=pd.DataFrame(columns=cols))

    return render_template("account/account.html", id=session["user_id"], username=session["username"], models_count=df_size, models_table_html=df_html)