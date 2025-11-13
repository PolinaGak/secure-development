from decimal import Decimal

import pytest

from app.models import WishItemCreate


def test_price_decimal_precision():
    item = WishItemCreate(name="Test", price=Decimal("10.00"))
    assert item.price == Decimal("10.00")


def test_xss_blocked():
    with pytest.raises(ValueError, match="Скрипты запрещены"):
        WishItemCreate(name="<script>alert(1)</script>")


def test_negative_price():
    with pytest.raises(ValueError, match="отрицательной"):
        WishItemCreate(name="Bad", price=Decimal("-5.00"))


def test_allowed_characters():
    WishItemCreate(name="Gift <3")  # сердечко
    WishItemCreate(name="Price: < 100")
    WishItemCreate(name="Hello world!")
