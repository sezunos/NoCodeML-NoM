from datetime import timedelta
import threading
import time
import os
from dotenv import load_dotenv

from flask import Flask
from flask_htmx import HTMX

from db import db, garbage_datasets_collector, garbage_temp_models_collector
from main_routes import auth, account, upload, edit, analysis, train, feedback
from utils import navigator, df_utils_add_cols


app = Flask(__name__)
htmx = HTMX(app)

load_dotenv()
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
app.config["SECRET_KEY"] = os.getenv("SECRET_SESSION_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=15)

app.register_blueprint(auth.auth_bp)
app.register_blueprint(account.account_bp)
app.register_blueprint(upload.upload_bp)
app.register_blueprint(navigator.navigator_bp)
app.register_blueprint(edit.edit_bp)
app.register_blueprint(analysis.analysis_bp)
app.register_blueprint(train.train_bp)
app.register_blueprint(feedback.feedback_bp)
app.register_blueprint(df_utils_add_cols.df_utils_add_cols_bp)

if __name__ == "__main__":
    sleep_time = 5 * 60
    kill_time_sd = 30 * 60
    kill_time_mc = 5 * 60

    def garbages(sleep_time, kill_time_sd, kill_time_mc):
        while True:
            garbage_datasets_collector.garbage_datasets_collector(kill_time_sd)
            garbage_temp_models_collector.garbage_temp_models_collector(kill_time_mc)
            time.sleep(sleep_time)

    garbages_thread = threading.Thread(target=garbages, args=(sleep_time, kill_time_sd, kill_time_mc), daemon=True)

    db.init_all()
    garbages_thread.start()
    app.run(port=8080, host="127.0.0.1")