import unicodedata

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from handlink.ext.db import db
from handlink.forms.auth import AppointmentForm
from handlink.models import Appointment, Category, Service


bp_services = Blueprint("services", __name__)


def slugify(value):
    text = unicodedata.normalize("NFKD", value or "")
    text = text.encode("ascii", "ignore").decode("ascii")
    return "-".join(text.lower().split())


def find_category_by_slug(slug):
    categories = Category.query.filter_by(status=True).all()
    for category in categories:
        if slugify(category.name) == slug:
            return category
    return None


@bp_services.route("/servicos/<slug>")
def category(slug):
    category = find_category_by_slug(slug)
    if category is None:
        flash("Categoria nao encontrada.", "warning")
        return render_template(
            "services/category.html",
            category=None,
            services=[],
            slug=slug
        ), 404

    services = (
        Service.query
        .filter_by(category_id=category.id, is_active=True)
        .order_by(Service.name)
        .all()
    )

    return render_template(
        "services/category.html",
        category=category,
        services=services,
        slug=slug
    )


@bp_services.route("/servicos/detalhe/<int:service_id>", methods=["GET", "POST"])
def detail(service_id):
    service = db.get_or_404(Service, service_id)
    form = AppointmentForm()

    if request.method == "POST" and not current_user.is_authenticated:
        flash("Faca login para solicitar um servico.", "warning")
        return redirect(url_for("auth.login", next=request.path))

    if form.validate_on_submit():
        appointment = Appointment(
            client_id=current_user.id,
            service_id=service.id,
            status="Pendente",
            appointment_time=form.appointment_time.data
        )
        db.session.add(appointment)
        db.session.commit()

        flash("Solicitacao enviada com sucesso!", "success")
        return redirect(url_for("user.profile"))

    return render_template(
        "services/detail.html",
        service=service,
        form=form
    )
