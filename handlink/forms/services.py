from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileAllowed

class AnunciarServicoForm(FlaskForm):
    name = StringField(
        'Nome do Serviço', 
        validators=[DataRequired(message="Dê um título ao seu serviço. Ex: Eletricista Residencial")]
    )
    description = TextAreaField(
        'Descrição Completa', 
        validators=[DataRequired(message="Explique detalhadamente o que você faz.")]
    )
    price_per_hour = DecimalField(
        'Valor por Hora (R$)', 
        validators=[
            DataRequired(message="Insira o seu valor por hora."),
            NumberRange(min=1.0, message="O valor deve ser maior que R$ 1,00.")
        ],
        places=2
    )
    photos = MultipleFileField(
        'Fotos do seu Serviço (Opcional)',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png'], 'Apenas imagens nos formatos JPG ou PNG são permitidas!')
        ]
    )
    submit = SubmitField('Publicar Anúncio')