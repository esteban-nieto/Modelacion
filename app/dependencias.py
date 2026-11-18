import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import obtener_db
from app.models import Usuario
from app.seguridad import leer_token

esquema = HTTPBearer(auto_error=False)

TODOS = ("administrador", "operador", "consulta")
ESCRITURA = ("administrador", "operador")
ADMIN = ("administrador",)


def usuario_actual(credenciales: HTTPAuthorizationCredentials | None = Depends(esquema), db=Depends(obtener_db)):
    if credenciales is None:
        raise HTTPException(401, "Autenticación requerida")
    try:
        datos = leer_token(credenciales.credentials)
    except jwt.PyJWTError:
        raise HTTPException(401, "Token inválido o vencido")
    usuario = db.get(Usuario, int(datos["sub"]))
    if usuario is None or usuario.eliminado:
        raise HTTPException(401, "Usuario no disponible")
    return usuario


def requiere_roles(*roles):
    def verificar(usuario=Depends(usuario_actual)):
        if usuario.rol.nombre not in roles:
            raise HTTPException(403, "No tiene permisos para esta operación")
        return usuario

    return verificar
