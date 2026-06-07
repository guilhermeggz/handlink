from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from handlink.ext.db import db
from handlink.forms.auth import LoginForm, SignUpForm
from handlink.models import User


bp_auth = Blueprint("auth", __name__)


@bp_auth.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = SignUpForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("Este e-mail ja esta em uso.", "danger")
            return redirect(url_for("auth.signup"))

        user = User.query.filter_by(cpf=form.cpf.data).first()
        if user:
            flash("Este CPF ja foi cadastrado.", "danger")
            return redirect(url_for("auth.signup"))

        new_user = User(
            name=form.name.data,
            email=form.email.data,
            cpf=form.cpf.data
        )
        new_user.set_password(form.password.data)

        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("main.index"))

        except Exception:
            db.session.rollback()
            flash("Ocorreu um erro ao criar sua conta. Por favor, tente novamente.", "danger")
            return redirect(url_for("auth.signup"))

    return render_template("auth/signup.html", form=form)


@bp_auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.index"))

        flash("E-mail ou senha invalidos.", "danger")

    return render_template("auth/login.html", form=form)


@bp_auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Voce saiu da sua conta.", "success")
    return redirect(url_for("main.index"))
