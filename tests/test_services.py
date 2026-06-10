from handlink.models import Appointment, Category, Service


def test_category_page_lists_active_services(client, app):
    with app.app_context():
        category = Category.query.filter_by(name="Eletricidade").one()

    response = client.get(f"/servicos/categoria/{category.id}")

    assert response.status_code == 200
    assert b"Instalacao de tomada" in response.data
    assert b"Maria Eletricista" in response.data
    assert b"Servico inativo" not in response.data


def test_service_detail_page_shows_service_and_provider(client, app):
    with app.app_context():
        service = Service.query.filter_by(name="Instalacao de tomada").one()

    response = client.get(f"/servicos/detalhes/{service.id}")

    assert response.status_code == 200
    assert b"Instalacao de tomada" in response.data
    assert b"Maria Eletricista" in response.data
    assert b"120" in response.data


def test_schedule_page_requires_login(client, app):
    with app.app_context():
        service = Service.query.filter_by(name="Instalacao de tomada").one()

    response = client.get(f"/servicos/agendar/{service.id}")

    assert response.status_code in (302, 303)
    assert "/login" in response.headers["Location"]


def test_authenticated_user_can_create_pending_appointment(
    auth_client,
    app,
    future_appointment_time,
):
    with app.app_context():
        service = Service.query.filter_by(name="Instalacao de tomada").one()

    response = auth_client.post(
        f"/servicos/agendar/{service.id}",
        data={
            "appointment_time": future_appointment_time,
            "hours": 2,
            "observacoes": "Trocar tomada da sala.",
        },
    )

    assert response.status_code in (302, 303)

    with app.app_context():
        appointment = Appointment.query.one()
        assert appointment.client.email == "cliente@example.com"
        assert appointment.service_id == service.id
        assert appointment.status == "Pendente"
