from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import DecimalField, MultipleFileField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange


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
    photos = MultipleFileField(
        "Fotos do seu serviço (opcional)",
        validators=[
            FileAllowed(["jpg", "jpeg", "png"], "Apenas imagens nos formatos JPG ou PNG são permitidas!"),
        ],
    )
    submit = SubmitField("Publicar anúncio")
