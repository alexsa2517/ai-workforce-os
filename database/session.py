"""
Database Session - SQLAlchemy connection and session management
Supports both SQLite (development) and PostgreSQL (production).
"""
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Generator
from app.core.config import settings

logger = logging.getLogger("ai_workforce.database")


def _create_engine():
    """Create SQLAlchemy engine with appropriate settings for the database type."""
    url = settings.DATABASE_URL
    is_sqlite = "sqlite" in url.lower()

    connect_args = {}
    if is_sqlite:
        # SQLite-specific settings: enable WAL mode for better concurrency
        connect_args["check_same_thread"] = False
        engine_kwargs = {}
    else:
        # PostgreSQL/MySQL settings
        engine_kwargs = {
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_pre_ping": True,
        }

    engine = create_engine(
        url,
        echo=settings.APP_DEBUG,
        connect_args=connect_args,
        **engine_kwargs,
    )

    if is_sqlite:
        # Enable WAL mode for better concurrency on SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


# Create engine
engine = _create_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for models - single source of truth
class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")


def get_engine():
    """Get the SQLAlchemy engine instance."""
    return engine
