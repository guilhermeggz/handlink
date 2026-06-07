def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"HandyLink" in response.data
    assert b"Eletricista" in response.data
