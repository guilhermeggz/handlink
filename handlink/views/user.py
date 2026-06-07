from flask import Blueprint, render_template
from flask_login import current_user, login_required


bp_user = Blueprint("user", __name__)


@bp_user.route("/perfil")
@login_required
def profile():
    return render_template("profile/profile.html", user=current_user)
