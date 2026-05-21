from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)

def register_models():
    import handlink.models.user
    import handlink.models.role
    import handlink.models.role_user
    import handlink.models.category
    import handlink.models.service
    import handlink.models.appointment
    import handlink.models.location