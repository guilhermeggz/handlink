from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, TextAreaField, DecimalField, SubmitField, FileField, widgets
from wtforms.validators import DataRequired, NumberRange, ValidationError, Length
from flask_wtf.file import FileAllowed

def apenas_numeros(form, field):
    if not field.data.isdigit():
        raise ValidationError("O CNPJ deve conter apenas números.")

class CadastrarPrestadorForm(FlaskForm):
    cnpj = StringField(
        'CNPJ', 
        validators=[
            DataRequired(message="Insira seu CNPJ para se cadastrar como prestador."),
            Length(min=14, max=14, message="O CNPJ deve ter exatamente 14 dígitos."),
            apenas_numeros
        ]
    )
    
    categories = SelectMultipleField(
        'Em quais categorias você trabalha?',
        coerce=int,  # Garante que o ID da categoria seja tratado como número inteiro
        validators=[DataRequired(message="Selecione ao menos uma categoria para continuar.")],
        widget=widgets.ListWidget(prefix_label=False), # Organiza em lista
        option_widget=widgets.CheckboxInput()          # Transforma cada opção em um checkbox
    )


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
    photo = FileField(
        'Fotos do seu Serviço (Opcional)',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png'], 'Apenas imagens nos formatos JPG ou PNG são permitidas!')
        ]
    )
    submit = SubmitField('Publicar Anúncio')