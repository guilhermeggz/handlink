from datetime import datetime, timedelta
from types import SimpleNamespace

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from handlink.forms.services import AnunciarServicoForm, CadastrarPrestadorForm
# Importando os novos forms criados
from handlink.forms.appointments import AgendarServicoForm, ProviderAppointmentActionForm, ClientAppointmentActionForm

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
    
    provider_status = current_user.provider_status()
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

@bp_services.route('/seja_prestador', methods=['GET', 'POST'])
def seja_prestador():
    if not current_user.is_authenticated:
        flash('Faça login ou cadastre-se rapidinho para se tornar um prestador.', 'info')
        return redirect(url_for('auth.login', next=request.path))
    
    form = CadastrarPrestadorForm()
    
    categorias_do_banco = Category.query.filter_by(status=True).all()
    form.categories.choices = [(c.id, c.name) for c in categorias_do_banco]

    provider_status = current_user.provider_status()
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
            provider_status=ProviderStatus.APROVADO
        )
        db.session.add(nova_associacao)
        db.session.commit()

        flash('Sua solicitação para ser prestador foi enviada com sucesso e está em análise!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('main/be_a_provider.html', form=form)

@bp_services.route('/servicos/detalhes/<int:service_id>')
def detalhes_servico(service_id):

    service = Service.query.get_or_404(service_id)
    
    return render_template(
        'main/service_details.html', 
        service=service
    )


@bp_services.route('/servicos/agendar/<int:service_id>', methods=['GET', 'POST'])
@login_required # Garante que apenas clientes logados acessem
def agendar_servico(service_id):
    service = Service.query.get_or_404(service_id)
    
    # Bloqueia se o prestador tentar agendar o próprio serviço
    if service.provider_id == current_user.id:
        flash('Você não pode agendar um serviço oferecido por você mesmo.', 'danger')
        return redirect(url_for('services.detalhes_servico', service_id=service.id))
        
    form = AgendarServicoForm()
    
    if form.validate_on_submit():
        data_escolhida = form.appointment_time.data
        tempo_minimo = datetime.now() + timedelta(hours=3)
        
        # VERIFICAÇÃO DE 3 HORAS DE ANTECEDÊNCIA NA CRIAÇÃO
        if data_escolhida < tempo_minimo:
            flash('Por favor, escolha um horário com no mínimo 3 horas de antecedência.', 'warning')
            return render_template('main/request_appointment.html', form=form, service=service)
        
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
        return redirect(url_for('services.meus_agendamentos'))
        
    return render_template('main/request_appointment.html', form=form, service=service)


# ==========================================
# PAINEL DO PROVIDER (Gerenciar Meus Serviços Solicitados)
# ==========================================

@bp_services.route('/painel-prestador', methods=['GET', 'POST'])
@login_required
def painel_prestador():
    # Segurança: Garante que ele possui perfil ou role de provider ativo
    if not any(assoc.role.name == 'provider' and assoc.provider_status == ProviderStatus.APROVADO for assoc in current_user.role_associations):
        flash('Acesso restrito a prestadores aprovados.', 'warning')
        return redirect(url_for('main.index'))

    form = ProviderAppointmentActionForm()

    # Processa o formulário de atualização de status via POST
    if form.validate_on_submit():
        appointment = Appointment.query.get_or_404(form.appointment_id.data)
        
        # Segurança: Garante que o agendamento é para um serviço deste provedor
        if appointment.service.provider_id != current_user.id:
            abort(403)
            
        # O validate_on_submit já garante que form.status.data é uma opção válida do SelectField
        novo_status = form.status.data 

        appointment.status = novo_status
        db.session.commit()
        flash(f'Agendamento atualizado para {novo_status} com sucesso!', 'success')
            
        return redirect(url_for('services.painel_prestador'))
    
    # Exibe erros de validação, se houver, de forma sutil
    elif form.errors:
        flash('Erro ao atualizar agendamento. Verifique os dados.', 'danger')

    # Processa a listagem via GET
    agendamentos = (
        Appointment.query
        .join(Service)
        .filter(Service.provider_id == current_user.id)
        .order_by(Appointment.appointment_time.asc())
        .all()
    )
    return render_template('main/provider_panel.html', agendamentos=agendamentos, form=form)


# ==========================================
# PAINEL DO CLIENTE (Meus Agendamentos)
# ==========================================
# (As rotas do cliente já estavam praticamente corretas, apenas mantive o padrão)

@bp_services.route('/meus-agendamentos', methods=['GET', 'POST'])
@login_required
def meus_agendamentos():
    form = ClientAppointmentActionForm()
    
    if form.validate_on_submit():
        appointment = Appointment.query.get_or_404(form.appointment_id.data)
        
        if appointment.client_id != current_user.id:
            abort(403)
            
        if appointment.pode_modificar:
            appointment.status = 'Cancelado'
            db.session.commit()
            flash('Agendamento cancelado com sucesso.', 'success')
        else:
            flash('Não é possível cancelar com menos de 3 dias de antecedência.', 'danger')
            
        return redirect(url_for('services.meus_agendamentos'))

    agendamentos = Appointment.query.filter_by(client_id=current_user.id).order_by(Appointment.appointment_time.desc()).all()
    return render_template('main/my_appointments.html', agendamentos=agendamentos, form=form)



@bp_services.route('/agendamento/<int:id>/alterar', methods=['POST'])
@login_required
def alterar_agendamento_cliente(id):
    appointment = Appointment.query.get_or_404(id)
    if appointment.client_id != current_user.id:
        abort(403)
        
    if not appointment.pode_modificar:
        flash('Não é possível alterar dados com menos de 3 dias de antecedência.', 'danger')
        return redirect(url_for('services.meus_agendamentos'))
        
    nova_data_str = request.form.get('appointment_time')
    novas_horas = request.form.get('hours')
    
    if nova_data_str:
        nova_data = datetime.strptime(nova_data_str, '%Y-%m-%dT%H:%M')
        
        tempo_minimo = datetime.now() + timedelta(hours=3)
        
        if nova_data < tempo_minimo:
            flash('O agendamento precisa ser marcado com pelo menos 3 horas de antecedência.', 'warning')
            return redirect(url_for('services.meus_agendamentos'))
            
        appointment.appointment_time = nova_data

    if novas_horas:
        appointment.hours = int(novas_horas)
        
    db.session.commit()
    flash('Agendamento atualizado com sucesso!', 'success')
    return redirect(url_for('services.meus_agendamentos'))