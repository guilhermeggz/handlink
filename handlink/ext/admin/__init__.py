from flask_admin import Admin

from handlink.ext.admin.views import UserAdmin, CategoryAdmin, CityAdmin
from handlink.models.user import User
from handlink.models.category import Category
from handlink.models.location import City
from handlink.ext.db import db

admin = Admin(name="HandLink Admin")

def init_app(app):
    admin.init_app(app)
    
    admin.add_view(UserAdmin(User, db.session, name='Verificar Usuários', endpoint='admin_users'))
    admin.add_view(CategoryAdmin(Category, db.session, name='Categorias', category='Gerenciamento do Sistema'))
    admin.add_view(CityAdmin(City, db.session, name='Cidades', category='Gerenciamento do Sistema'))