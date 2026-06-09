from types import SimpleNamespace

from flask import Blueprint, abort, jsonify, render_template, request

from handlink.models import Category, Service

bp_services = Blueprint("services", __name__)

FALLBACK_CATEGORIES = {
    1: "Limpeza",
    2: "Eletricidade",
    3: "Encanamento",
    4: "Montagem",
    5: "Pintura",
    6: "Frete",
}


@bp_services.route('/servicos/categoria/<int:category_id>')
def services_by_category(category_id):
    category = Category.query.get(category_id)

    if not category and category_id in FALLBACK_CATEGORIES:
        category = SimpleNamespace(id=category_id, name=FALLBACK_CATEGORIES[category_id])
        services = []
        return render_template(
            'main/services.html',
            category=category,
            services=services,
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
