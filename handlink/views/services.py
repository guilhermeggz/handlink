import os
import secrets
from datetime import datetime, timedelta
from types import SimpleNamespace

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

from handlink.forms.services import AnunciarServicoForm, CadastrarPrestadorForm
from handlink.forms.appointments import AgendarServicoForm

from handlink.ext.db import db
from handlink.models import Category, City, Role, RoleUser, Service, Appointment
from handlink.models.role_user import ProviderStatus
from handlink.models.user import User

bp_services = Blueprint("services", __name__)

FALLBACK_CATEGORIES = {
    1: "Limpeza",
    2: "Eletricidade",
    3: "Encanamento",
    4: "Montagem",
    5: "Pintura",
    6: "Frete",
}

def save_uploaded_photo(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    picture_path = os.path.join(current_app.root_path, 'static/uploads', picture_fn)

    form_picture.save(picture_path)

    return picture_fn

def set_service_form_choices(form):
    categories = current_user.worked_categories
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
            'main/service/services.html',
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
        'main/service/services.html',
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


@bp_services.route('/api/servicos/em-alta', methods=['GET'])
def servicos_em_alta():
    limit = min(request.args.get('limit', 4, type=int), 24)
    offset = max(request.args.get('offset', 0, type=int), 0)

    query = (
        Service.query
        .filter(Service.is_active == True)
        .order_by(Service.created_at.desc(), Service.name.asc())
    )

    total_servicos = query.count()
    services = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return jsonify({
        "total_servicos": total_servicos,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(services) < total_servicos,
        "servicos": [
            serialize_service(service)
            for service in services
        ],
    }), 200


@bp_services.route('/api/servicos/buscar', methods=['GET'])
def buscar_servicos():
    termo_busca = request.args.get('q', '')

    query = Service.query.filter(Service.is_active == True)

    if termo_busca:
        query = query.filter(Service.name.ilike(f'%{termo_busca}%'))

    servicos_encontrados = query.all()

    return jsonify({
        "total_servicos": len(servicos_encontrados),
        "servicos": [
            serialize_service(servico)
            for servico in servicos_encontrados
        ],
    }), 200


def serialize_service(service):
    return {
        "id": service.id,
        "name": service.name,
        "preco": service.price,
        "descricao": service.desc,
        "prestador": service.provider.name,
        "categoria": service.category.name,
        "categoria_id": service.category.id,
        "cidade": f"{service.city.name} - {service.city.state}",
    }


@bp_services.route('/servicos/anunciar_servico', methods=['GET', 'POST'])
def anunciar_servico():
    if not current_user.is_authenticated:
        flash('Faça login ou cadastre-se rapidinho para anunciar seu serviço.', 'info')
        return redirect(url_for('auth.login', next=request.path))
    
    provider_status = current_user.provider_status
    current_app.logger.debug(f"Status do usuário {current_user.email} como provider: {provider_status}")
    
    match provider_status:
        case ProviderStatus.PENDENTE:
            flash('Sua solicitação de prestador está pendente. Aguarde a aprovação.', 'info')
            return redirect(url_for('main.index'))
            
        case ProviderStatus.APROVADO:
            pass
        
        case ProviderStatus.REPROVADO:
            flash('Sua solicitação de prestador foi reprovada. Entre em contato para mais informações.', 'danger')
            return redirect(url_for('main.index'))

        case _:
            flash('Cadastre-se como prestador para anunciar seus serviços.', 'warning')
            return redirect(url_for('services.seja_prestador'))

    form = AnunciarServicoForm()
    set_service_form_choices(form)

    if not form.category_id.choices or not form.city_id.choices:
        flash('Cadastre ao menos uma categoria e uma cidade antes de anunciar um serviço.', 'warning')

    if form.validate_on_submit():
        if form.photo.data:
            try:
                photo_filename = save_uploaded_photo(form.photo.data)
            except Exception as e:
                current_app.logger.error(f"Erro ao salvar foto do serviço: {e}")
                flash('Houve um erro ao processar a foto. Tente novamente.', 'danger')
                return render_template('main/create_service.html', form=form)
            
        service = Service(
            provider_id=current_user.id,
            category_id=form.category_id.data,
            city_id=form.city_id.data,
            name=form.name.data,
            desc=form.description.data,
            price=form.price_per_hour.data,
            is_active=True,
            photo=photo_filename if 'photo_filename' in locals() else None
        )

        db.session.add(service)
        db.session.commit()

        flash('Serviço anunciado com sucesso!', 'success')
        return redirect(url_for('services.services_by_category', category_id=service.category_id))

    return render_template('main/service/create_service.html', form=form)

@bp_services.route('/seja_prestador', methods=['GET', 'POST'])
def seja_prestador():
    if not current_user.is_authenticated:
        flash('Faça login ou cadastre-se rapidinho para se tornar um prestador.', 'info')
        return redirect(url_for('auth.login', next=request.path))
    
    form = CadastrarPrestadorForm()
    
    categorias_do_banco = Category.query.filter_by(status=True).all()
    form.categories.choices = [(c.id, c.name) for c in categorias_do_banco]

    provider_status = current_user.provider_status
    current_app.logger.debug(f"Status do usuário {current_user.email} como provider: {provider_status}")

    match provider_status:
        case ProviderStatus.PENDENTE:
            flash('Sua solicitação de prestador está pendente. Aguarde a aprovação.', 'info')
            return redirect(url_for('main.index'))
        
        case ProviderStatus.APROVADO:
            flash('Você já é um prestador aprovado! Comece a anunciar seus serviços.', 'success')
            return redirect(url_for('services.anunciar_servico'))
        
        case ProviderStatus.REPROVADO:
            flash('Sua solicitação de prestador foi reprovada. Entre em contato para mais informações.', 'danger')
            return redirect(url_for('main.index'))
            
        case _:
            pass

    if form.validate_on_submit():
        user = User.query.filter_by(cnpj=form.cnpj.data).first()
        if user:
            flash("Este CNPJ foi cadastrado.", "danger")
            return redirect(url_for("services.seja_prestador"))
        
        current_user.cnpj = form.cnpj.data

        categorias_selecionadas = Category.query.filter(Category.id.in_(form.categories.data)).all()

        current_user.worked_categories = categorias_selecionadas

        provider_role = Role.query.filter_by(name="provider").first()
        if not provider_role:
            provider_role = Role(name="provider", status=True)
            db.session.add(provider_role)
            db.session.flush()

        nova_associacao = RoleUser(
            user=current_user,
            role=provider_role,
            provider_status=ProviderStatus.PENDENTE
        )
        db.session.add(nova_associacao)
        db.session.commit()

        flash('Sua solicitação para ser prestador foi enviada com sucesso e está em análise!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('main/provider/be_a_provider.html', form=form)

@bp_services.route('/servicos/detalhes/<int:service_id>')
def detalhes_servico(service_id):

    service = Service.query.get_or_404(service_id)
    
    return render_template(
        'main/service/service_details.html', 
        service=service
    )


@bp_services.route('/servicos/agendar/<int:service_id>', methods=['GET', 'POST'])
def agendar_servico(service_id):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.path))
    service = Service.query.get_or_404(service_id)
    
    if service.provider_id == current_user.id:
        flash('Você não pode agendar um serviço oferecido por você mesmo.', 'danger')
        return redirect(url_for('services.detalhes_servico', service_id=service.id))
        
    form = AgendarServicoForm()
    
    if form.validate_on_submit():
        data_escolhida = form.appointment_time.data
        tempo_minimo = datetime.now() + timedelta(hours=3)
        
        if data_escolhida < tempo_minimo:
            flash('Por favor, escolha um horário com no mínimo 3 horas de antecedência.', 'warning')
            return render_template('main/appointment/request_appointment.html', form=form, service=service)
        
        appointment = Appointment(
            client_id=current_user.id,
            service_id=service.id,
            appointment_time=data_escolhida,
            hours=form.hours.data,
            observations=form.observacoes.data,
            status='Pendente'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        flash('Solicitação de agendamento enviada!', 'success')
        return redirect(url_for('appointments.meus_agendamentos'))
        
    return render_template('main/appointment/request_appointment.html', form=form, service=service)