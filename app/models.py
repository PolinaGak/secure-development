from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    wishlists = relationship("Wishlist", back_populates="owner")


class Wishlist(Base):
    __tablename__ = "wishlists"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="wishlists")
    items = relationship("WishItem", back_populates="wishlist", cascade="all, delete")


class WishItem(Base):
    __tablename__ = "wish_items"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float)
    url = Column(String)
    category = Column(String)
    is_reserved = Column(Boolean, default=False)
    reserved_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reserved_by_user = relationship("User", foreign_keys=[reserved_by_user_id])
    reservation_message = Column(Text, nullable=True)
    reserved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    wishlist_id = Column(Integer, ForeignKey("wishlists.id"), nullable=False)
    wishlist = relationship("Wishlist", back_populates="items")
