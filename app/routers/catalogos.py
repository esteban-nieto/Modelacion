from app.dependencias import ADMIN
from app.models import Cita, Paciente, Profesional, Sede, Servicio, Usuario
from app.negocio.preparaciones import preparar_cita, preparar_profesional, preparar_usuario
from app.recursos import Recurso, crear_router
from app.schemas import (
    CitaEntrada,
    CitaSalida,
    PacienteEntrada,
    PacienteSalida,
    ProfesionalEntrada,
    ProfesionalSalida,
    SedeEntrada,
    SedeSalida,
    ServicioEntrada,
    ServicioSalida,
    UsuarioEntrada,
    UsuarioSalida,
)

RECURSOS = [
    Recurso(
        "usuarios",
        Usuario,
        UsuarioEntrada,
        UsuarioSalida,
        ("nombre", "correo"),
        ("rol_id",),
        ("id", "nombre", "correo"),
        lectura=ADMIN,
        escritura=ADMIN,
        preparar=preparar_usuario,
    ),
    Recurso("sedes", Sede, SedeEntrada, SedeSalida, ("nombre", "vereda"), (), ("id", "nombre", "vereda")),
    Recurso(
        "servicios",
        Servicio,
        ServicioEntrada,
        ServicioSalida,
        ("nombre",),
        (),
        ("id", "nombre", "duracion_media_min"),
    ),
    Recurso(
        "profesionales",
        Profesional,
        ProfesionalEntrada,
        ProfesionalSalida,
        ("nombre",),
        ("sede_id",),
        ("id", "nombre"),
        preparar=preparar_profesional,
    ),
    Recurso(
        "pacientes",
        Paciente,
        PacienteEntrada,
        PacienteSalida,
        ("nombre", "documento"),
        (),
        ("id", "nombre", "documento"),
    ),
    Recurso(
        "citas",
        Cita,
        CitaEntrada,
        CitaSalida,
        ("estado", "prioridad"),
        ("sede_id", "servicio_id", "profesional_id", "paciente_id", "estado", "prioridad"),
        ("id", "llegada", "estado", "prioridad"),
        preparar=preparar_cita,
    ),
]

ROUTERS = [crear_router(recurso) for recurso in RECURSOS]
