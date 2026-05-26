from flask import (
    Blueprint, render_template, current_app,
    flash, redirect, url_for,
    abort, jsonify, request,
)
from handlink.models import Service, User, RoleUser, Role
from handlink.ext.db import db
from handlink.forms.main import SignUpForm, LoginForm

bp_main = Blueprint("main", __name__)

@bp_main.route('/')
def index():
    current_app.logger.debug('renderizando index html dinamicamente')

    return render_template(
        'main/index.html'
    )

@bp_main.route('/api/servicos/buscar', methods=['GET'])
def buscar_servicos():
    termo_busca = request.args.get('q','')

    query = Service.query.filter(Service.is_active == True)

    if termo_busca:
        query = query.filter(Service.name.ilike(f'%{termo_busca}%'))

    servicos_encontrados = query.all()

    lista_resultado = []
    for servico in servicos_encontrados:
        lista_resultado.append({
            "id": servico.id,
            "name": servico.name,
            "preco": servico.price,
            "descricao": servico.desc,

            "prestador": servico.provider.name,
            "categoria": servico.category.name,
            "cidade": f"{servico.city.name} - {servico.city.state}"
        })

    return jsonify({
        "total_servicos": len(lista_resultado),
        "servicos": lista_resultado
    }), 200