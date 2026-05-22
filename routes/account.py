from flask import Blueprint, render_template, session
from utils import helpers
from utils import df_utils
from db import db
import pandas as pd


account_bp = Blueprint("account", __name__)

@account_bp.route("/account", methods=["GET", "POST"])
@helpers.session_required
def account_page():
    query = """
        SELECT m.name, m.model_type, ld.name, m.train_date, m.description, ld.id
        FROM models m
        INNER JOIN linked_datasets ld ON m.dataset_id = ld.id
        WHERE user_id = (?)
    """
    data = db._execute(query, (session["user_id"],))[0]
    cols = ["Название модели", "Тип модели", "Название датасета", "Дата обучения", "Описание", "dummy"]
    
    if data:
        df = pd.DataFrame(data, columns=cols).drop(columns=["dummy"])
        df["Дата обучения"] = pd.to_datetime(df["Дата обучения"], unit='s').dt.strftime(r"%d-%m-%Y %H:%M")
        df_size = len(df)
        df_html = df_utils.get_correct_df_html(data[-1])
    else:
        df_size = 0
        min_idxs = 5
        df_html = df_utils.expand_idxs_to(pd.DataFrame(columns=cols).drop(columns=["dummy"]), min_idxs)
        df_html = df_utils.make_df_html(df_html)

    return render_template("account.html", id=session["user_id"], username=session["username"], models_count=df_size, models_table_html=df_html)