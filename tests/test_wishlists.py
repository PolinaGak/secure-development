"""from tests.conftest import get_auth_headers

def test_create_wishlist(client):
    client.post("/auth/register", json={
        "username": "wishlistuser",
        "email": "wl@example.com",
        "password": "password123"
    })
    headers = get_auth_headers(client, "wl@example.com", "password123")

    response = client.post("/wishlists", json={
        "name": "My Wishlist",
        "description": "Test list",
        "is_public": True
    }, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Wishlist"
    assert data["is_public"] is True


def test_get_my_wishlists(client):
    client.post("/auth/register", json={
        "username": "mywluser",
        "email": "mywl@example.com",
        "password": "password123"
    })
    headers = get_auth_headers(client, "mywl@example.com", "password123")

    client.post("/wishlists", json={"name": "List 1"}, headers=headers)
    client.post("/wishlists", json={"name": "List 2", "is_public": False}, headers=headers)

    response = client.get("/wishlists/mine", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "List 1"""
