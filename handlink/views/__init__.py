from handlink.views.main import bp_main

def init_app(app):
    """
    Registra o blueprint na aplicacao Flask e envia mensagem de inicializacao.
    """
    app.register_blueprint(bp_main)
    app.logger.info("Blueprint 'site' registrado com sucesso")