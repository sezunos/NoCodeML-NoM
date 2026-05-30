import os

import numpy as np
from flask import Blueprint, render_template, session, request

from utils import helpers, df_utils, lru_session_datasets


edit_bp = Blueprint("edit", __name__)

no_dataset_message = "Сначала нужно загрузить датасет"

@edit_bp.route("/edit/cut_add_bad", methods=["POST", "GET"])
@helpers.session_required
def cut_add_bad():
    el_id = os.urandom(3).hex()
    add_bad = f"""
        <input type="text" name="element_{el_id}" placeholder="Введите значение элемента" required>
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

def na_work(dataset, col: str, na_work_type: str, **kwargs):
    aggfuncs = {
        "mean": np.nanmean,
        "median": np.nanmedian,
    }
    if na_work_type == "drop":
        dataset = dataset.dropna(subset=[col])
    elif na_work_type == "ffill":
        dataset[col] = dataset[col].ffill()
    elif na_work_type == "bfill":
        dataset[col] = dataset[col].bfill()
    else:
        dataset[col] = dataset[col].fillna(aggfuncs[na_work_type](dataset[col]))

    return dataset

def cut(dataset, col: str, min: int, max: int, where_remove: str, bads: list, **kwargs):
    def to_dtype(value, dtype):
        try:
            return np.array(value, dtype=dtype)
        except:
            return value

    col_dtype = dataset[col].dtype
    min = to_dtype(min, col_dtype)
    max = to_dtype(max, col_dtype)
    bads = to_dtype(bads, col_dtype)

    query = ''
    if (min != '') and (max != ''):
        query = f"(@min <= `{col}` <= @max)"
        if where_remove == "inner":
            query = '~' + query
    if len(bads) != 0:
        query += ('&' if query else '') + f"(`{col}` not in @bads)"
    print(query)
    dataset = dataset.query(query)

    return dataset

@edit_bp.route("/edit/<string:action_type>", methods=["GET", "POST"])
@helpers.session_required
def do_action(action_type):
    if helpers.is_htmx_req():
        actions = {
            "add_col": add_col,
            "del_col": del_col,
            "upd_col": upd_col,
            "na_work": na_work,
            "cut": cut
        }

        session_dataset_id = session.get("session_dataset_id", None)
        session_dataset = lru_session_datasets.get_dataset(session_dataset_id)
        if session_dataset is None:
            return no_dataset_message
        
        params = request.form.to_dict()
        params["bads"] = list()
        for key, param in params.items():
            if "element" in key:
                params["bads"].append(param)

        try:
            session_dataset = actions[action_type](session_dataset, **params)
            lru_session_datasets.update_dataset(session_dataset_id, session_dataset)

            return helpers.htmx_redirect("/edit")
        except:
            return "Произошла ошибка"

@edit_bp.route("/edit", methods=["GET", "POST"])
@helpers.session_required
def edit_page():
    if helpers.is_htmx_req():
        session_dataset = lru_session_datasets.get_dataset(session.get("session_dataset_id", None))
        if session_dataset is None:
            return no_dataset_message
        
        action_type = request.headers.get("HX-Trigger")
        
        return render_template("edit/" + action_type + ".html", cols=session_dataset.columns, action_type=action_type)
    
    df_html = df_utils.show_session_df_html()
    return render_template("edit/edit.html", username=session["username"], df_html=df_html)