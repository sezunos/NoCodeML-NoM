import os
import time
from pathlib import Path

from flask import Blueprint, render_template, session, request
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, mean_absolute_error, r2_score, root_mean_squared_error, recall_score
from lightgbm import LGBMClassifier, LGBMRegressor
import joblib

from db import db
from utils import helpers, df_utils, lru_session_datasets


train_bp = Blueprint("train", __name__)

no_dataset_message = "Сначала нужно загрузить датасет"

def get_text_encoder_auto(col: str):
    session_dataset = lru_session_datasets.get_dataset(session.get("session_dataset_id", None))
    if session_dataset is None:
        return no_dataset_message
    
    nunique_values = session_dataset[col].nunique()
    words_cnt = session_dataset[col].str.split().str.len()
    median_words_cnt = words_cnt.median()

    if nunique_values <= 7:
        return "OHE"
    elif median_words_cnt <= 5:
        return "CntVec"
    else:
        return "TFIDF"
    
def get_scaler_auto(col: str):
    session_dataset = lru_session_datasets.get_dataset(session.get("session_dataset_id", None))
    if session_dataset is None:
        return no_dataset_message
    
    Q1 = session_dataset[col].quantile(0.25)
    Q3 = session_dataset[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    query = f"(`{col}` < {lower_bound}) | ({upper_bound} < `{col}`)"
    outbound_count = len(session_dataset.query(query))
    outbound_percent = outbound_count / len(session_dataset[col])

    if outbound_percent >= 0.05:
        return "Robust"
    else:
        return "Standard"
    
def get_model_auto(target_col):
    session_dataset = lru_session_datasets.get_dataset(session.get("session_dataset_id", None))
    if session_dataset is None:
        return no_dataset_message
    
    nunique_values = session_dataset[target_col].nunique()
    values_cnt = len(session_dataset)
    if nunique_values <= 7:
        regression = "LogReg"
        rforest = "RandForClas"
        gradboost = "LGBMClas"
    else:
        regression = "LinReg"
        rforest = "RandForReg"
        gradboost = "LGBMReg"

    if values_cnt <= 1000:
        return regression
    elif values_cnt <= 10000:
        return rforest
    else:
        return gradboost


@train_bp.route("/train/save_model", methods=["GET", "POST"])
@helpers.session_required
def save_model():
    if helpers.is_htmx_req():
        session_dataset_id = session.get("session_dataset_id", None)
        
        fetchone = db.get_session_dataset_data(session_dataset_id)

        linked_dataset_id = db.add_linked_dataset('_'.join(fetchone[1].split('_')[1:]), fetchone[2])

        model_data_query = """
            SELECT id
            FROM models
            WHERE user_id = (?) AND dataset_id IS NULL
        """
        fetchall, lastrowid = db._execute(model_data_query, (session["user_id"],))
        model_id = fetchall[0][0]

        model_update_query = """
            UPDATE models
            SET dataset_id = (?)
            WHERE id = (?)
        """
        db._execute(model_update_query, (linked_dataset_id, model_id))

        session_dataset_kill_query = """
            DELETE
            FROM session_datasets
            WHERE id = (?) 
        """
        db._execute(session_dataset_kill_query, (session_dataset_id,))
        lru_session_datasets._clear_cache([session_dataset_id])

        return helpers.htmx_redirect("/account")

@train_bp.route("/train", methods=["GET", "POST"])
@helpers.session_required
def train_page():
    session_dataset_id = session.get("session_dataset_id", None)
    session_dataset = lru_session_datasets.get_dataset(session_dataset_id)
    if session_dataset is None:
        return render_template("train.html", username=session["username"], child_of_trash_architecture=True, df_html=df_utils.show_session_df_html())

    if helpers.is_htmx_req():
        params = request.form.to_dict()

        last_temp_model_kill_query = """
            DELETE
            FROM models
            WHERE user_id = (?) AND dataset_id IS NULL
        """
        db._execute(last_temp_model_kill_query, (session["username"],))
        
        models = {
            "LogReg": (LogisticRegression, "Clas"),
            "RandForClas": (RandomForestClassifier, "Clas"),
            "LGBMClas": (LGBMClassifier, "Clas"),
            "LinReg": (LinearRegression, "Reg"),
            "RandForReg": (RandomForestRegressor, "Reg"),
            "LGBMReg": (LGBMRegressor, "Reg")
        }

        Scalers_cols = {
            "Standard": [],
            "MinMax": [],
            "Robust": []
        }
        
        TextEncoders_cols = {
            "OHE": [],
            "CntVec": [],
            "TFIDF": [],
            "Label": []
        }

        model_name = params["model_name"]
        model_description = params["model_description"]
        text_work_param = params["text_work"]
        scaler_param = params["scaler"]
        model_param = params["model_type"]
        target_col = params["target_col"]
        train_percent = float(params["train_test_percent"]) / 100

        session_dataset = session_dataset.dropna()

        for col in session_dataset.columns:
            if col == target_col: continue

            if session_dataset[col].dtype == "object":
                text_encoder = TextEncoders_cols[get_text_encoder_auto(col)] if text_work_param == "auto" else TextEncoders_cols[text_work_param]
                text_encoder.append(col)
            elif session_dataset[col].dtype.kind in "ifu":
                scaler = Scalers_cols[get_scaler_auto(col)] if scaler_param == "auto" else Scalers_cols[scaler_param]
                scaler.append(col)
        
        transformer = []

        if Scalers_cols["Standard"]: transformer.append(("StandardScaler", StandardScaler(), Scalers_cols["Standard"]))
        if Scalers_cols["MinMax"]: transformer.append(("MinMax", MinMaxScaler(), Scalers_cols["MinMax"]))
        if Scalers_cols["Robust"]: transformer.append(("Robust", RobustScaler(), Scalers_cols["Robust"]))

        if TextEncoders_cols["OHE"]: transformer.append(("OHE", OneHotEncoder(handle_unknown="ignore"), TextEncoders_cols["OHE"]))

        if TextEncoders_cols["CntVec"]:
            for col in TextEncoders_cols["CntVec"]:
                transformer.append((f"CntVec_{col}", CountVectorizer(), col))

        if TextEncoders_cols["TFIDF"]:
            for col in TextEncoders_cols["TFIDF"]:
                transformer.append((f"TFIDF_{col}", TfidfVectorizer(), col))

        try:
            preprocessor = ColumnTransformer(transformers=transformer)
            if model_param == "auto":
                model_param = get_model_auto(params["target_col"])
            model, task_type = models[model_param]
            pipeline = Pipeline([
                ("preprocessing", preprocessor),
                ("fit", model())
            ])

            y = session_dataset[target_col]
            if session_dataset[target_col].dtype == "object" and task_type == "Clas":
                y = LabelEncoder().fit_transform(y)
            X = session_dataset.drop(columns=[target_col])

            if task_type == "Reg":
                X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=train_percent)
            else:
                try:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=train_percent, stratify=y)
                except:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=train_percent)


            final_model = pipeline.fit(X_train, y_train)
            
            y_pred = final_model.predict(X_test)
            if task_type == "Clas":
                metrics = {
                    "Accuracy score": [accuracy_score(y_test, y_pred)],
                    "Precision score": [precision_score(y_test, y_pred, average="macro")],
                    "Recall score": [recall_score(y_test, y_pred, average="macro")],
                    "F1 score": [f1_score(y_test, y_pred, average="macro")]
                }
            else:
                metrics = {
                    "Mean absolute error": [mean_absolute_error(y_test, y_pred)],
                    "Root mean squared error": [root_mean_squared_error(y_test, y_pred)],
                    "R2 score": [r2_score(y_test, y_pred)]
                }
            
            path = str(Path.cwd() / "data" / "models" / f"{os.urandom(2).hex()}_{model_name}_{session["username"]}.joblib")
            joblib.dump(pipeline, path)
            db.add_model(model_name, path, session["user_id"], model_param, time.time(), model_description, None)

            report_html = pd.DataFrame(metrics).round(3)
            report_html = df_utils.get_correct_df_html(dataset=report_html)
            save_button = f"""
                <p>
                    <button name="save_model" hx-post="/train/save_model">Сохранить модель</button>
                </p>
            """

            return report_html + save_button
        except:
            return "Произошла ошибка"

    df_html = df_utils.show_session_df_html()
    return render_template("train.html", username=session["username"], df_html=df_html, cols=session_dataset.columns)