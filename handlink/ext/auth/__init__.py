from flask_login import LoginManager

from handlink.models.user import User


login_manager = LoginManager()


def init_app(app):
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faca login para acessar esta pagina."
    login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
