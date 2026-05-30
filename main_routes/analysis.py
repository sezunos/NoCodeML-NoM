import io
import base64

from flask import Blueprint, render_template, session, request, send_file
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from utils import helpers, df_utils, lru_session_datasets


analysis_bp = Blueprint("analysis", __name__)

no_dataset_message = "Сначала нужно загрузить датасет"

@analysis_bp.route("/analysis/plots/<string:plot_type>", methods=["POST", "GET"])
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

    session_dataset = lru_session_datasets.get_dataset(session.get("session_dataset_id", None))
    if session_dataset is None:
        return no_dataset_message
        
    params = {key: (value if value else None) for key, value in request.form.to_dict().items()}
    if plot_type == "heat":
        params["annot"] = True
        params["fmt"] = ".2f"
        params["cmap"] = "coolwarm"
        params["center"] = 0
    plot_dataset = session_dataset.corr(numeric_only=True) if plot_type == "heat" else session_dataset

    try:
        plot_types[plot_type](data=plot_dataset, ax=ax, **params)
        with io.BytesIO() as buffer:
            fig.savefig(buffer)
            buffer.seek(0)
            img = base64.b64encode(buffer.read()).decode("utf-8")
            html_plot = fr"<img src='data:image/png;base64,{img}'>"
    except:
        return "Произошла ошибка"
    finally:
        plt.close(fig)

    return html_plot
        
@analysis_bp.route("/analysis/plots", methods=["GET", "POST"])
@helpers.session_required
def plots_page():
    if helpers.is_htmx_req():
        session_dataset = lru_session_datasets.get_dataset(session.get("session_dataset_id", None))
        if session_dataset is None:
            return no_dataset_message

        plot_type = request.headers.get("HX-Trigger")
        html_type = plot_type
        if plot_type in ("linear", "box"):
            html_type = "universal"

        return render_template("analysis/plots/" + html_type + ".html", cols=session_dataset.columns, plot_type=plot_type)

    return render_template("analysis/plots/plots.html")

@analysis_bp.route("/analysis/groupby", methods=["GET", "POST"])
@helpers.session_required
def gropby_page():
    if helpers.is_htmx_req():
        session_dataset = lru_session_datasets.get_dataset(session.get("session_dataset_id", None))
        if session_dataset is None:
            return no_dataset_message

        params = request.form.to_dict()

        try:
            groupby = session_dataset.groupby(params["group_col"])[[params["target_col"]]].agg(params["aggfunc"])
            groupby_html = df_utils.get_correct_df_html(dataset=groupby, min_idxs=0)

            return groupby_html
        except:
            return "Произошла ошибка"
    
@analysis_bp.route("/analysis/pivottable", methods=["GET", "POST"])
@helpers.session_required
def pivottable_page():
    if helpers.is_htmx_req():
        session_dataset = lru_session_datasets.get_dataset(session.get("session_dataset_id", None))
        if session_dataset is None:
            return no_dataset_message

        params = request.form.to_dict()
        
        try:
            pivottable = session_dataset.pivot_table(**params)
            pivottable_html = df_utils.get_correct_df_html(dataset=pivottable, min_idxs=0)

            return pivottable_html
        except Exception as e:
            print(e)
            return "Произошла ошибка"

@analysis_bp.route("/analysis", methods=["GET", "POST"])
@helpers.session_required
def analysis_page():
    if helpers.is_htmx_req():
        session_dataset = lru_session_datasets.get_dataset(session.get("session_dataset_id", None))
        if session_dataset is None:
            return no_dataset_message
        
        redirect_to = request.headers.get("HX-Trigger")

        return render_template("/analysis/" + redirect_to + ".html", cols=session_dataset.columns)

    df_html = df_utils.show_session_df_html()
    return render_template("analysis/analysis.html", username=session["username"], df_html=df_html)