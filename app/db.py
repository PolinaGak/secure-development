# app/db.py

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

_engine = None
_SessionLocal = None
Base = declarative_base()

def get_engine():
    global _engine
    if _engine is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is not set")
        _engine = create_engine(DATABASE_URL, echo=False, future=True)
    return _engine

def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

def get_db() -> Session:
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()
