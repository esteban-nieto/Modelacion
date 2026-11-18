import csv
import io
from collections import defaultdict
from datetime import datetime

from sqlalchemy import select

from app.models import Cita, Profesional, Servicio

MINUTOS_JORNADA = 540


def minutos(inicio, fin):
    return (fin - inicio).total_seconds() / 60


def citas_atendidas(db, desde=None, hasta=None):
    consulta = (
        select(Cita, Servicio.nombre, Profesional.nombre)
        .join(Servicio, Servicio.id == Cita.servicio_id)
        .join(Profesional, Profesional.id == Cita.profesional_id)
        .where(Cita.eliminado.is_(False), Cita.estado == "atendida")
        .order_by(Cita.llegada)
    )
    if desde:
        consulta = consulta.where(Cita.llegada >= desde)
    if hasta:
        consulta = consulta.where(Cita.llegada <= hasta)
    return [
        {
            "cita_id": cita.id,
            "sede_id": cita.sede_id,
            "servicio": servicio,
            "profesional": profesional,
            "prioridad": cita.prioridad,
            "llegada": cita.llegada,
            "inicio_atencion": cita.inicio_atencion,
            "fin_atencion": cita.fin_atencion,
            "espera_min": round(minutos(cita.llegada, cita.inicio_atencion), 2),
            "atencion_min": round(minutos(cita.inicio_atencion, cita.fin_atencion), 2),
        }
        for cita, servicio, profesional in db.execute(consulta)
    ]


def promedio(valores):
    return round(sum(valores) / len(valores), 2) if valores else 0.0


def tiempos_por_servicio(filas):
    grupos = defaultdict(list)
    for fila in filas:
        grupos[fila["servicio"]].append(fila)
    return [
        {
            "servicio": servicio,
            "citas": len(grupo),
            "espera_media_min": promedio([f["espera_min"] for f in grupo]),
            "atencion_media_min": promedio([f["atencion_min"] for f in grupo]),
        }
        for servicio, grupo in sorted(grupos.items())
    ]


def ocupacion_por_profesional(filas):
    dias = {f["llegada"].date() for f in filas}
    grupos = defaultdict(float)
    for fila in filas:
        grupos[fila["profesional"]] += fila["atencion_min"]
    disponible = max(len(dias), 1) * MINUTOS_JORNADA
    return [
        {
            "profesional": profesional,
            "minutos_atendidos": round(total, 1),
            "minutos_disponibles": disponible,
            "ocupacion_pct": round(100 * total / disponible, 1),
        }
        for profesional, total in sorted(grupos.items())
    ]


def volumen_por_periodo(filas, periodo="dia"):
    formato = "%Y-%m" if periodo == "mes" else "%Y-%m-%d"
    conteo = defaultdict(int)
    for fila in filas:
        conteo[fila["llegada"].strftime(formato)] += 1
    return [{"periodo": clave, "citas": total} for clave, total in sorted(conteo.items())]


def a_csv(filas):
    if not filas:
        return ""
    salida = io.StringIO()
    escritor = csv.DictWriter(salida, fieldnames=list(filas[0].keys()), lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(filas)
    return salida.getvalue()


def interpretar_fecha(texto):
    return datetime.fromisoformat(texto) if texto else None
