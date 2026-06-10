from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from app import create_app
from handlink.ext.db import db
from handlink.models import Category, City, Role, RoleUser, Service, User
from handlink.models.role_user import ProviderStatus


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "handlink_test.db"

    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        "SECRET_KEY": "test-secret-key",
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

        client_user = User(
            name="Cliente Teste",
            email="cliente@example.com",
            phone="27999990000",
            cpf="12345678901",
        )
        client_user.set_password("senha1234")

        provider_user = User(
            name="Maria Eletricista",
            email="maria@example.com",
            phone="27988880000",
            cpf="10987654321",
        )
        provider_user.set_password("senha1234")

        provider_role = Role(name="provider", status=True)
        category = Category(
            name="Eletricidade",
            desc="Servicos eletricos residenciais.",
            status=True,
        )
        city = City(
            name="Vitoria",
            state="ES",
            country="Brasil",
            region="Sudeste",
        )

        db.session.add_all([client_user, provider_user, provider_role, category, city])
        db.session.commit()

        db.session.add(RoleUser(
            user_id=provider_user.id,
            role_id=provider_role.id,
            provider_status=ProviderStatus.APROVADO,
        ))
        db.session.commit()

        active_service = Service(
            provider_id=provider_user.id,
            category_id=category.id,
            city_id=city.id,
            name="Instalacao de tomada",
            desc="Instalacao e troca de tomadas residenciais.",
            price=Decimal("120.00"),
            is_active=True,
        )
        inactive_service = Service(
            provider_id=provider_user.id,
            category_id=category.id,
            city_id=city.id,
            name="Servico inativo",
            desc="Este servico nao deve aparecer na listagem.",
            price=Decimal("99.00"),
            is_active=False,
        )
        db.session.add_all([active_service, inactive_service])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(client):
    login(client)
    return client


@pytest.fixture()
def future_appointment_time():
    return (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%dT%H:%M")


def login(client, email="cliente@example.com", password="senha1234"):
    return client.post("/login", data={
        "email": email,
        "password": password,
    })
