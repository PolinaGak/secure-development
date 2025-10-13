| Поток/Элемент           | Угроза (STRIDE)          | Риск | Контроль                                           | Ссылка на NFR   | Проверка/Артефакт                                |
|------------------------|--------------------------|------|---------------------------------------------------|-----------------|-------------------------------------------------|
| F1 /auth/register       | S: Spoofing              | R1   | MFA, email verification                            | NFR-03, NFR-01  | e2e тесты, unit-тесты аутентификации             |
| F1 /auth/register       | T: Tampering             | R2   | Хэширование паролей Argon2id                       | NFR-01          | Unit-тесты, ревью кода                           |
| F2 /auth/login          | S: Spoofing              | R3   | MFA, ограничение попыток входа (rate-limit)       | NFR-03, NFR-04  | Интеграционные тесты, мониторинг метрик          |
| F2 /auth/login          | D: Denial of Service     | R4   | Ограничение попыток входа, блокировка IP          | NFR-03          | Метрики, нагрузочные тесты                        |
| F3 /auth/token_refresh  | T: Tampering             | R5   | Короткоживущие токены, проверка ротации секретов | NFR-04          | Ревью конфигурации, e2e тесты                     |
| F3 /auth/token_refresh  | R: Repudiation           | R6   | Логирование операций с токенами                    | NFR-08          | Лог-анализ                                       |
| F4 /wishlists/create    | A: Atomicity violation   | R7   | Атомарность операций резервирования                | NFR-06          | Конкурентные нагрузочные тесты (k6/locust)       |
| F5 /wishlists/read      | I: Information Disclosure| R8   | RBAC и авторизация                                 | NFR-05          | Контрактные тесты, pen-test                        |
| F6 /wishlists/update    | E: Elevation of Privilege| R9   | Проверка owner_id/role при изменениях              | NFR-05          | Unit-тесты, ревью кода                           |
| F7 /wishlists/delete    | E: Elevation of Privilege| R10  | RBAC + проверка владельца                           | NFR-05          | Контрактные тесты, ревью                         |
| F8 /wishlists/reserve   | D: Denial of Service     | R11  | Ограничение частоты вызовов                        | NFR-03          | Метрики, нагрузочные тесты                        |
| F8 /wishlists/reserve   | A: Atomicity violation   | R12  | Конкурентный контроль резервирования               | NFR-06          | Тесты с высокой конкуренцией                      |
| Token Validation        | S: Spoofing              | R13  | Валидация JWT, ротация секретов                    | NFR-04          | Проверка конфигурации, ревью infra                |
| Logging                 | I: Information Disclosure| R14  | Структурированные логи без секретов                | NFR-08          | Secret-scanner, ревью логгера                      |
| Input Validation        | T: Tampering             | R15  | Валидация и экранирование входных данных           | NFR-07          | Unit-тесты, DAST                                |
| API Gateway            | D: Denial of Service      | R16  | Ограничение количества запросов, throttling       | NFR-03          | Метрики, нагрузочные тесты                        |
