from handlink.views.main import bp_main
from handlink.views.auth import bp_auth
from handlink.views.user import bp_user
from handlink.views.services import bp_services

def init_app(app):
    """
    Registra o blueprint na aplicacao Flask e envia mensagem de inicializacao.
    """
    app.register_blueprint(bp_main)
    app.logger.info("Blueprint 'site' registrado com sucesso")

    app.register_blueprint(bp_services)
    app.logger.info("Blueprint 'services' registrado com sucesso")

    app.register_blueprint(bp_user)
    app.logger.info("Blueprint 'user' registrado com sucesso")

    app.register_blueprint(bp_auth)
    app.logger.info("Blueprint 'auth' registrado com sucesso")
