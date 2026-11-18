from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app import config


class Base(DeclarativeBase):
    pass


def crear_motor(url):
    if url.startswith("sqlite"):
        opciones = {"connect_args": {"check_same_thread": False}}
        if ":memory:" in url:
            opciones["poolclass"] = StaticPool
        return create_engine(url, **opciones)
    return create_engine(url, pool_pre_ping=True)


motor = crear_motor(config.DATABASE_URL)
Sesion = sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)


def obtener_db():
    db = Sesion()
    try:
        yield db
    finally:
        db.close()
