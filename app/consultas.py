from math import ceil

from sqlalchemy import func, or_, select


def convertir(columna, valor):
    try:
        return columna.type.python_type(valor)
    except (ValueError, TypeError, NotImplementedError):
        return valor


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
