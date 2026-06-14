"""Database setup — SQLAlchemy engine, session, and Base.

SQLite is used for zero-setup local runs. Swapping to PostgreSQL only
requires changing DATABASE_URL (the diagrams target Postgres in production).
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# File-based SQLite DB stored next to the backend package.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./learnhub.db")

# check_same_thread is required only for SQLite + FastAPI's threadpool.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
