from flask import Blueprint, render_template, session
from utils import helpers
from db import db
import pandas as pd


account_bp = Blueprint("account", __name__)

@account_bp.route("/account", methods=["GET", "POST"])
@helpers.session_required
def account_page():
    query = """
        SELECT m.name, m.model_type, ld.name, m.train_date, m.description
        FROM models m
        INNER JOIN linked_datasets ld ON m.dataset_id = ld.id
        WHERE user_id = (?)
    """
    data = db._execute(query, (session["id"],))[0]
    cols = ["Название модели", "Тип модели", "Название датасета", "Дата обучения", "Описание"]
    df = pd.DataFrame(data, columns=cols)
    df["Дата обучения"] = pd.to_datetime(df["Дата обучения"], unit='s').dt.strftime(r"%d-%m-%Y %H:%M")
    added = 0
    while len(df) < 5:
        new_row = pd.DataFrame([[""] * len(cols)], columns=cols)
        df = pd.concat([df, new_row], ignore_index=True)
        added += 1

    return render_template("account.html", id=session["id"], username=session["username"], models_count=df["Название модели"].count() - added, models_table_html=df.to_html(index=False))