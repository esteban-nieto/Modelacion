from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, motor
from app.routers import auth, catalogos, operacion

DIRECTORIO_ESTATICO = Path(__file__).resolve().parent.parent / "static"

ENCABEZADOS_SEGURIDAD = {
    "Content-Security-Policy": "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
}


@asynccontextmanager
async def ciclo_de_vida(_):
    Base.metadata.create_all(motor)
    yield


app = FastAPI(title="Gestión de turnos en puestos de salud rurales", version="1.0.0", lifespan=ciclo_de_vida)

# Mensajes de validación automática de FastAPI/Pydantic, traducidos al español.
# La forma de la respuesta (lista "detail" con loc/msg) se mantiene para la interfaz.
TRADUCCIONES = {
    "missing": "Campo obligatorio",
    "string_too_short": "Texto demasiado corto",
    "string_too_long": "Texto demasiado largo",
    "int_parsing": "Debe ser un número entero",
    "float_parsing": "Debe ser un número",
    "int_type": "Debe ser un número entero",
    "float_type": "Debe ser un número",
    "bool_parsing": "Debe ser verdadero o falso",
    "datetime_parsing": "Debe ser una fecha y hora válidas",
    "date_from_datetime_parsing": "Debe ser una fecha válida",
    "greater_than_equal": "Debe ser mayor o igual que el mínimo permitido",
    "less_than_equal": "Debe ser menor o igual que el máximo permitido",
    "json_invalid": "El cuerpo de la solicitud no es JSON válido",
}


@app.exception_handler(RequestValidationError)
async def errores_de_validacion(_, exc: RequestValidationError):
    errores = [
        {"loc": list(e["loc"]), "msg": TRADUCCIONES.get(e["type"], e["msg"]), "type": e["type"]}
        for e in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errores})


@app.middleware("http")
async def agregar_encabezados(request, siguiente):
    respuesta = await siguiente(request)
    if not request.url.path.startswith(("/docs", "/redoc", "/openapi")):
        respuesta.headers.update(ENCABEZADOS_SEGURIDAD)
    if request.url.path == "/" or request.url.path.startswith("/static"):
        # La interfaz cambia con frecuencia: el navegador debe revalidar en cada carga.
        respuesta.headers["Cache-Control"] = "no-cache"
    return respuesta


app.include_router(auth.router)
app.include_router(operacion.router)
for router in catalogos.ROUTERS:
    app.include_router(router)


@app.get("/", include_in_schema=False)
def inicio():
    return FileResponse(DIRECTORIO_ESTATICO / "index.html")


app.mount("/static", StaticFiles(directory=DIRECTORIO_ESTATICO), name="static")
