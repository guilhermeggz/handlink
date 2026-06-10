from flask_admin.contrib.sqla import ModelView
from handlink.models.role_user import RoleUser
from flask_login import current_user
from flask import redirect, url_for, flash

class SecuredModelView(ModelView):
    def is_accessible(self):
        return (current_user.is_authenticated and 
                any(role.name == 'admin' for role in getattr(current_user, 'roles', [])))

    def inaccessible_callback(self, name, **kwargs):
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for('auth.login'))

class UserAdmin(SecuredModelView):  
    column_list = ('id', 'name', 'email', 'provider_status')
    column_searchable_list = ('name', 'email')

    column_filters = ('provider_status',)

    form_columns = ('name', 'email', 'phone', 'cpf', 'cnpj', 'is_active', 'role_associations')

    inline_models = (RoleUser,)

    can_export = True

class CategoryAdmin(SecuredModelView):  
    column_list = ('id', 'name', 'image_file')
    column_searchable_list = ('name',)
    column_filters = ('name',)
    can_export = True
    
    form_columns = ('name', 'desc', 'status')

    column_labels = {
        'name': 'Nome da Categoria',
        'image_file': 'Ícone (FontAwesome)'
    }


class CityAdmin(SecuredModelView):  
    column_list = ('id', 'name', 'state')
    column_searchable_list = ('name', 'state')
    column_filters = ('state',)

    form_columns = ('name', 'state', 'country')

    can_export = True