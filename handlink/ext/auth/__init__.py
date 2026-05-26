from flask_login import LoginManager
# Importe o seu modelo de Usuário (ajuste o nome da classe 'User' se for diferente)
from handlink.models.user import User  

login_manager = LoginManager()

def init_app(app):
    login_manager.init_app(app)

# ---> O QUE FALTA ESTÁ AQUI <---
@login_manager.user_loader
def load_user(user_id):
    # Essa função recebe o ID da sessão (como string) e busca o usuário no banco
    return User.query.get(int(user_id))