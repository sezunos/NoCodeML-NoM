from flask import Blueprint, render_template, session, request, send_file
from utils import helpers, df_utils
from utils.lru_session_datasets import lru_session_datasets
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
import mpld3

analysis_bp = Blueprint("analysis", __name__)

no_dataset_message = "Сначала нужно загрузить таблицу"

@analysis_bp.route("/analysis/<string:plot_type>", methods=["POST", "GET"])
@helpers.session_required
def analysis_create_plot(plot_type):
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(1, 1, 1)
    sns.set_theme(style="darkgrid", palette="Set1")
    plot_types = {
        "linear": sns.lineplot,
        "bar": sns.barplot,
        "scatter": sns.scatterplot,
        "hist": sns.histplot,
        "box": sns.boxplot,
        "heat": sns.heatmap
    }

    session_dataset_id = session["session_dataset_id"]
    session_dataset = lru_session_datasets.get_dataset(session_dataset_id)
    if session_dataset is None:
        return no_dataset_message
        
    params = {key: (value if value else None) for key, value in request.form.to_dict().items()}

    try:
        plot_types[plot_type](data=session_dataset, ax=ax, **params)
        html_graph = mpld3.fig_to_html(fig)
    except Exception as e:
        print(e)
        return "Неверные данные для построения графика"

    fig.tight_layout()
    return html_graph
        
@analysis_bp.route("/analysis", methods=["GET", "POST"])
@helpers.session_required
def analysis_page():
    if request.headers.get("HX-Request") and request.method == "POST":
        plot_params_request = {
            "linear": "universal params request",
            "bar": "bar params request",
            "scatter": "scatter params request",
            "hist": "hist params request",
            "box": "universal params request",
            "heat": "heat params request"
        }

        session_dataset_id = session.get("session_dataset_id", None)
        if session_dataset_id is None:
            return no_dataset_message
        session_dataset = lru_session_datasets.get_dataset(session_dataset_id)
        if session_dataset is None:
            return no_dataset_message

        plot_type = request.headers.get("HX-Trigger")

        return render_template("analysis/" + plot_params_request[plot_type] + ".html", cols=session_dataset.columns, plot_type=plot_type)

    df_html = df_utils.show_session_df_html()
    return render_template("analysis/analysis.html", username=session["username"], df_html=df_html)