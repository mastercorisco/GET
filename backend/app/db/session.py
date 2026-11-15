from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base

_ENGINE_CACHE: dict[str, tuple[Engine, sessionmaker[Session]]] = {}


def sqlite_url(db_path: Path) -> str:
    return f"sqlite:///{db_path.resolve()}"


def create_sqlite_engine(db_path: Path) -> Engine:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        sqlite_url(db_path),
        connect_args={"check_same_thread": False, "timeout": 120.0},
        poolclass=StaticPool,
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()

    return engine


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=None)


def bind_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session_factory_for_workspace(db_path: Path) -> tuple[Engine, sessionmaker[Session]]:
    key = str(db_path.resolve())
    cached = _ENGINE_CACHE.get(key)
    if cached is not None:
        return cached
    engine = create_sqlite_engine(db_path)
    factory = bind_session_factory(engine)
    _ENGINE_CACHE[key] = (engine, factory)
    return engine, factory


def session_scope(factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()