from tests.conftest import login


def test_login_page_returns_200_and_form(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert b"Login" in response.data or b"Entrar" in response.data
    assert b'name="email"' in response.data
    assert b'name="password"' in response.data


def test_valid_login_authenticates_user(client):
    response = login(client)

    assert response.status_code in (302, 303)

    with client.session_transaction() as session:
        assert "_user_id" in session


def test_invalid_login_does_not_authenticate(client):
    response = login(client, password="senha-errada")

    assert response.status_code == 200
    assert b"E-mail ou senha" in response.data

    with client.session_transaction() as session:
        assert "_user_id" not in session


def test_logout_clears_session(auth_client):
    response = auth_client.get("/logout")

    assert response.status_code in (302, 303)

    with auth_client.session_transaction() as session:
        assert "_user_id" not in session
