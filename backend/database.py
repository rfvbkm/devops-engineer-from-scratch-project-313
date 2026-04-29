from collections.abc import Generator

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from .config import get_database_url
from .models import Link  # noqa: F401 — регистрация таблицы links

_engine = None


def get_engine():
    global _engine
    if _engine is not None:
        return _engine
    url = get_database_url()
    kwargs: dict = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in url:
            kwargs["poolclass"] = StaticPool
    _engine = create_engine(url, **kwargs)
    return _engine


def reset_engine() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
    _engine = None


def init_db() -> None:
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Generator[Session, None, None]:
    session = Session(get_engine())
    try:
        yield session
    finally:
        session.close()
