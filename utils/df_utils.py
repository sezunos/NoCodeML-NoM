from flask import session

from utils import lru_session_datasets


def expand_idxs_to(df, min_idxs: int):
    need_idxs = min_idxs - len(df)
    if need_idxs <= 0:
        return df
    new_index = range(min_idxs)
    return df.reindex(new_index)

def make_df_html(df):
    return df.to_html(na_rep="", escape=False)

def get_correct_df_html(dataset_id: int=None, min_idxs: int=None, max_idxs: int=None, dataset=None, more_button: bool=False):
    if min_idxs is None:
        min_idxs = 1

    df = lru_session_datasets.get_dataset(dataset_id) if dataset is None else dataset
    if df is None:
        return
    df_len = len(df)

    if max_idxs is None or max_idxs > df_len:
        max_idxs = df_len
    df = df.head(max_idxs)
    
    df = expand_idxs_to(df, min_idxs)
    html_table = make_df_html(df)
    if more_button:
        html_table = "<div id='df_html_table'>" + html_table +\
        f"<br><button hx-post='/df_utils_add_cols/{max_idxs}' hx-target='#df_html_table'>Еще</button> " +\
        "<button hx-post='/df_utils_hide_cols' hx-target='#df_html_table'>Скрыть</button>" +\
        "</div>"

    return html_table

def show_session_df_html():
    max_idxs = 10
    df_html = "<p>Нет датасета</p>"
    
    session_dataset_id = session.get("session_dataset_id", None)
    correct_df_html = get_correct_df_html(session_dataset_id, max_idxs=max_idxs, more_button=True)

    if correct_df_html is not None:
        df_html = "<p>Текущий датасет: </p>" + correct_df_html

    return df_html