import json

from app.models import Auditoria


def registrar(db, usuario, entidad, registro_id, accion, detalle=None):
    db.add(
        Auditoria(
            usuario_id=usuario.id if usuario else None,
            entidad=entidad,
            registro_id=registro_id,
            accion=accion,
            detalle=json.dumps(detalle, default=str, ensure_ascii=False) if detalle else "",
        )
    )
