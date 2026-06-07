from decimal import Decimal

import pytest

from app import create_app
from handlink.ext.db import db
from handlink.models import Category, City, Service, User


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test.db"
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        "SECRET_KEY": "test",
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
        client_user.set_password("senha123")

        provider = User(
            name="Maria Eletricista",
            email="maria@example.com",
            phone="27988880000",
            cpf="10987654321",
        )
        provider.set_password("senha123")

        category = Category(
            name="Eletricista",
            desc="Servicos eletricos residenciais.",
            status=True,
        )
        city = City(
            name="Vitoria",
            state="ES",
            country="Brasil",
            region="Sudeste",
        )

        db.session.add_all([client_user, provider, category, city])
        db.session.commit()

        service = Service(
            provider_id=provider.id,
            category_id=category.id,
            city_id=city.id,
            name="Instalacao de tomada",
            desc="Instalacao e troca de tomadas residenciais.",
            price=Decimal("120.00"),
            is_active=True,
        )
        db.session.add(service)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(client):
    client.post("/login", data={
        "email": "cliente@example.com",
        "password": "senha123",
    })
    return client
