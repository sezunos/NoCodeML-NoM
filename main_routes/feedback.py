from pathlib import Path

from flask import Blueprint, render_template, session, request

from utils import helpers


path_to_dir = Path.cwd() / "data" / "feedbacks"
path_to_dir.parent.mkdir(parents=True, exist_ok=True)

feedback_bp = Blueprint("feedback", __name__)

@feedback_bp.route("/feedback", methods=["GET", "POST"])
@helpers.session_required
def feedback_page():
    if helpers.is_htmx_req():
        mail = request.form.get("mail")
        feedback = request.form.get("feedback")
        with open(path_to_dir, 'a', encoding="utf-8") as feedback_file:
            if feedback_file.tell() != 0: feedback_file.write('\n$$$\n')
            feedback_file.write(mail + '\n')
            feedback_file.write(feedback)
        
        return helpers.htmx_redirect("/account")
    
    return render_template("feedback.html", username=session["username"])