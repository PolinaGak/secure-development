"""from tests.conftest import get_auth_headers


def test_delete_own_user(client):
    client.post("/auth/register", json={
        "username": "todelete",
        "email": "delete@example.com",
        "password": "password123"
    })
    headers = get_auth_headers(client, "delete@example.com", "password123")

    response = client.delete("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted
"""
