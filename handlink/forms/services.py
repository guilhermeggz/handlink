from flask_wtf import FlaskForm
from wtforms import FileField, StringField, TextAreaField, DecimalField, SubmitField, SelectField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange
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
        coerce=int,
        validators=[DataRequired(message="Selecione ao menos uma categoria para continuar.")],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

class AnunciarServicoForm(FlaskForm):
    category_id = SelectField(
        "Categoria",
        coerce=int,
        validators=[DataRequired(message="Selecione uma categoria.")],
    )
    city_id = SelectField(
        "Cidade de atendimento",
        coerce=int,
        validators=[DataRequired(message="Selecione uma cidade.")],
    )
    name = StringField(
        "Nome do serviço",
        validators=[DataRequired(message="Dê um título ao seu serviço. Ex: Eletricista residencial")],
    )
    description = TextAreaField(
        "Descrição completa",
        validators=[DataRequired(message="Explique detalhadamente o que você faz.")],
    )
    price_per_hour = DecimalField(
        "Valor por hora (R$)",
        validators=[
            DataRequired(message="Insira o seu valor por hora."),
            NumberRange(min=1.0, message="O valor deve ser maior que R$ 1,00."),
        ],
        places=2,
    )
    photo = FileField(
        "Foto do seu serviço (opcional)",
        validators=[
            FileAllowed(["jpg", "jpeg", "png"], "Apenas imagens nos formatos JPG ou PNG são permitidas!"),
        ],
    )
    submit = SubmitField("Publicar anúncio")
