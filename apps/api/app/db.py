from __future__ import annotations

from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from .settings import settings


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def _ensure_sqlite_dir(database_url: str) -> None:
    if not database_url.startswith("sqlite:///./"):
        return
    rel = database_url.removeprefix("sqlite:///./")
    p = Path(rel).parent
    p.mkdir(parents=True, exist_ok=True)


database_url = _normalize_database_url(settings.database_url)
_ensure_sqlite_dir(database_url)

engine_kwargs = {}
if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 1
    engine_kwargs["max_overflow"] = 0

engine = create_engine(
    database_url,
    **engine_kwargs,
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

