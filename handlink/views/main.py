from flask import Blueprint, render_template, current_app, flash, redirect, url_for, abort, jsonify, request
from handlink.models import Service, User, RoleUser, Role
from handlink.ext.db import db

#from handlink.forms.main import Formulario

bp_main = Blueprint("main", __name__)

def index():
    current_app.logger.debug('renderizando index html dinamicamente')

    return render_template(
        'main/index.html'
    )

@bp_main.route('/api/cadastro/<string:nome>/<string:r_email>/<string:senha>/<string:r_cpf>')
def cadastro(nome, r_email, senha, r_cpf):
    if r_email:
        user = User.query.filter_by(email=r_email).first()
        if user:
            return jsonify({
                "ERRO": "Email ja cadastrado"
            }), 422
    if r_cpf:
        user = User.query.filter_by(cpf=r_cpf).first()
        if user:
            return jsonify({
                "ERRO": "CPF ja cadastrado"
            }), 422
    
    new_user = User(name=nome, email=r_email, password=senha, cpf=r_cpf)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "Mensagem": f"Usuário cadastrado com sucesso!",
        "Nome": nome,
        "E-mail": r_email
    }), 201

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