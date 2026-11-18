from sqlalchemy import func, select

from app import config
from app.models import Cita, Profesional, profesional_servicio
from app.negocio.reportes import promedio


def cola_de_atencion(db, sede_id):
    consulta = (
        select(Cita)
        .where(Cita.eliminado.is_(False), Cita.estado == "programada", Cita.sede_id == sede_id)
        .order_by(Cita.prioridad.desc(), Cita.llegada)
    )
    return db.scalars(consulta).all()


def profesional_con_menos_carga(db, sede_id, servicio_id):
    carga = func.count(Cita.id)
    consulta = (
        select(Profesional, carga)
        .join(profesional_servicio, profesional_servicio.c.profesional_id == Profesional.id)
        .outerjoin(
            Cita,
            (Cita.profesional_id == Profesional.id) & (Cita.estado == "programada") & (Cita.eliminado.is_(False)),
        )
        .where(
            Profesional.eliminado.is_(False),
            Profesional.sede_id == sede_id,
            profesional_servicio.c.servicio_id == servicio_id,
        )
        .group_by(Profesional.id)
        .order_by(carga, Profesional.id)
    )
    fila = db.execute(consulta).first()
    return fila[0] if fila else None


def alertas_capacidad(filas, umbral=None):
    umbral = config.UMBRAL_ESPERA_MIN if umbral is None else umbral
    por_servicio = {}
    for fila in filas:
        por_servicio.setdefault(fila["servicio"], []).append(fila["espera_min"])
    return [
        {"servicio": servicio, "espera_media_min": promedio(esperas), "umbral_min": umbral}
        for servicio, esperas in sorted(por_servicio.items())
        if promedio(esperas) > umbral
    ]
