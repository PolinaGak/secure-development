"""
from tests.conftest import get_auth_headers

def test_add_item_to_wishlist(client):
    client.post("/auth/register", json={
        "username": "itemuser",
        "email": "item@example.com",
        "password": "password123"
    })
    headers = get_auth_headers(client, "item@example.com", "password123")

    wl_response = client.post("/wishlists", json={"name": "Gifts"}, headers=headers)
    wishlist_id = wl_response.json()["id"]

    response = client.post(f"/wishlists/{wishlist_id}/items", json={
        "name": "Book",
        "price": 15.99
    }, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Book"
    assert data["price"] == 15.99


def test_reserve_item(client):
    client.post("/auth/register", json={
        "username": "owner",
        "email": "owner@example.com",
        "password": "password123"
    })
    client.post("/auth/register", json={
        "username": "reserver",
        "email": "reserver@example.com",
        "password": "password123"
    })

    owner_headers = get_auth_headers(client, "owner@example.com", "password123")
    reserver_headers = get_auth_headers(client, "reserver@example.com", "password123")

    wl_response = client.post("/wishlists", json={"name": "Public Gifts", "is_public": True}, headers=owner_headers)
    wishlist_id = wl_response.json()["id"]

    item_response = client.post(f"/wishlists/{wishlist_id}/items", json={"name": "Laptop"}, headers=owner_headers)
    item_id = item_response.json()["id"]

    response = client.put(f"/wishlists/{wishlist_id}/items/{item_id}/reserve",
                          json={"message": "I'll buy it!"},
                          headers=reserver_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["is_reserved"] is True
    assert data["reservation_message"] == "I'll buy it!"
"""
