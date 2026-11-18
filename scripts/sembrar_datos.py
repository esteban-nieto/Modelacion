import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import Base, Sesion, motor
from app.models import Cita, Paciente, Profesional, Rol, Sede, Servicio, Usuario
from app.seguridad import hashear_clave

SEMILLA = 2024
DIAS_HABILES = 60
INICIO_JORNADA = 7
MINUTOS_JORNADA = 540
TOTAL_PACIENTES = 700

SERVICIOS = {
    "Medicina general": {"duracion": 20, "llegadas_por_min": 0.07, "profesionales": ["Dra. Marcela Rojas", "Dr. Andrés Pineda"]},
    "Enfermería y vacunación": {"duracion": 10, "llegadas_por_min": 0.05, "profesionales": ["Enf. Sandra Cuervo"]},
    "Odontología": {"duracion": 30, "llegadas_por_min": 0.02, "profesionales": ["Dr. Julián Mora"]},
}

NOMBRES = ["Ana", "Luis", "María", "Carlos", "Rosa", "Jorge", "Lucía", "Pedro", "Elena", "Juan", "Marta", "Diego"]
APELLIDOS = ["Gómez", "Rodríguez", "Pérez", "Sánchez", "Torres", "Ramírez", "Castro", "Vargas", "Moreno", "Ortiz"]

CLAVES = {
    "administrador": os.environ.get("CLAVE_ADMIN", "Admin12345"),
    "operador": os.environ.get("CLAVE_OPERADOR", "Operador12345"),
    "consulta": os.environ.get("CLAVE_CONSULTA", "Consulta12345"),
}


def tiempo_de_servicio(rng, servicio):
    if servicio == "Medicina general":
        sigma = 0.5
        mu = np.log(20) - sigma**2 / 2
        return rng.lognormal(mu, sigma)
    if servicio == "Enfermería y vacunación":
        return rng.gamma(2.0, 5.0)
    return 30.0 * rng.weibull(2.5) / 0.8873


def llegadas_del_dia(rng, tasa):
    instantes = []
    reloj = rng.exponential(1 / tasa)
    while reloj < MINUTOS_JORNADA:
        instantes.append(reloj)
        reloj += rng.exponential(1 / tasa)
    return instantes


def generar_citas_del_dia(rng, fecha, servicios, profesionales, pacientes):
    apertura = datetime(fecha.year, fecha.month, fecha.day, INICIO_JORNADA)
    citas = []
    for servicio in servicios:
        libres = {p.id: apertura for p in profesionales[servicio.nombre]}
        configuracion = SERVICIOS[servicio.nombre]
        for instante in llegadas_del_dia(rng, configuracion["llegadas_por_min"]):
            profesional = profesionales[servicio.nombre][rng.integers(len(profesionales[servicio.nombre]))]
            llegada = apertura + timedelta(minutes=float(instante))
            sorteo = rng.random()
            cita = Cita(
                paciente_id=int(pacientes[rng.integers(len(pacientes))].id),
                profesional_id=profesional.id,
                servicio_id=servicio.id,
                sede_id=profesional.sede_id,
                llegada=llegada,
                prioridad="prioritaria" if rng.random() < 0.12 else "normal",
            )
            if sorteo < 0.05:
                cita.estado = "no_asistio" if sorteo < 0.03 else "cancelada"
            else:
                inicio = max(llegada, libres[profesional.id])
                fin = inicio + timedelta(minutes=float(tiempo_de_servicio(rng, servicio.nombre)))
                libres[profesional.id] = fin
                cita.estado, cita.inicio_atencion, cita.fin_atencion = "atendida", inicio, fin
            citas.append(cita)
    return citas


def dias_habiles(cantidad):
    dia = datetime(2024, 3, 4)
    while cantidad:
        if dia.weekday() < 5:
            yield dia
            cantidad -= 1
        dia += timedelta(days=1)


def base_con_datos():
    Base.metadata.create_all(motor)
    with Sesion() as db:
        return db.scalar(select(Usuario.id).limit(1)) is not None


def sembrar():
    Base.metadata.drop_all(motor)
    Base.metadata.create_all(motor)
    rng = np.random.default_rng(SEMILLA)
    with Sesion() as db:
        roles = {nombre: Rol(nombre=nombre) for nombre in CLAVES}
        db.add_all(roles.values())
        db.flush()
        for nombre, rol in roles.items():
            db.add(
                Usuario(
                    nombre=nombre.capitalize(),
                    correo=f"{nombre}@saludrural.co",
                    clave_hash=hashear_clave(CLAVES[nombre]),
                    rol_id=rol.id,
                )
            )
        sede = Sede(nombre="Puesto de Salud Fagua", vereda="Fagua")
        db.add(sede)
        servicios = [Servicio(nombre=n, duracion_media_min=c["duracion"]) for n, c in SERVICIOS.items()]
        db.add_all(servicios)
        db.flush()
        profesionales = {}
        for servicio in servicios:
            profesionales[servicio.nombre] = []
            for nombre in SERVICIOS[servicio.nombre]["profesionales"]:
                profesional = Profesional(nombre=nombre, sede_id=sede.id, servicios=[servicio])
                db.add(profesional)
                profesionales[servicio.nombre].append(profesional)
        pacientes = [
            Paciente(
                documento=str(10000000 + i),
                nombre=f"{NOMBRES[i % len(NOMBRES)]} {APELLIDOS[(i // 3) % len(APELLIDOS)]} {i}",
                telefono=f"3{100000000 + i}",
                fecha_nacimiento=datetime(1940, 1, 1) + timedelta(days=int(rng.integers(0, 28000))),
            )
            for i in range(TOTAL_PACIENTES)
        ]
        db.add_all(pacientes)
        db.flush()
        for fecha in dias_habiles(DIAS_HABILES):
            db.add_all(generar_citas_del_dia(rng, fecha, servicios, profesionales, pacientes))
        db.commit()
        total = db.scalar(select(Cita.id).order_by(Cita.id.desc()))
    print(f"Datos sembrados: {TOTAL_PACIENTES} pacientes y {total} citas")


if __name__ == "__main__":
    if "--forzar" not in sys.argv and base_con_datos():
        print("La base ya tiene datos; use --forzar para reiniciarla")
    else:
        sembrar()
