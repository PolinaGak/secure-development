import argon2
from argon2 import Parameters

from app.hashing import hash_password, verify_password


def test_hash_password_uses_argon2id():
    password = "StrongPassword123!"
    hashed = hash_password(password)

    assert hashed.startswith("$argon2id$")

    params: Parameters = argon2.extract_parameters(hashed)
    assert params.type == argon2.Type.ID
    assert params.time_cost == 3
    assert params.memory_cost == 256000
    assert params.parallelism == 1


def test_password_verification():
    password = "some-password"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False
