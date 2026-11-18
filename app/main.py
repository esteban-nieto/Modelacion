from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
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


@app.middleware("http")
async def agregar_encabezados(request, siguiente):
    respuesta = await siguiente(request)
    if not request.url.path.startswith(("/docs", "/redoc", "/openapi")):
        respuesta.headers.update(ENCABEZADOS_SEGURIDAD)
    return respuesta


app.include_router(auth.router)
app.include_router(operacion.router)
for router in catalogos.ROUTERS:
    app.include_router(router)


@app.get("/", include_in_schema=False)
def inicio():
    return FileResponse(DIRECTORIO_ESTATICO / "index.html")


app.mount("/static", StaticFiles(directory=DIRECTORIO_ESTATICO), name="static")
