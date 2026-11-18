from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.consultas import listar
from app.database import obtener_db
from app.dependencias import ADMIN, ESCRITURA, TODOS, requiere_roles
from app.models import Auditoria
from app.negocio import reportes, tablero, turnos
from app.schemas import AuditoriaSalida, CitaSalida, Pagina, ProfesionalSalida

router = APIRouter(prefix="/api", tags=["operacion"])

REPORTES = {
    "tiempos": reportes.tiempos_por_servicio,
    "ocupacion": reportes.ocupacion_por_profesional,
    "volumen": reportes.volumen_por_periodo,
}


def respuesta_csv(filas, nombre):
    return Response(
        reportes.a_csv(filas),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{nombre}.csv"'},
    )


@router.get("/reportes/{nombre}")
def reporte(
    nombre: str,
    desde: str | None = None,
    hasta: str | None = None,
    periodo: str = Query("dia", pattern="^(dia|mes)$"),
    formato: str = Query("json", pattern="^(json|csv)$"),
    db=Depends(obtener_db),
    _=Depends(requiere_roles(*TODOS)),
):
    if nombre not in REPORTES:
        raise HTTPException(404, "Reporte no encontrado")
    try:
        filas = reportes.citas_atendidas(db, reportes.interpretar_fecha(desde), reportes.interpretar_fecha(hasta))
    except ValueError:
        raise HTTPException(422, "Las fechas deben tener formato ISO (AAAA-MM-DD)")
    resultado = REPORTES[nombre](filas, periodo) if nombre == "volumen" else REPORTES[nombre](filas)
    return respuesta_csv(resultado, nombre) if formato == "csv" else resultado


@router.get("/exportar/citas.csv")
def exportar_citas(db=Depends(obtener_db), _=Depends(requiere_roles(*ESCRITURA))):
    return respuesta_csv(reportes.citas_atendidas(db), "citas_historicas")


@router.get("/citas/cola", response_model=list[CitaSalida])
def cola(sede_id: int, db=Depends(obtener_db), _=Depends(requiere_roles(*TODOS))):
    return turnos.cola_de_atencion(db, sede_id)


@router.get("/citas/profesional-sugerido", response_model=ProfesionalSalida)
def profesional_sugerido(sede_id: int, servicio_id: int, db=Depends(obtener_db), _=Depends(requiere_roles(*ESCRITURA))):
    profesional = turnos.profesional_con_menos_carga(db, sede_id, servicio_id)
    if profesional is None:
        raise HTTPException(404, "No hay profesionales disponibles para ese servicio en la sede")
    return profesional


@router.get("/alertas/capacidad")
def alertas_capacidad(db=Depends(obtener_db), _=Depends(requiere_roles(*TODOS))):
    return turnos.alertas_capacidad(reportes.citas_atendidas(db))


@router.get("/tablero")
def tablero_indicadores(db=Depends(obtener_db), _=Depends(requiere_roles(*TODOS))):
    filas = reportes.citas_atendidas(db)
    return {
        "reales": tablero.indicadores_reales(filas),
        "proyectados": tablero.proyectados(tablero.resultados_simulacion()),
        "alertas": turnos.alertas_capacidad(filas),
    }


@router.get("/auditoria", response_model=Pagina[AuditoriaSalida])
def consultar_auditoria(
    pagina: int = Query(1, ge=1),
    tamano: int = Query(20, ge=1, le=100),
    entidad: str | None = None,
    db=Depends(obtener_db),
    _=Depends(requiere_roles(*ADMIN)),
):
    filtros = {"entidad": entidad} if entidad else {}
    return listar(db, Auditoria, filtros, None, (), "id", "desc", pagina, tamano)
