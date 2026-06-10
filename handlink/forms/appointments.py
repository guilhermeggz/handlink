from flask_wtf import FlaskForm
from wtforms import IntegerField, DateTimeLocalField, TextAreaField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class AgendarServicoForm(FlaskForm):
    appointment_time = DateTimeLocalField(
        'Data e Hora do Atendimento',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(message="Por favor, selecione a data e hora para o atendimento.")]
    )
    
    hours = IntegerField(
        'Quantas horas de serviço serão necessárias?',
        validators=[
            DataRequired(message="Informe a quantidade de horas estimadas."),
            NumberRange(min=1, max=24, message="A quantidade de horas deve ser entre 1 e 24.")
        ],
        default=1
    )
    
    observacoes = TextAreaField('Instruções ou observações adicionais (Opcional)')

from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

class ProviderAppointmentActionForm(FlaskForm):
    """Formulário para o provedor alterar o status do agendamento."""
    appointment_id = HiddenField("ID do Agendamento", validators=[DataRequired()])
    
    status = SelectField(
        "Ação",
        choices=[
            ('Confirmado', 'Aceitar Agendamento'),
            ('Finalizado', 'Marcar como Concluído'),
            ('Cancelado', 'Recusar / Cancelar')
        ],
        validators=[DataRequired()]
    )
    
    feedback = TextAreaField("Observações (Opcional)", validators=[Optional()])
    submit = SubmitField("Atualizar Status")


class ClientAppointmentActionForm(FlaskForm):
    """Formulário para o cliente cancelar um agendamento."""
    appointment_id = HiddenField("ID do Agendamento", validators=[DataRequired()])
    submit = SubmitField("Cancelar Agendamento")