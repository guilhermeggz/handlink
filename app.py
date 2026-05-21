from flask import Flask
import logging

def create_app(test_config=None):
    app = Flask(__name__)

    if app.debug:
        app.logger.setLevel(logging.DEBUG)

    from handlink.ext.config import init_app as init_config
    init_config(app)
    
    if test_config:
        app.config.update(test_config)


    # ----------------------------------------------------------
    # Inicializacao do banco de dados
    # ----------------------------------------------------------

    from handlink.ext.db import init_app as init_db
    init_db(app)

    from handlink.ext.db import register_models
    register_models()

    # ----------------------------------------------------------
    # Blueprints (camada de apresentacao)
    # ----------------------------------------------------------

    from handlink.views import init_app as init_site
    init_site(app)

    return app