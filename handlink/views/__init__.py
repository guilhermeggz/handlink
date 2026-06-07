from handlink.views.auth import bp_auth
from handlink.views.main import bp_main
from handlink.views.services import bp_services
from handlink.views.user import bp_user


def init_app(app):
    app.register_blueprint(bp_main)
    app.logger.info("Blueprint 'main' registrado com sucesso")

    app.register_blueprint(bp_user)
    app.logger.info("Blueprint 'user' registrado com sucesso")

    app.register_blueprint(bp_auth)
    app.logger.info("Blueprint 'auth' registrado com sucesso")

    app.register_blueprint(bp_services)
    app.logger.info("Blueprint 'services' registrado com sucesso")
