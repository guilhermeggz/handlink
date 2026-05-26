from flask import Blueprint, render_template, current_app, flash, redirect, url_for, abort, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user

from handlink.models import User
from handlink.ext.db import db
from handlink.forms.auth import SignUpForm, LoginForm


bp_auth = Blueprint("auth", __name__)

@bp_auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = SignUpForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("Este e-mail já está em uso.", "danger")
            return redirect(url_for("auth.signup"))
        
        user = User.query.filter_by(cpf=form.cpf.data).first()
        if user:
            flash("Este CPF já foi cadastrado.", "danger")
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

            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('main.index'))
        
        except Exception as e:
            db.session.rollback(),
            flash('Ocorreu um erro ao criar sua conta. Por favor, tente novamente.', 'danger')
            return redirect(url_for('auth.signup'))
    
    return render_template(
        'auth/signup.html',
        form=form
    )

@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('E-mail ou senha inválidos.', 'danger')

    return render_template(
        'auth/login.html',
        form=form
    )

@bp_auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('main.index'))