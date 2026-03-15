"""SQLAlchemy database engine, session factory, and dependency injection."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from typing import Generator

from backend.config import get_settings


settings = get_settings()

# ── Engine ──
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug,
    pool_pre_ping=True,
)

# Enable WAL mode and foreign keys for SQLite
if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# ── Session Factory ──
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Base Class ──
class Base(DeclarativeBase):
    pass


# ── FastAPI Dependency ──
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Call on startup."""
    from backend.models import (  # noqa: F401 — import to register models
        user, aquaculture, crop, poultry, inventory,
        sensor, automation, financial, market, incident, production,
        store, supply_chain, retail, packing, logistics, service_request, activity_log,
    )
    Base.metadata.create_all(bind=engine)
