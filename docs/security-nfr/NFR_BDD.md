# NFR_BDD.md — Приёмка в формате Gherkin

### Feature: Унифицированные ответы при аутентификации (NFR-02)
  **Scenario:** Неверный логин/пароль возвращает единый ответ
    Given сервис запущен на тестовом окружении
    When клиент пытается войти с неверным username или неверным password
    Then API возвращает HTTP 401 и тело { "error": "invalid_credentials" }
    And в логах фиксируется событие auth_failure без поля с причинами
    And p95 разницы времени ответа между "неверным паролем" и "пользователь не найден" ≤ 50 ms

### Feature: Защита от брутфорса (NFR-03)
  **Scenario:** Блокировка аккаунта после 5 неуспешных попыток
    Given сервис запущен и существует аккаунт test-user
    When выполняется 5 последовательных неуспешных попыток входа за 15 минут
    Then при 6-й попытке API возвращает HTTP 429 или HTTP 401 и тело { "error": "account_temporarily_locked" }
    And аккаунт блокируется на ~15 минут


### Feature: TTL токенов — отклонение просроченных (NFR-04)
  **Scenario:** Просроченный access token отклоняется
    Given пользователь получил access token с TTL = 15 минут
    When проходит 16 минут и клиент делает запрос к защищённому endpoint
    Then API возвращает HTTP 401 и тело { "error": "token_expired" }

### Feature: Авторизация (проверка прав владельца) (NFR-05)
  **Scenario:** Только владелец может удалить вишлист
    Given wishlist id=20 принадлежит owner (id=1)
    When пользователь attacker (id=2) вызывает DELETE /wishlists/20
    Then API возвращает HTTP 403 и тело { "error": "access_denied" }
    And владелец может успешно удалить wishlist (HTTP 200 при запросе от owner)

### Feature: Атомарность резервирования (NFR-06)
  **Scenario:** При 100 конкурентных запросах только 1 успешный reserve
    Given в базе есть wishlist id=10 с item id=100 (is_reserved=false)
    When 100 клиентов параллельно отправляют PUT /wishlists/10/items/100/reserve
    Then ровно 1 запрос возвращает HTTP 200 и item.is_reserved == true
    And остальные запросы возвращают HTTP 400/409 с { "error": "already_reserved" }
