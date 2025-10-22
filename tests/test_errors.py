from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_not_found_item():
    r = client.get("/items/999")
    assert r.status_code == 404
    body = r.json()
    assert body["detail"] == "Ресурс не найден"


def test_auth_invalid_credentials():
    response = client.post("/auth/login", json={"email": "x@x.com", "password": "123"})
    assert response.status_code == 401
    assert response.json() == {"error": "invalid_credentials"}
    assert "X-Correlation-ID" in response.headers


def test_wishlist_not_found():
    response = client.get("/wishlists/999999/items")
    assert response.status_code == 404
    body = response.json()
    assert "type" in body
    assert "correlation_id" in body
    assert body["status"] == 404
