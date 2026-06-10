def test_home_page_returns_200_and_brand(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"HandLink" in response.data or b"HandyLink" in response.data
