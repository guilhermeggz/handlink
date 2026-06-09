from flask_wtf import FlaskForm
from validate_docbr import CPF
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


class SignUpForm(FlaskForm):
    name = StringField(
        "Nome Completo",
        validators=[DataRequired()],
        render_kw={"placeholder": "João da Silva"},
    )

    email = StringField(
        "E-mail",
        validators=[
            DataRequired(),
            Email(
                message="Por favor, insira um endereço de e-mail válido.",
                check_deliverability=True,
            ),
        ],
        render_kw={"placeholder": "nome@exemplo.com"},
    )

    password = PasswordField(
        "Senha",
        validators=[DataRequired(), Length(min=8)],
    )

    confirm_password = PasswordField(
        "Confirmar Senha",
        validators=[
            DataRequired(),
            EqualTo("password", message="As senhas devem coincidir"),
        ],
    )

    cpf = StringField(
        "CPF",
        validators=[DataRequired(), Length(min=11, max=11)],
        render_kw={"placeholder": "00000000000"},
    )

    def validate_cpf(self, field):
        cpf = field.data
        if not cpf.isdigit():
            raise ValidationError("O CPF deve conter apenas números.")

        validator = CPF()
        if not validator.validate(cpf):
            raise ValidationError("CPF inválido.")

    submit = SubmitField("Cadastrar")


class LoginForm(FlaskForm):
    email = StringField(
        "E-mail",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "nome@exemplo.com"},
    )
    password = PasswordField(
        "Senha",
        validators=[DataRequired(), Length(min=8)],
    )
    submit = SubmitField("Login")
