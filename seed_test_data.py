from decimal import Decimal

from app import create_app
from handlink.ext.db import db
from handlink.models import Category, City, Role, RoleUser, Service, User
from handlink.models.role_user import ProviderStatus


DEFAULT_PASSWORD = "12345678"


ROLES = [
    "admin",
    "provider",
]


CATEGORIES = [
    ("Limpeza", "Faxinas, limpeza pesada e organizacao de ambientes."),
    ("Eletricidade", "Instalacoes, manutencao eletrica e pequenos reparos."),
    ("Encanamento", "Consertos hidraulicos, vazamentos e instalacoes."),
    ("Montagem", "Montagem de moveis, suportes e pequenas instalacoes."),
    ("Pintura", "Pintura residencial, retoques e acabamento."),
    ("Frete", "Mudancas pequenas, transporte e entregas locais."),
]


CITIES = [
    ("Vila Velha", "ES", "Brasil", "Sudeste"),
    ("Serra", "ES", "Brasil", "Sudeste"),
    ("Vitoria", "ES", "Brasil", "Sudeste"),
    ("Cariacica", "ES", "Brasil", "Sudeste"),
]


USERS = [
    {
        "name": "Admin HandLink",
        "email": "admin@gmail.com",
        "cpf": "39471245036",
        "phone": "11900000000",
        "roles": ["admin", "provider"],
    },
    {
        "name": "Maria Eletricista",
        "email": "maria.eletricista@gmail.com",
        "cpf": "62289844039",
        "phone": "11911111111",
        "roles": ["provider"],
    },
    {
        "name": "Carlos Encanador",
        "email": "carlos.encanador@gmail.com",
        "cpf": "97442284078",
        "phone": "11922222222",
        "roles": ["provider"],
    },
    {
        "name": "Ana Cliente",
        "email": "ana.cliente@gmail.com",
        "cpf": "20387949011",
        "phone": "11933333333",
        "roles": [],
    },
]


SERVICES = [
    {
        "name": "Faxina completa residencial",
        "desc": "Limpeza detalhada de quartos, sala, cozinha e banheiros.",
        "price": Decimal("120.00"),
        "provider_email": "maria.eletricista@gmail.com",
        "category": "Limpeza",
        "city": ("Vila Velha", "ES"),
    },
    {
        "name": "Instalacao de tomadas e luminarias",
        "desc": "Instalacao e troca de tomadas, interruptores e luminarias.",
        "price": Decimal("150.00"),
        "provider_email": "maria.eletricista@gmail.com",
        "category": "Eletricidade",
        "city": ("Vila Velha", "ES"),
    },
    {
        "name": "Reparo de vazamentos",
        "desc": "Conserto de vazamentos em pias, torneiras e registros.",
        "price": Decimal("110.00"),
        "provider_email": "carlos.encanador@gmail.com",
        "category": "Encanamento",
        "city": ("Cariacica", "ES"),
    },
    {
        "name": "Montagem de moveis",
        "desc": "Montagem de armarios, mesas, camas e paineis.",
        "price": Decimal("100.00"),
        "provider_email": "carlos.encanador@gmail.com",
        "category": "Montagem",
        "city": ("Vitoria", "ES"),
    },
    {
        "name": "Pintura de paredes internas",
        "desc": "Pintura de paredes internas com acabamento simples e limpo.",
        "price": Decimal("180.00"),
        "provider_email": "maria.eletricista@gmail.com",
        "category": "Pintura",
        "city": ("Vila Velha", "ES"),
    },
    {
        "name": "Frete pequeno local",
        "desc": "Transporte de caixas, pequenos moveis e objetos dentro da cidade.",
        "price": Decimal("90.00"),
        "provider_email": "carlos.encanador@gmail.com",
        "category": "Frete",
        "city": ("Serra", "ES"),
    },
]


def get_or_create(model, defaults=None, **filters):
    instance = model.query.filter_by(**filters).first()

    if instance:
        return instance, False

    params = dict(filters)
    params.update(defaults or {})
    instance = model(**params)
    db.session.add(instance)
    return instance, True


def seed_roles():
    roles = {}

    for role_name in ROLES:
        role, _ = get_or_create(Role, name=role_name)
        role.status = True
        roles[role_name] = role

    return roles


def seed_categories():
    categories = {}

    for name, desc in CATEGORIES:
        category, _ = get_or_create(Category, name=name)
        category.desc = desc
        category.status = True
        categories[name] = category

    return categories


def seed_cities():
    cities = {}

    for name, state, country, region in CITIES:
        city, _ = get_or_create(
            City,
            name=name,
            state=state,
            defaults={"country": country, "region": region},
        )
        city.country = country
        city.region = region
        cities[(name, state)] = city

    return cities


def seed_users(roles):
    users = {}

    for user_data in USERS:
        user, created = get_or_create(
            User,
            email=user_data["email"],
            defaults={
                "name": user_data["name"],
                "cpf": user_data["cpf"],
                "phone": user_data["phone"],
            },
        )
        user.name = user_data["name"]
        user.cpf = user_data["cpf"]
        user.phone = user_data["phone"]
        user.is_active = True

        if created or not user.password:
            user.set_password(DEFAULT_PASSWORD)

        users[user.email] = user

    db.session.flush()

    for user_data in USERS:
        user = users[user_data["email"]]

        for role_name in user_data["roles"]:
            role = roles[role_name]
            role_user, _ = get_or_create(
                RoleUser,
                role_id=role.id,
                user_id=user.id,
            )

            if role_name == "provider":
                role_user.provider_status = ProviderStatus.APROVADO

    return users


def seed_services(users, categories, cities):
    for service_data in SERVICES:
        provider = users[service_data["provider_email"]]
        category = categories[service_data["category"]]
        city = cities[service_data["city"]]

        service, _ = get_or_create(
            Service,
            name=service_data["name"],
            provider_id=provider.id,
            defaults={
                "category_id": category.id,
                "city_id": city.id,
                "desc": service_data["desc"],
                "price": service_data["price"],
                "is_active": True,
            },
        )
        service.category_id = category.id
        service.city_id = city.id
        service.desc = service_data["desc"]
        service.price = service_data["price"]
        service.is_active = True


def run():
    app = create_app()

    with app.app_context():
        roles = seed_roles()
        categories = seed_categories()
        cities = seed_cities()
        users = seed_users(roles)
        seed_services(users, categories, cities)

        db.session.commit()

        print("Dados basicos de teste cadastrados com sucesso.")
        print(f"Usuarios de teste usam a senha: {DEFAULT_PASSWORD}")


if __name__ == "__main__":
    run()
