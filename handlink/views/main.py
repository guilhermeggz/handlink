from flask import Blueprint, current_app, jsonify, render_template, request

from handlink.models import Service


bp_main = Blueprint("main", __name__)


@bp_main.route("/")
def index():
    current_app.logger.debug("renderizando index html dinamicamente")
    categories = [
        {
            "name": "Eletricista",
            "slug": "eletricista",
            "desc": "Instalacoes, reparos eletricos e manutencao residencial.",
        },
        {
            "name": "Pedreiro",
            "slug": "pedreiro",
            "desc": "Pequenas obras, reformas e reparos estruturais.",
        },
        {
            "name": "Marceneiro",
            "slug": "marceneiro",
            "desc": "Moveis, portas, ajustes e servicos em madeira.",
        },
        {
            "name": "Encanador",
            "slug": "encanador",
            "desc": "Vazamentos, torneiras, caixas d'agua e tubulacoes.",
        },
    ]
    return render_template("main/index.html", categories=categories)


@bp_main.route("/api/servicos/buscar", methods=["GET"])
def buscar_servicos():
    termo_busca = request.args.get("q", "")

    query = Service.query.filter(Service.is_active == True)

    if termo_busca:
        query = query.filter(Service.name.ilike(f"%{termo_busca}%"))

    servicos_encontrados = query.all()

    lista_resultado = []
    for servico in servicos_encontrados:
        cidade = ""
        if servico.city:
            cidade = f"{servico.city.name} - {servico.city.state}"

        lista_resultado.append({
            "id": servico.id,
            "name": servico.name,
            "preco": servico.price,
            "descricao": servico.desc,
            "prestador": servico.provider.name,
            "categoria": servico.category.name,
            "cidade": cidade,
        })

    return jsonify({
        "total_servicos": len(lista_resultado),
        "servicos": lista_resultado
    }), 200
