from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.database import obtener_db
from app.dependencias import usuario_actual
from app.models import Usuario
from app.schemas import LoginEntrada, LoginSalida, UsuarioSalida
from app.seguridad import crear_token, verificar_clave

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginSalida)
def iniciar_sesion(datos: LoginEntrada, db=Depends(obtener_db)):
    usuario = db.scalar(select(Usuario).where(Usuario.correo == datos.correo, Usuario.eliminado.is_(False)))
    if usuario is None or not verificar_clave(datos.clave, usuario.clave_hash):
        raise HTTPException(401, "Correo o clave incorrectos")
    return LoginSalida(token=crear_token(usuario.id, usuario.rol.nombre), nombre=usuario.nombre, rol=usuario.rol.nombre)


@router.get("/yo", response_model=UsuarioSalida)
def usuario_en_sesion(usuario=Depends(usuario_actual)):
    return usuario
