from flask_wtf import FlaskForm
from validate_docbr import CPF
from wtforms import PasswordField, StringField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


class SignUpForm(FlaskForm):
    name = StringField(
        "Nome Completo",
        validators=[DataRequired()],
        render_kw={"placeholder": "Joao da Silva"}
    )

    email = StringField(
        "E-mail",
        validators=[
            DataRequired(),
            Email(
                message="Por favor, insira um endereco de e-mail valido.",
                check_deliverability=False
            )
        ],
        render_kw={"placeholder": "nome@exemplo.com"}
    )

    password = PasswordField(
        "Senha",
        validators=[DataRequired(), Length(min=8)]
    )

    confirm_password = PasswordField(
        "Confirmar Senha",
        validators=[DataRequired(), EqualTo("password", message="As senhas devem coincidir")]
    )

    cpf = StringField(
        "CPF",
        validators=[DataRequired(), Length(min=11, max=11)],
        render_kw={"placeholder": "00000000000"}
    )

    def validate_cpf(self, field):
        cpf = field.data
        if not cpf.isdigit():
            raise ValidationError("O CPF deve conter apenas numeros.")

        validator = CPF()
        if not validator.validate(cpf):
            raise ValidationError("CPF invalido.")

    submit = SubmitField("Cadastrar")


class LoginForm(FlaskForm):
    email = StringField(
        "E-mail",
        validators=[DataRequired(), Email(check_deliverability=False)],
        render_kw={"placeholder": "nome@exemplo.com"}
    )
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Login")


class AppointmentForm(FlaskForm):
    appointment_time = DateTimeLocalField(
        "Data e hora",
        validators=[DataRequired()],
        format="%Y-%m-%dT%H:%M",
        render_kw={"type": "datetime-local"}
    )
    submit = SubmitField("Solicitar servico")
