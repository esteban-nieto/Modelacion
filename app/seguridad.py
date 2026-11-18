import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt

from app import config

PARAMETROS_SCRYPT = {"n": 2**14, "r": 8, "p": 1}


def _derivar(clave, sal):
    return hashlib.scrypt(clave.encode(), salt=sal, **PARAMETROS_SCRYPT)


def hashear_clave(clave):
    sal = os.urandom(16)
    return f"{sal.hex()}${_derivar(clave, sal).hex()}"


def verificar_clave(clave, almacenada):
    sal_hex, hash_hex = almacenada.split("$")
    return hmac.compare_digest(_derivar(clave, bytes.fromhex(sal_hex)), bytes.fromhex(hash_hex))


def _clave_secreta():
    if not config.SECRET_KEY:
        raise RuntimeError("Falta la variable de entorno SECRET_KEY")
    return config.SECRET_KEY


def crear_token(usuario_id, rol):
    expira = datetime.now(timezone.utc) + timedelta(minutes=config.TOKEN_MINUTOS)
    return jwt.encode({"sub": str(usuario_id), "rol": rol, "exp": expira}, _clave_secreta(), algorithm="HS256")


def leer_token(token):
    return jwt.decode(token, _clave_secreta(), algorithms=["HS256"])
