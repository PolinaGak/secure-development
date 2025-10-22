def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_register_duplicate_email(client):
    client.post("/auth/register", json={
        "username": "user1",
        "email": "duplicate@example.com",
        "password": "password123"
    })
    # Попробуем снова
    response = client.post("/auth/register", json={
        "username": "user2",
        "email": "duplicate@example.com",
        "password": "password123"
    })
    assert response.status_code == 400

def test_login_success(client):
    # Регистрация
    client.post("/auth/register", json={
        "username": "logintest",
        "email": "login@example.com",
        "password": "password123"
    })
    # Логин
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    client.post("/auth/register", json={
        "username": "badlogin",
        "email": "bad@example.com",
        "password": "password123"
    })
    response = client.post("/auth/login", json={
        "email": "bad@example.com",
        "password": "wrong"
    })
    assert response.status_code == 401
