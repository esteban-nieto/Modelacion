from fastapi import HTTPException
from sqlalchemy import select

from app.models import Profesional, Servicio
from app.seguridad import hashear_clave


def preparar_usuario(db, datos, existente):
    clave = datos.pop("clave")
    if clave:
        datos["clave_hash"] = hashear_clave(clave)
    elif existente is None:
        raise HTTPException(422, "La clave es obligatoria")
    return datos


def preparar_profesional(db, datos, existente):
    ids = set(datos.pop("servicios_ids"))
    servicios = db.scalars(select(Servicio).where(Servicio.id.in_(ids), Servicio.eliminado.is_(False))).all()
    if len(servicios) != len(ids):
        raise HTTPException(422, "Alguno de los servicios indicados no existe")
    datos["servicios"] = servicios
    return datos


def preparar_cita(db, datos, existente):
    profesional = db.get(Profesional, datos["profesional_id"])
    if profesional is None or profesional.eliminado:
        raise HTTPException(422, "El profesional indicado no existe")
    if profesional.sede_id != datos["sede_id"]:
        raise HTTPException(422, "El profesional no pertenece a la sede indicada")
    if datos["servicio_id"] not in {s.id for s in profesional.servicios}:
        raise HTTPException(422, "El profesional no presta el servicio indicado")
    return datos
