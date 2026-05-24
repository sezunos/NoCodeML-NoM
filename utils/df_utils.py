from utils.lru_session_datasets import lru_session_datasets
from flask import session
import pandas as pd


def expand_idxs_to(df, min_idxs: int):
    need_idxs = min_idxs - len(df)
    if need_idxs <= 0:
        return df
    new_index = range(min_idxs)
    return df.reindex(new_index)

def make_df_html(df):
    return df.to_html(index=False, na_rep="")

def get_correct_df_html(dataset_id: int, min_idxs: int=None, max_idxs: int=None):
    if min_idxs is None:
        min_idxs = 5

    df = lru_session_datasets.get_dataset(dataset_id)
    if df is None:
        df = pd.DataFrame()

    if max_idxs is None:
        max_idxs = len(df)
    df = df.head(max_idxs)
    
    df = expand_idxs_to(df, min_idxs)
    html_table = make_df_html(df)
    return html_table

def show_session_df_html():
    min_idxs = 5
    max_idxs = 10
    df_html = "<p>No dataset yet</p>"
    
    session_dataset_id = session.get("session_dataset_id", None)
    if session_dataset_id is not None:
        df_html = "<p>Current Dataset: </p>" + get_correct_df_html(session_dataset_id, min_idxs, max_idxs)

    return df_html