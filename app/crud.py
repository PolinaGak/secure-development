# app/crud.py

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.hashing import hash_password


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )
    return db_user


def delete_user(db: Session, user_id: int) -> dict:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}


def get_user_wishlists(db: Session, user_id: int) -> list[models.Wishlist]:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(models.Wishlist).filter(models.Wishlist.owner_id == user_id).all()


def get_wishlist_by_id(db: Session, wishlist_id: int) -> models.Wishlist | None:
    return db.query(models.Wishlist).filter(models.Wishlist.id == wishlist_id).first()


def get_wishlist_public_or_owner(
    db: Session, wishlist_id: int, current_user_id: Optional[int] = None
) -> models.Wishlist:
    wishlist = get_wishlist_by_id(db, wishlist_id)
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    if wishlist.is_public:
        return wishlist

    if current_user_id is None or wishlist.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return wishlist


def create_wishlist(
    db: Session, wishlist: schemas.WishlistCreate, owner_id: int
) -> models.Wishlist:
    user = get_user_by_id(db, owner_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_wishlist = models.Wishlist(
        name=wishlist.name,
        description=wishlist.description,
        is_public=wishlist.is_public,
        owner_id=owner_id,
    )
    db.add(db_wishlist)
    db.commit()
    db.refresh(db_wishlist)
    return db_wishlist


def get_user_wishlist(db: Session, user_id: int, wishlist_id: int) -> models.Wishlist:
    wishlist = get_wishlist_by_id(db, wishlist_id)
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")
    if wishlist.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not the owner of this wishlist")
    return wishlist


def delete_wishlist(db: Session, wishlist_id: int) -> dict:
    wishlist = get_wishlist_by_id(db, wishlist_id)
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")
    db.delete(wishlist)
    db.commit()
    return {"detail": "Wishlist deleted"}


def get_wish_item_by_id(db: Session, item_id: int) -> models.WishItem | None:
    return db.query(models.WishItem).filter(models.WishItem.id == item_id).first()


def get_items_from_wishlist(db: Session, wishlist_id: int) -> list[models.WishItem]:
    wishlist = get_wishlist_by_id(db, wishlist_id)
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")
    return wishlist.items


def add_item_to_wishlist(
    db: Session, wishlist_id: int, item: schemas.WishItemCreate
) -> models.WishItem:
    wishlist = get_wishlist_by_id(db, wishlist_id)
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    db_item = models.WishItem(
        name=item.name,
        description=item.description,
        price=item.price,
        url=item.url,
        category=item.category,
        wishlist_id=wishlist_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_wishlist_item_by_id(db: Session, item_id: int) -> models.WishItem:
    item = get_wish_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Wish item not found")
    return item


def update_wishlist_item(
    db: Session, wishlist_id: int, item_id: int, item_update: schemas.WishItemCreate
) -> models.WishItem:
    db_item = get_wish_item_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Wish item not found")
    if db_item.wishlist_id != wishlist_id:
        raise HTTPException(status_code=400, detail="Item does not belong to this wishlist")

    for key, value in item_update.dict(exclude_unset=True).items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item


def reserve_item(
    db: Session,
    wishlist_id: int,
    item_id: int,
    current_user_id: int,
    message: Optional[str] = None,
) -> models.WishItem:
    db_item = get_wish_item_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Wish item not found")
    if db_item.wishlist_id != wishlist_id:
        raise HTTPException(status_code=400, detail="Item does not belong to this wishlist")
    if db_item.is_reserved:
        raise HTTPException(status_code=400, detail="Item is already reserved")

    db_item.is_reserved = True
    db_item.reserved_by_user_id = current_user_id
    db_item.reservation_message = message
    db_item.reserved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_item)
    return db_item


def unreserve_item(db: Session, wishlist_id: int, item_id: int) -> models.WishItem:
    db_item = get_wish_item_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Wish item not found")
    if db_item.wishlist_id != wishlist_id:
        raise HTTPException(status_code=400, detail="Item does not belong to this wishlist")
    if not db_item.is_reserved:
        raise HTTPException(status_code=400, detail="Item is not reserved")

    db_item.is_reserved = False
    db_item.reserved_by_user_id = None
    db_item.reservation_message = None
    db_item.reserved_at = None

    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, wishlist_id: int, item_id: int) -> dict:
    db_item = get_wish_item_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Wish item not found")
    if db_item.wishlist_id != wishlist_id:
        raise HTTPException(status_code=400, detail="Item does not belong to this wishlist")

    db.delete(db_item)
    db.commit()
    return {"detail": "Item deleted"}
