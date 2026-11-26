from math import ceil

from fastapi import HTTPException
from sqlalchemy import func, or_, select


def convertir(columna, valor):
    """Convierte el valor de un filtro al tipo de la columna.

    Si el valor no se puede convertir, responde 422 con un mensaje claro en lugar de
    ignorar el filtro en silencio. Los tipos sin conversión conocida pasan como texto.
    """
    try:
        tipo = columna.type.python_type
    except NotImplementedError:
        return valor
    try:
        return tipo(valor)
    except (ValueError, TypeError):
        raise HTTPException(422, f"Valor no válido para el filtro '{columna.key}': {valor!r}")


def listar(db, modelo, filtros, busqueda, campos_busqueda, orden, direccion, pagina, tamano):
    consulta = select(modelo)
    if hasattr(modelo, "eliminado"):
        consulta = consulta.where(modelo.eliminado.is_(False))
    for campo, valor in filtros.items():
        columna = getattr(modelo, campo)
        consulta = consulta.where(columna == convertir(columna, valor))
    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.where(or_(*[getattr(modelo, c).ilike(patron) for c in campos_busqueda]))
    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    columna_orden = getattr(modelo, orden)
    columna_orden = columna_orden.desc() if direccion == "desc" else columna_orden.asc()
    items = db.scalars(consulta.order_by(columna_orden).offset((pagina - 1) * tamano).limit(tamano)).all()
    return {
        "total": total,
        "pagina": pagina,
        "tamano": tamano,
        "paginas": ceil(total / tamano) if total else 0,
        "items": items,
    }
