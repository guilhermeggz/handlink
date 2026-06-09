from flask import Blueprint, current_app, render_template

bp_main = Blueprint("main", __name__)

@bp_main.route('/')
def index():
    current_app.logger.debug('renderizando index html dinamicamente')

    return render_template(
        'main/index.html'
    )
