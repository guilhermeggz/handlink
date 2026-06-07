def test_profile_requires_login(client):
    response = client.get("/perfil")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_authenticated_profile(auth_client):
    response = auth_client.get("/perfil")

    assert response.status_code == 200
    assert b"Cliente Teste" in response.data
    assert b"cliente@example.com" in response.data
