from handlink.models import Appointment, Service


def test_category_page(client):
    response = client.get("/servicos/eletricista")

    assert response.status_code == 200
    assert b"Eletricista" in response.data
    assert b"Instalacao de tomada" in response.data


def test_service_detail_page(client, app):
    with app.app_context():
        service = Service.query.filter_by(name="Instalacao de tomada").first()

    response = client.get(f"/servicos/detalhe/{service.id}")

    assert response.status_code == 200
    assert b"Maria Eletricista" in response.data
    assert b"Solicitar servico" in response.data


def test_create_appointment(auth_client, app):
    with app.app_context():
        service = Service.query.filter_by(name="Instalacao de tomada").first()

    response = auth_client.post(
        f"/servicos/detalhe/{service.id}",
        data={"appointment_time": "2026-06-10T14:30"},
        follow_redirects=False,
    )

    assert response.status_code == 302

    with app.app_context():
        appointment = Appointment.query.one()
        assert appointment.client.email == "cliente@example.com"
        assert appointment.service_id == service.id
        assert appointment.status == "Pendente"
