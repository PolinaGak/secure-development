from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_user_flow():
    # Создание пользователя
    r = client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "secret123",
        },
    )
    assert r.status_code == 200
    user_id = r.json()["id"]

    # Создание вишлиста
    r = client.post(
        "/wishlists",
        params={"user_id": user_id},
        json={"name": "Виш", "description": "Тест", "is_public": True},
    )
    assert r.status_code == 200
    wl_id = r.json()["id"]

    # Добавление предмета
    r = client.post(
        f"/wishlists/{wl_id}/items",
        json={"name": "Книга", "price": 1000.0, "category": "Книги"},
    )
    assert r.status_code == 200
    item_id = r.json()["id"]

    # Резервирование
    r = client.put(
        f"/wishlists/{wl_id}/items/{item_id}/reserve",
        json={"reserved_by": "Друг", "message": "Подарю"},
    )
    assert r.status_code == 200

    # Получение
    r = client.get(f"/wishlist/{item_id}")
    assert r.status_code == 200
    assert r.json()["id"] == item_id

    # Удаление
    client.delete(f"/wishlists/{wl_id}/items/{item_id}")
    client.delete(f"/wishlists/{wl_id}")
    client.delete(f"/users/{user_id}")


def test_error_cases():
    # 404: пользователь
    r = client.get("/users/999/wishlists")
    assert r.status_code == 404
    assert r.json()["title"] == "User Not Found"

    # 404: вишлист
    r = client.get("/wishlists/999/items")
    assert r.status_code == 404
    assert r.json()["title"] == "Wishlist Not Found"


def test_item_validation():
    """422 при пустом имени"""
    r = client.post(
        "/users",
        json={
            "username": "user1",
            "email": "user@example.com",
            "password": "secret123",
        },
    )
    assert r.status_code == 200
    user_id = r.json()["id"]

    r = client.post("/wishlists", params={"user_id": user_id}, json={"name": "WL"})
    assert r.status_code == 200
    wl_id = r.json()["id"]

    r = client.post(f"/wishlists/{wl_id}/items", json={"name": ""})
    assert r.status_code == 422
    assert r.json()["title"] == "Validation Error"

    client.delete(f"/users/{user_id}")


def test_duplicate_user():
    """400 при дубликате"""
    client.post(
        "/users", json={"username": "dup", "email": "a@b.c", "password": "secret123"}
    )

    r = client.post(
        "/users", json={"username": "dup", "email": "x@y.z", "password": "secret123"}
    )
    assert r.status_code == 400
    assert r.json()["title"] == "Username Exists"


def test_reservation_errors():
    """400 при двойном резерве"""
    r = client.post(
        "/users",
        json={
            "username": "reserve1",
            "email": "reserve@example.com",
            "password": "secret123",
        },
    )
    assert r.status_code == 200
    user_id = r.json()["id"]

    r = client.post("/wishlists", params={"user_id": user_id}, json={"name": "R"})
    assert r.status_code == 200
    wl_id = r.json()["id"]

    r = client.post(f"/wishlists/{wl_id}/items", json={"name": "Item"})
    assert r.status_code == 200
    item_id = r.json()["id"]

    client.put(f"/wishlists/{wl_id}/items/{item_id}/reserve", json={"reserved_by": "A"})

    r = client.put(
        f"/wishlists/{wl_id}/items/{item_id}/reserve", json={"reserved_by": "B"}
    )
    assert r.status_code == 400
    assert r.json()["title"] == "Already Reserved"

    client.delete(f"/users/{user_id}")


def test_get_nonexistent_item():
    r = client.get("/wishlist/999")
    assert r.status_code == 404
    assert r.json()["title"] == "Item Not Found"
