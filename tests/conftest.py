import os

os.environ["SECRET_KEY"] = "clave-de-pruebas-0123456789abcdef"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app import config
from app.database import Base, Sesion, motor
from app.main import app
from app.models import Paciente, Profesional, Rol, Sede, Servicio, Usuario
from app.seguridad import hashear_clave

CLAVE = "Prueba12345"


@pytest.fixture(autouse=True)
def base_de_datos():
    Base.metadata.drop_all(motor)
    Base.metadata.create_all(motor)
    with Sesion() as db:
        roles = {n: Rol(nombre=n) for n in ("administrador", "operador", "consulta")}
        db.add_all(roles.values())
        db.flush()
        for nombre, rol in roles.items():
            db.add(Usuario(nombre=nombre, correo=f"{nombre}@prueba.co", clave_hash=hashear_clave(CLAVE), rol_id=rol.id))
        sede = Sede(nombre="Sede Central", vereda="Fagua")
        servicio = Servicio(nombre="Medicina general", duracion_media_min=20)
        otro = Servicio(nombre="Odontología", duracion_media_min=30)
        db.add_all([sede, servicio, otro])
        db.flush()
        db.add(Profesional(nombre="Dra. Ana Ruiz", sede_id=sede.id, servicios=[servicio]))
        db.add(Paciente(documento="123456", nombre="Paciente Uno", telefono="3001234567", fecha_nacimiento=datetime(1990, 1, 1)))
        db.commit()
    yield


@pytest.fixture
def cliente():
    return TestClient(app)


@pytest.fixture
def entrar(cliente):
    def _entrar(rol):
        respuesta = cliente.post("/api/auth/login", json={"correo": f"{rol}@prueba.co", "clave": CLAVE})
        return {"Authorization": f"Bearer {respuesta.json()['token']}"}

    return _entrar


@pytest.fixture
def cita_valida():
    return {
        "paciente_id": 1,
        "profesional_id": 1,
        "servicio_id": 1,
        "sede_id": 1,
        "llegada": "2024-03-04T08:00:00",
        "inicio_atencion": "2024-03-04T08:10:00",
        "fin_atencion": "2024-03-04T08:30:00",
        "estado": "atendida",
    }


@pytest.fixture
def umbral():
    anterior = config.UMBRAL_ESPERA_MIN
    yield anterior
    config.UMBRAL_ESPERA_MIN = anterior
