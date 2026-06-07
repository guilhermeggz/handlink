def test_login_page(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert b"Faca seu login" in response.data


def test_valid_login(client):
    response = client.post("/login", data={
        "email": "cliente@example.com",
        "password": "senha123",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Login realizado com sucesso" in response.data

    with client.session_transaction() as session:
        assert "_user_id" in session


def test_invalid_login(client):
    response = client.post("/login", data={
        "email": "cliente@example.com",
        "password": "errada",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"E-mail ou senha invalidos" in response.data

    with client.session_transaction() as session:
        assert "_user_id" not in session


def test_logout(auth_client):
    response = auth_client.get("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"Voce saiu da sua conta" in response.data

    with auth_client.session_transaction() as session:
        assert "_user_id" not in session
