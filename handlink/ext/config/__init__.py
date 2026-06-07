import os

from dotenv import load_dotenv


def init_app(app):
    env_name = os.environ.get("HANDLINK_ENV", "dev")
    env_file = f".env.{env_name}"
    if os.path.exists(env_file):
        load_dotenv(env_file, override=True)

    app.json.ensure_ascii = False

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")
    app.config["DEBUG"] = os.environ.get("FLASK_DEBUG") == "1"

    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")

    mail_port = os.environ.get("MAIL_PORT")
    app.config["MAIL_PORT"] = int(mail_port) if mail_port else 587

    app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS") == "True"
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "sqlite:///handlink.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if app.debug:
        app.config["DEBUG_TB_TEMPLATE_EDITOR_ENABLED"] = True
        app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
        app.config["DEBUG_TB_PANELS"] = (
            "flask_debugtoolbar.panels.versions.VersionDebugPanel",
            "flask_debugtoolbar.panels.timer.TimerDebugPanel",
            "flask_debugtoolbar.panels.headers.HeaderDebugPanel",
            "flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel",
            "flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel",
            "flask_debugtoolbar.panels.template.TemplateDebugPanel",
            "flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel",
            "flask_debugtoolbar.panels.logger.LoggingPanel",
            "flask_debugtoolbar.panels.route_list.RouteListDebugPanel",
        )
