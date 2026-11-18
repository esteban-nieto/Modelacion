from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

T = TypeVar("T")


class Pagina(BaseModel, Generic[T]):
    total: int
    pagina: int
    tamano: int
    paginas: int
    items: list[T]


class Salida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int


class RolSalida(Salida):
    nombre: str


class UsuarioEntrada(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    correo: EmailStr
    clave: str | None = None
    rol_id: int = Field(gt=0)

    @field_validator("clave")
    @classmethod
    def clave_segura(cls, valor):
        if valor is None:
            return valor
        if len(valor) < 8 or not any(c.isalpha() for c in valor) or not any(c.isdigit() for c in valor):
            raise ValueError("La clave debe tener al menos 8 caracteres, con letras y números")
        return valor


class UsuarioSalida(Salida):
    nombre: str
    correo: str
    rol: RolSalida


class SedeEntrada(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    vereda: str = Field(min_length=3, max_length=100)


class SedeSalida(SedeEntrada, Salida):
    pass


class ServicioEntrada(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    duracion_media_min: int = Field(ge=1, le=240)


class ServicioSalida(ServicioEntrada, Salida):
    pass


class ProfesionalEntrada(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    sede_id: int = Field(gt=0)
    servicios_ids: list[int] = Field(min_length=1)


class ProfesionalSalida(Salida):
    nombre: str
    sede_id: int
    servicios: list[ServicioSalida]


class PacienteEntrada(BaseModel):
    documento: str = Field(pattern=r"^\d{5,15}$")
    nombre: str = Field(min_length=3, max_length=100)
    telefono: str = Field(pattern=r"^\d{7,15}$")
    fecha_nacimiento: datetime


class PacienteSalida(PacienteEntrada, Salida):
    pass


class CitaEntrada(BaseModel):
    paciente_id: int = Field(gt=0)
    profesional_id: int = Field(gt=0)
    servicio_id: int = Field(gt=0)
    sede_id: int = Field(gt=0)
    llegada: datetime
    inicio_atencion: datetime | None = None
    fin_atencion: datetime | None = None
    estado: Literal["programada", "atendida", "cancelada", "no_asistio"] = "programada"
    prioridad: Literal["normal", "prioritaria"] = "normal"

    @model_validator(mode="after")
    def tiempos_coherentes(self):
        if self.inicio_atencion and self.inicio_atencion < self.llegada:
            raise ValueError("El inicio de atención no puede ser anterior a la llegada")
        if self.fin_atencion and (not self.inicio_atencion or self.fin_atencion < self.inicio_atencion):
            raise ValueError("El fin de atención debe ser posterior al inicio")
        if self.estado == "atendida" and not self.fin_atencion:
            raise ValueError("Una cita atendida requiere inicio y fin de atención")
        return self


class CitaSalida(CitaEntrada, Salida):
    pass


class AuditoriaSalida(Salida):
    usuario_id: int | None
    entidad: str
    registro_id: int
    accion: str
    detalle: str
    fecha: datetime


class LoginEntrada(BaseModel):
    correo: EmailStr
    clave: str = Field(min_length=1)


class LoginSalida(BaseModel):
    token: str
    nombre: str
    rol: str
