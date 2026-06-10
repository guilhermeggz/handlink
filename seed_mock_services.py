from decimal import Decimal

from app import create_app
from handlink.ext.db import db
from handlink.models import Category, City, Role, RoleUser, Service, User


MOCK_CATEGORIES = [
    {
        "name": "Limpeza",
        "desc": "Faxinas, limpezas pesadas e organização.",
        "service": "Faxina residencial completa",
        "service_desc": "Limpeza detalhada para casas e apartamentos, com organização dos principais ambientes.",
        "price": "120.00",
        "provider": "Ana Souza",
        "email": "ana.limpeza@handlink.com",
        "cpf": "10000000001",
        "phone": "27990000001",
    },
    {
        "name": "Eletricidade",
        "desc": "Instalações, reparos elétricos e manutenção residencial.",
        "service": "Instalação de chuveiro elétrico",
        "service_desc": "Instalação segura de chuveiros, tomadas, disjuntores e pequenos reparos elétricos.",
        "price": "150.00",
        "provider": "Marcos Lima",
        "email": "marcos.eletrica@handlink.com",
        "cpf": "10000000002",
        "phone": "27990000002",
    },
    {
        "name": "Encanamento",
        "desc": "Reparos hidráulicos, vazamentos e desentupimentos.",
        "service": "Reparo de vazamento",
        "service_desc": "Correção de vazamentos, troca de sifões, torneiras e manutenção hidráulica simples.",
        "price": "95.00",
        "provider": "Carlos Mendes",
        "email": "carlos.hidraulica@handlink.com",
        "cpf": "10000000003",
        "phone": "27990000003",
    },
    {
        "name": "Montagem",
        "desc": "Montagem e desmontagem de móveis residenciais.",
        "service": "Montagem de móveis planejados",
        "service_desc": "Montagem de guarda-roupas, mesas, painéis, estantes e móveis compactos.",
        "price": "180.00",
        "provider": "Rafael Costa",
        "email": "rafael.montagem@handlink.com",
        "cpf": "10000000004",
        "phone": "27990000004",
    },
    {
        "name": "Pintura",
        "desc": "Pintura residencial, pequenos acabamentos e retoques.",
        "service": "Pintura de cômodo",
        "service_desc": "Pintura interna com preparação da parede, acabamento limpo e orientação de materiais.",
        "price": "250.00",
        "provider": "Beatriz Rocha",
        "email": "beatriz.pintura@handlink.com",
        "cpf": "10000000005",
        "phone": "27990000005",
    },
    {
        "name": "Frete",
        "desc": "Transporte de pequenos volumes, mudanças rápidas e entregas.",
        "service": "Frete urbano pequeno",
        "service_desc": "Transporte de móveis pequenos, caixas e objetos em rotas urbanas.",
        "price": "140.00",
        "provider": "João Pereira",
        "email": "joao.frete@handlink.com",
        "cpf": "10000000006",
        "phone": "27990000006",
    },
]


def get_or_create_role(name):
    role = Role.query.filter_by(name=name).first()
    if role:
        role.status = True
        return role

    role = Role(name=name, status=True)
    db.session.add(role)
    db.session.flush()
    return role


def get_or_create_city():
    city = City.query.filter_by(name="Vila Velha", state="ES").first()
    if city:
        return city

    city = City(name="Vila Velha", state="ES", country="Brasil", region="Sudeste")
    db.session.add(city)
    db.session.flush()
    return city


def get_or_create_category(name, desc):
    category = Category.query.filter_by(name=name).first()
    if category:
        category.desc = desc
        category.status = True
        return category

    category = Category(name=name, desc=desc, status=True)
    db.session.add(category)
    db.session.flush()
    return category


def get_or_create_provider(mock, provider_role):
    provider = User.query.filter_by(email=mock["email"]).first()
    if provider:
        provider.name = mock["provider"]
        provider.phone = mock["phone"]
        provider.is_active = True
    else:
        provider = User(
            name=mock["provider"],
            email=mock["email"],
            cpf=mock["cpf"],
            phone=mock["phone"],
            is_active=True,
        )
        provider.set_password("12345678")
        db.session.add(provider)
        db.session.flush()

    association = RoleUser.query.filter_by(
        user_id=provider.id,
        role_id=provider_role.id,
    ).first()
    if association:
        association.service_provider_status = "Aprovado"
    else:
        db.session.add(RoleUser(
            user_id=provider.id,
            role_id=provider_role.id,
            service_provider_status="Aprovado",
        ))

    return provider


def upsert_service(mock, provider, category, city):
    service = Service.query.filter_by(
        provider_id=provider.id,
        category_id=category.id,
        name=mock["service"],
    ).first()

    if not service:
        service = Service(
            provider_id=provider.id,
            category_id=category.id,
            city_id=city.id,
            name=mock["service"],
        )
        db.session.add(service)

    service.desc = mock["service_desc"]
    service.price = Decimal(mock["price"])
    service.city_id = city.id
    service.is_active = True

    return service


def run_mock_seed():
    app = create_app()

    with app.app_context():
        provider_role = get_or_create_role("Prestador")
        city = get_or_create_city()

        for mock in MOCK_CATEGORIES:
            category = get_or_create_category(mock["name"], mock["desc"])
            provider = get_or_create_provider(mock, provider_role)
            upsert_service(mock, provider, category, city)

        db.session.commit()
        print("Mock de serviços criado com sucesso.")
        print(f"{len(MOCK_CATEGORIES)} categorias com 1 serviço cada foram preparadas.")


if __name__ == "__main__":
    run_mock_seed()
