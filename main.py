from flask import Flask, render_template
from flask_htmx import HTMX
from db import db, garbage_datasets_collector
from routes import auth, account, upload, edit, analysis, train
from utils import navigator, df_utils_add_cols


app = Flask(__name__)
app.secret_key = "adsaddasaadasdadaaddsdasdsasdaads"
htmx = HTMX(app)

app.register_blueprint(auth.auth_bp)
app.register_blueprint(account.account_bp)
app.register_blueprint(upload.upload_bp)
app.register_blueprint(navigator.navigator_bp)
app.register_blueprint(edit.edit_bp)
app.register_blueprint(analysis.analysis_bp)
app.register_blueprint(train.train_bp)
app.register_blueprint(df_utils_add_cols.df_utils_add_cols_bp)

# TODO: доделать edit 
# TODO: доделать analysis
# TODO: рефактор edit (попытаться применить DRY)
# TODO: сделать "еще" в utils
# TODO: разобраться с flask_email, временная метка в куках
# TODO: перенести роуты в routes

if __name__ == "__main__":
    db.init_all()
    app.run(port=8080, host="127.0.0.1")