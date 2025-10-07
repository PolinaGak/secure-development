from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

argon2_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=256000,
    parallelism=1,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    return argon2_hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return argon2_hasher.verify(hashed, password)
    except VerifyMismatchError:
        return False
