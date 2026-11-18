from dataclasses import dataclass
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app import auditoria
from app.consultas import listar
from app.database import obtener_db
from app.dependencias import ADMIN, ESCRITURA, TODOS, requiere_roles
from app.schemas import Pagina


@dataclass
class Recurso:
    nombre: str
    modelo: type
    entrada: type
    salida: type
    campos_busqueda: tuple
    filtros: tuple = ()
    ordenables: tuple = ("id",)
    lectura: tuple = TODOS
    escritura: tuple = ESCRITURA
    borrado: tuple = ADMIN
    preparar: Callable | None = None


def validar_referencias(db, modelo, datos):
    for columna in modelo.__table__.columns:
        valor = datos.get(columna.name)
        if valor is None:
            continue
        for clave_foranea in columna.foreign_keys:
            destino = clave_foranea.column
            if db.execute(select(destino).where(destino == valor)).first() is None:
                raise HTTPException(422, f"No existe el registro referenciado en {columna.name}")


def obtener_o_404(db, modelo, registro_id):
    registro = db.get(modelo, registro_id)
    if registro is None or getattr(registro, "eliminado", False):
        raise HTTPException(404, "Registro no encontrado")
    return registro


def guardar(db, operacion=None):
    try:
        (operacion or db.commit)()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Ya existe un registro con esos datos únicos")


def crear_router(recurso):
    router = APIRouter(prefix=f"/api/{recurso.nombre}", tags=[recurso.nombre])
    salida = recurso.salida

    @router.get("", response_model=Pagina[salida])
    def listar_registros(
        request: Request,
        pagina: int = Query(1, ge=1),
        tamano: int = Query(10, ge=1, le=100),
        busqueda: str | None = Query(None, max_length=100),
        orden: str = "id",
        direccion: str = Query("asc", pattern="^(asc|desc)$"),
        db=Depends(obtener_db),
        _=Depends(requiere_roles(*recurso.lectura)),
    ):
        if orden not in recurso.ordenables:
            raise HTTPException(422, f"Orden permitido: {', '.join(recurso.ordenables)}")
        filtros = {k: v for k, v in request.query_params.items() if k in recurso.filtros}
        return listar(db, recurso.modelo, filtros, busqueda, recurso.campos_busqueda, orden, direccion, pagina, tamano)

    @router.get("/{registro_id}", response_model=salida)
    def consultar(registro_id: int, db=Depends(obtener_db), _=Depends(requiere_roles(*recurso.lectura))):
        return obtener_o_404(db, recurso.modelo, registro_id)

    @router.post("", response_model=salida, status_code=201)
    def crear(datos: recurso.entrada, db=Depends(obtener_db), usuario=Depends(requiere_roles(*recurso.escritura))):
        valores = datos.model_dump()
        if recurso.preparar:
            valores = recurso.preparar(db, valores, None)
        validar_referencias(db, recurso.modelo, valores)
        registro = recurso.modelo(**valores)
        db.add(registro)
        guardar(db, db.flush)
        auditoria.registrar(db, usuario, recurso.nombre, registro.id, "crear", datos.model_dump(exclude={"clave"}))
        guardar(db)
        return registro

    @router.put("/{registro_id}", response_model=salida)
    def actualizar(
        registro_id: int,
        datos: recurso.entrada,
        db=Depends(obtener_db),
        usuario=Depends(requiere_roles(*recurso.escritura)),
    ):
        registro = obtener_o_404(db, recurso.modelo, registro_id)
        valores = datos.model_dump()
        if recurso.preparar:
            valores = recurso.preparar(db, valores, registro)
        validar_referencias(db, recurso.modelo, valores)
        for campo, valor in valores.items():
            setattr(registro, campo, valor)
        auditoria.registrar(db, usuario, recurso.nombre, registro.id, "actualizar", datos.model_dump(exclude={"clave"}))
        guardar(db)
        return registro

    @router.delete("/{registro_id}", status_code=204)
    def eliminar(registro_id: int, db=Depends(obtener_db), usuario=Depends(requiere_roles(*recurso.borrado))):
        registro = obtener_o_404(db, recurso.modelo, registro_id)
        registro.eliminado = True
        auditoria.registrar(db, usuario, recurso.nombre, registro.id, "eliminar")
        guardar(db)

    return router
