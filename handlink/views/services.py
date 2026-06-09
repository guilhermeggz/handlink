from types import SimpleNamespace

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

from handlink.ext.db import db
from handlink.forms.services import AnunciarServicoForm
from handlink.models import Category, City, Service

bp_services = Blueprint("services", __name__)

FALLBACK_CATEGORIES = {
    1: "Limpeza",
    2: "Eletricidade",
    3: "Encanamento",
    4: "Montagem",
    5: "Pintura",
    6: "Frete",
}


def set_service_form_choices(form):
    categories = (
        Category.query
        .filter(Category.status == True)
        .order_by(Category.name.asc())
        .all()
    )
    cities = City.query.order_by(City.name.asc()).all()

    form.category_id.choices = [(category.id, category.name) for category in categories]
    form.city_id.choices = [
        (city.id, f"{city.name} - {city.state}" if city.state else city.name)
        for city in cities
    ]


@bp_services.route('/servicos/categoria/<int:category_id>')
def services_by_category(category_id):
    category = Category.query.get(category_id)

    if not category and category_id in FALLBACK_CATEGORIES:
        category = SimpleNamespace(id=category_id, name=FALLBACK_CATEGORIES[category_id])
        return render_template(
            'main/services.html',
            category=category,
            services=[],
        )

    if not category:
        abort(404)

    services = (
        Service.query
        .filter(Service.category_id == category.id)
        .filter(Service.is_active == True)
        .order_by(Service.name.asc())
        .all()
    )

    return render_template(
        'main/services.html',
        category=category,
        services=services,
    )


@bp_services.route('/api/categorias', methods=['GET'])
def listar_categorias():
    categories = (
        Category.query
        .filter(Category.status == True)
        .order_by(Category.name.asc())
        .all()
    )

    return jsonify({
        "total_categorias": len(categories),
        "categorias": [
            {
                "id": category.id,
                "name": category.name,
                "description": category.desc,
            }
            for category in categories
        ],
    }), 200


@bp_services.route('/api/servicos/buscar', methods=['GET'])
def buscar_servicos():
    termo_busca = request.args.get('q', '')

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
            "cidade": f"{servico.city.name} - {servico.city.state}",
        })

    return jsonify({
        "total_servicos": len(lista_resultado),
        "servicos": lista_resultado,
    }), 200


@bp_services.route('/servicos/anunciar_servico', methods=['GET', 'POST'])
def anunciar_servico():
    if not current_user.is_authenticated:
        flash('Faça login ou cadastre-se rapidinho para anunciar seu serviço.', 'info')
        return redirect(url_for('auth.login', next=request.path))

    form = AnunciarServicoForm()
    set_service_form_choices(form)

    if not form.category_id.choices or not form.city_id.choices:
        flash('Cadastre ao menos uma categoria e uma cidade antes de anunciar um serviço.', 'warning')

    if form.validate_on_submit():
        service = Service(
            provider_id=current_user.id,
            category_id=form.category_id.data,
            city_id=form.city_id.data,
            name=form.name.data,
            desc=form.description.data,
            price=form.price_per_hour.data,
            is_active=True,
        )

        db.session.add(service)
        db.session.commit()

        flash('Serviço anunciado com sucesso!', 'success')
        return redirect(url_for('services.services_by_category', category_id=service.category_id))

    return render_template('main/create_service.html', form=form)
