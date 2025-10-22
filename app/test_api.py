import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_user_flow():
    """Тестирование пользовательских методов"""
    # Создание пользователя
    response = client.post(
        "/users", json={"username": "testuser", "email": "testuser@example.com"}
    )
    assert response.status_code == 200
    user_data = response.json()
    user_id = user_data["id"]
    assert "id" in user_data
    assert user_data["message"] == "Пользователь создан"

    # Создание вишлиста
    response = client.post(
        "/wishlists",
        params={"user_id": user_id},
        json={
            "name": "Тестовый вишлист",
            "description": "Описание тестового вишлиста",
            "is_public": True,
        },
    )
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}. Response: {response.text}"
    wishlist_data = response.json()
    wishlist_id = wishlist_data["id"]
    assert "id" in wishlist_data

    # Получение вишлистов пользователя
    response = client.get(f"/users/{user_id}/wishlists")
    assert response.status_code == 200
    wishlists = response.json()
    assert len(wishlists) > 0

    # Получение конкретного вишлиста пользователя
    response = client.get(f"/users/{user_id}/wishlists/{wishlist_id}")
    assert response.status_code == 200
    wishlist = response.json()
    assert wishlist["id"] == wishlist_id
    assert wishlist["owner_id"] == user_id

    # Добавление элемента в вишлист
    response = client.post(
        f"/wishlists/{wishlist_id}/items",
        json={
            "name": "Тестовый предмет",
            "description": "Описание тестового предмета",
            "price": 100.0,
            "category": "Тест",
        },
    )
    assert response.status_code == 200
    item_data = response.json()
    item_id = item_data["id"]
    assert item_data["name"] == "Тестовый предмет"
    assert item_data["price"] == 100.0

    # Получение всех элементов вишлиста
    response = client.get(f"/wishlists/{wishlist_id}/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["id"] == item_id

    # Получение конкретного элемента
    response = client.get(f"/wishlist/{item_id}")
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == item_id

    # Обновление элемента
    response = client.put(
        f"/wishlists/{wishlist_id}/items/{item_id}",
        json={
            "name": "Обновленный предмет",
            "price": 150.0,
        },
    )
    assert response.status_code == 200
    updated_item = response.json()
    assert updated_item["name"] == "Обновленный предмет"
    assert updated_item["price"] == 150.0

    # Резервирование элемента
    response = client.put(
        f"/wishlists/{wishlist_id}/items/{item_id}/reserve",
        json={"reserved_by": "Друг пользователя", "message": "Подарю на день рождения"},
    )
    assert response.status_code == 200
    reserved_item = response.json()
    assert reserved_item["is_reserved"]
    assert reserved_item["reserved_by"] == "Друг пользователя"

    # Отмена резервирования
    response = client.put(f"/wishlists/{wishlist_id}/items/{item_id}/unreserve")
    assert response.status_code == 200
    unreserved_item = response.json()
    assert not unreserved_item["is_reserved"]
    assert unreserved_item["reserved_by"] is None

    # Удаление элемента
    response = client.delete(f"/wishlists/{wishlist_id}/items/{item_id}")
    assert response.status_code == 200
    delete_message = response.json()
    assert "удален" in delete_message["message"]

    # Удаление вишлиста
    response = client.delete(f"/wishlists/{wishlist_id}")
    assert response.status_code == 200
    delete_message = response.json()
    assert "удален" in delete_message["message"]

    # Удаление пользователя
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    delete_message = response.json()
    assert "удален" in delete_message["message"]


def test_error_cases():
    """Тестирование обработки ошибок"""
    user_response = client.post(
        "/users",
        json={"username": "error_test_user", "email": "error_test@example.com"},
    )
    user_id = user_response.json()["id"]

    wishlist_response = client.post(
        "/wishlists", params={"user_id": user_id}, json={"name": "Тест ошибок"}
    )
    wishlist_id = wishlist_response.json()["id"]

    # Пользователь не найден
    response = client.get("/users/999/wishlists")
    assert response.status_code == 404
    error_data = response.json()
    assert error_data["detail"] == "Пользователь не найден"  # ← из ApiError

    # Вишлист не найден
    response = client.get("/wishlists/999/items")
    assert response.status_code == 404
    error_data = response.json()
    assert error_data["detail"] == "Вишлист не найден"

    response = client.post("/wishlists/999/items", json={"name": "Тестовый предмет"})
    assert response.status_code == 404

    response = client.put(
        "/wishlists/1/items/999/reserve", json={"reserved_by": "Тест"}
    )
    assert response.status_code == 404

    client.delete(f"/wishlists/{wishlist_id}")
    client.delete(f"/users/{user_id}")


def test_item_validation():
    """Тестирование ошибки валидации"""
    user_resp = client.post("/users", json={"username": "test", "email": "t@e.com"})
    user_id = user_resp.json()["id"]

    wl_resp = client.post(
        "/wishlists", params={"user_id": user_id}, json={"name": "Test"}
    )
    wl_id = wl_resp.json()["id"]

    r = client.post(f"/wishlists/{wl_id}/items", json={"name": ""})
    assert r.status_code == 422
    error_data = r.json()
    assert error_data["detail"] == "Ошибка валидации входных данных"


def test_duplicate_user():
    """Тестирование создания дубликата пользователя"""
    response = client.post(
        "/users", json={"username": "uniqueuser", "email": "unique@example.com"}
    )
    assert response.status_code == 200
    user_id = response.json()["id"]

    response = client.post(
        "/users", json={"username": "uniqueuser", "email": "different@example.com"}
    )
    assert response.status_code == 400
    error_data = response.json()
    assert error_data["detail"] == "Имя пользователя уже занято"

    # Дубль email
    response = client.post(
        "/users", json={"username": "differentuser", "email": "unique@example.com"}
    )
    assert response.status_code == 400
    error_data = response.json()
    assert error_data["detail"] == "Email уже зарегистрирован"

    client.delete(f"/users/{user_id}")


def test_reservation_errors():
    """Тестирование ошибок резервирования"""
    user_response = client.post(
        "/users", json={"username": "reserve_test", "email": "reserve@test.com"}
    )
    user_id = user_response.json()["id"]

    wishlist_response = client.post(
        "/wishlists", params={"user_id": user_id}, json={"name": "Резервирование тест"}
    )
    assert wishlist_response.status_code == 200
    wishlist_id = wishlist_response.json()["id"]

    item_response = client.post(
        f"/wishlists/{wishlist_id}/items", json={"name": "Предмет для резервирования"}
    )
    assert item_response.status_code == 200
    item_id = item_response.json()["id"]

    # 1. УСПЕШНАЯ резервация
    response = client.put(
        f"/wishlists/{wishlist_id}/items/{item_id}/reserve",
        json={"reserved_by": "Тестер"},
    )
    assert response.status_code == 200

    # 2. ПОВТОРНАЯ резервация → ошибка
    response = client.put(
        f"/wishlists/{wishlist_id}/items/{item_id}/reserve",
        json={"reserved_by": "Другой тестер"},
    )
    assert response.status_code == 400
    error_data = response.json()
    assert error_data["detail"] == "Элемент уже зарезервирован"

    # 3. Отмена резервации
    response = client.put(f"/wishlists/{wishlist_id}/items/{item_id}/unreserve")
    assert response.status_code == 200

    # 4. Повторная отмена → ошибка
    response = client.put(f"/wishlists/{wishlist_id}/items/{item_id}/unreserve")
    assert response.status_code == 400
    error_data = response.json()
    assert error_data["detail"] == "Элемент не был зарезервирован"

    # Очистка
    client.delete(f"/wishlists/{wishlist_id}/items/{item_id}")
    client.delete(f"/wishlists/{wishlist_id}")
    client.delete(f"/users/{user_id}")


def test_get_nonexistent_item():
    """Тестирование получения несуществующего элемента"""
    response = client.get("/wishlist/999")
    assert response.status_code == 404
    error_data = response.json()
    assert error_data["detail"] == "Элемент не найден"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
