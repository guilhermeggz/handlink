import os
import secrets
from datetime import datetime, timedelta
from types import SimpleNamespace

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from handlink.forms.appointments import ProviderAppointmentActionForm, ClientAppointmentActionForm

from handlink.ext.db import db
from handlink.models import Service, Appointment
from handlink.models.role_user import ProviderStatus
from handlink.models.user import User

bp_appointments = Blueprint("appointments", __name__)

@bp_appointments.route('/painel-prestador', methods=['GET', 'POST'])
@login_required
def painel_prestador():
    if not any(assoc.role.name == 'provider' and assoc.provider_status == ProviderStatus.APROVADO for assoc in current_user.role_associations):
        flash('Acesso restrito a prestadores aprovados.', 'warning')
        return redirect(url_for('main.index'))

    form = ProviderAppointmentActionForm()

    if form.validate_on_submit():
        appointment = Appointment.query.get_or_404(form.appointment_id.data)
        
        if appointment.service.provider_id != current_user.id:
            abort(403)
            
        novo_status = form.status.data 

        appointment.status = novo_status
        db.session.commit()
        flash(f'Agendamento atualizado para {novo_status} com sucesso!', 'success')
            
        return redirect(url_for('appointments.painel_prestador'))
    
    elif form.errors:
        flash('Erro ao atualizar agendamento. Verifique os dados.', 'danger')

    agendamentos = (
        Appointment.query
        .join(Service)
        .filter(Service.provider_id == current_user.id)
        .order_by(Appointment.appointment_time.asc())
        .all()
    )
    return render_template('main/provider/provider_panel.html', agendamentos=agendamentos, form=form)


@bp_appointments.route('/meus-agendamentos', methods=['GET', 'POST'])
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
            
        return redirect(url_for('appointments.meus_agendamentos'))

    agendamentos = Appointment.query.filter_by(client_id=current_user.id).order_by(Appointment.appointment_time.desc()).all()
    return render_template('main/appointment/my_appointments.html', agendamentos=agendamentos, form=form)


@bp_appointments.route('/agendamento/<int:id>/alterar', methods=['POST'])
@login_required
def alterar_agendamento_cliente(id):
    appointment = Appointment.query.get_or_404(id)
    if appointment.client_id != current_user.id:
        abort(403)
        
    if not appointment.pode_modificar:
        flash('Não é possível alterar dados com menos de 3 dias de antecedência.', 'danger')
        return redirect(url_for('appointments.meus_agendamentos'))
        
    nova_data_str = request.form.get('appointment_time')
    novas_horas = request.form.get('hours')
    
    if nova_data_str:
        nova_data = datetime.strptime(nova_data_str, '%Y-%m-%dT%H:%M')
        
        tempo_minimo = datetime.now() + timedelta(hours=3)
        
        if nova_data < tempo_minimo:
            flash('O agendamento precisa ser marcado com pelo menos 3 horas de antecedência.', 'warning')
            return redirect(url_for('appointments.meus_agendamentos'))
            
        appointment.appointment_time = nova_data

    if novas_horas:
        appointment.hours = int(novas_horas)
        
    db.session.commit()
    flash('Agendamento atualizado com sucesso!', 'success')
    return redirect(url_for('appointments.meus_agendamentos'))