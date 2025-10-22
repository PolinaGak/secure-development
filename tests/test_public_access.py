"""from tests.conftest import get_auth_headers

def test_view_public_wishlist_without_auth(client):
    client.post("/auth/register", json={
        "username": "publicuser",
        "email": "public@example.com",
        "password": "password123"
    })
    headers = get_auth_headers(client, "public@example.com", "password123")

    wl_response = client.post("/wishlists", json={"name": "Public List", "is_public": True}, headers=headers)
    wishlist_id = wl_response.json()["id"]

    response = client.get(f"/wishlists/{wishlist_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Public List"


def test_cannot_view_private_wishlist_without_auth(client):
    client.post("/auth/register", json={
        "username": "privateuser",
        "email": "private@example.com",
        "password": "password123"
    })
    headers = get_auth_headers(client, "private@example.com", "password123")

    wl_response = client.post("/wishlists", json={"name": "Private List", "is_public": False}, headers=headers)
    wishlist_id = wl_response.json()["id"]

    response = client.get(f"/wishlists/{wishlist_id}")
    assert response.status_code == 403
    """
