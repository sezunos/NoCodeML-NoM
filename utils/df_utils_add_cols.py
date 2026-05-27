from flask import Blueprint, request, session
from utils import df_utils
from utils.lru_session_datasets import lru_session_datasets


df_utils_add_cols_bp = Blueprint("df-utils_add_cols", __name__)

no_dataset_message = "Сначала нужно загрузить датасет"

@df_utils_add_cols_bp.route("/df_utils_hide_cols", methods=["GET", "POST"])
def hide_cols():
    session_dataset_id = session.get("session_dataset_id", None)
    if session_dataset_id is None:
        return no_dataset_message
    return df_utils.get_correct_df_html(session_dataset_id, min_idxs=5, max_idxs=10, more_button=True)

@df_utils_add_cols_bp.route("/df_utils_add_cols/<int:cur_max_idxs>", methods=["GET", "POST"])
def add_cols(cur_max_idxs: int):
    session_dataset_id = session.get("session_dataset_id", None)
    if session_dataset_id is None:
        return no_dataset_message
    return df_utils.get_correct_df_html(session_dataset_id, max_idxs=cur_max_idxs+5, more_button=True)