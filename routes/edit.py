from flask import Blueprint, render_template, session, request
from utils import helpers, df_utils
from utils.lru_session_datasets import lru_session_datasets
import numpy as np
import time


edit_bp = Blueprint("edit", __name__)

no_dataset_message = "Сначала нужно загрузить датасет"

@edit_bp.route("/edit/cut_add_bad", methods=["POST", "GET"])
@helpers.session_required
def cut_add_bad():
    timestamp = time.time_ns()
    add_bad = f"""
        <input type="text" name="element_{timestamp}" placeholder="Введите значение элемента" required>
    """
    return add_bad

@edit_bp.route("/edit/cut_del_bads", methods=["POST", "GET"])
@helpers.session_required
def cut_del_bads():
    return ''

def add_col(dataset, name: str, col1: str, elwisefunc_name: str, col2: str, **kwargs):
    elwisefunc = {
        '+': np.add,
        '-': np.subtract,
        '*': np.multiply,
        '/': np.true_divide
    }
    dataset[name] = elwisefunc[elwisefunc_name](dataset[col1], dataset[col2])
    
    return dataset

def del_col(dataset, col: str, **kwargs):
    dataset = dataset.drop(columns=[col])

    return dataset

def upd_col(dataset, col: str, elwisefunc_name, **kwargs):
    elwisefunc = {
        "round": np.round,
        "ceil": np.ceil,
        "floor": np.floor,
        "abs": np.abs,
        "sqrt": np.sqrt,
        "cos": np.cos,
        "sin": np.sin
    }
    dataset[col] = elwisefunc[elwisefunc_name](dataset[col])

    return dataset

def na_work(dataset, col: str, action_type: str, **kwargs):
    aggfuncs = {
        "mean": np.nanmean,
        "median": np.nanmedian,
    }
    if action_type == "drop":
        dataset = dataset.dropna(subset=[col])
    elif action_type == "ffill":
        dataset[col] = dataset[col].ffill()
    elif action_type == "bfill":
        dataset[col] = dataset[col].bfill()
    else:
        dataset[col] = dataset[col].fillna(aggfuncs[action_type](dataset[col]))

    return dataset

def cut(dataset, col: str, min: int, max: int, where: str, bads: list, **kwargs):
    query = ''
    if min and max:
        query = f"({min} <= `{col}` <= {max})"
        if where == "inner":
            query = '~' + query
    if bads:
        query += ('&' if query else '') + f"(`{col}` not in {bads})"
    dataset = dataset.query(query)

    return dataset

@edit_bp.route("/edit/<string:action_type>", methods=["GET", "POST"])
@helpers.session_required
def do_action(action_type):
    if request.headers.get("HX-Request") and request.method == "POST":
        actions = {
            "add_col": add_col,
            "del_col": del_col,
            "upd_col": upd_col,
            "na_work": na_work,
            "cut": cut
        }

        session_dataset_id = session.get("session_dataset_id", None)
        if session_dataset_id is None:
            return no_dataset_message
        session_dataset = lru_session_datasets.get_dataset(session_dataset_id)
        if session_dataset is None:
            return no_dataset_message
        
        params = request.form.to_dict()
        params["bads"] = list()
        for key, param in params.items():
            if "element" in key:
                params["bads"].append(param)

        session_dataset = actions[action_type](session_dataset, **params)
        lru_session_datasets.update_dataset(session_dataset_id, session_dataset)

        return helpers.htmx_redirect("/edit")

@edit_bp.route("/edit", methods=["GET", "POST"])
@helpers.session_required
def edit_page():
    if request.headers.get("HX-Request") and request.method == "POST":
        action_type = request.headers.get("HX-Trigger")
        session_dataset_id = session.get("session_dataset_id", None)
        if session_dataset_id is None:
            return no_dataset_message
        session_dataset = lru_session_datasets.get_dataset(session_dataset_id)
        if session_dataset is None:
            return no_dataset_message
        
        return render_template("edit/" + action_type + ".html", cols=session_dataset.columns, action_type=action_type)
    
    df_html = df_utils.show_session_df_html()
    return render_template("edit/edit.html", username=session["username"], df_html=df_html)