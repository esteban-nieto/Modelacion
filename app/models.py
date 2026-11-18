from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

profesional_servicio = Table(
    "profesional_servicio",
    Base.metadata,
    Column("profesional_id", ForeignKey("profesionales.id"), primary_key=True),
    Column("servicio_id", ForeignKey("servicios.id"), primary_key=True),
)


class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(30), unique=True)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    correo: Mapped[str] = mapped_column(String(120), unique=True)
    clave_hash: Mapped[str] = mapped_column(String(200))
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    eliminado: Mapped[bool] = mapped_column(default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    rol: Mapped[Rol] = relationship(lazy="joined")


class Sede(Base):
    __tablename__ = "sedes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    vereda: Mapped[str] = mapped_column(String(100))
    eliminado: Mapped[bool] = mapped_column(default=False)


class Servicio(Base):
    __tablename__ = "servicios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    duracion_media_min: Mapped[int] = mapped_column(Integer)
    eliminado: Mapped[bool] = mapped_column(default=False)


class Profesional(Base):
    __tablename__ = "profesionales"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    sede_id: Mapped[int] = mapped_column(ForeignKey("sedes.id"))
    eliminado: Mapped[bool] = mapped_column(default=False)
    servicios: Mapped[list[Servicio]] = relationship(secondary=profesional_servicio, lazy="selectin")


class Paciente(Base):
    __tablename__ = "pacientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    documento: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    telefono: Mapped[str] = mapped_column(String(20))
    fecha_nacimiento: Mapped[datetime] = mapped_column(DateTime)
    eliminado: Mapped[bool] = mapped_column(default=False)


class Cita(Base):
    __tablename__ = "citas"

    id: Mapped[int] = mapped_column(primary_key=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("pacientes.id"))
    profesional_id: Mapped[int] = mapped_column(ForeignKey("profesionales.id"))
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicios.id"))
    sede_id: Mapped[int] = mapped_column(ForeignKey("sedes.id"))
    llegada: Mapped[datetime] = mapped_column(DateTime, index=True)
    inicio_atencion: Mapped[datetime | None] = mapped_column(DateTime)
    fin_atencion: Mapped[datetime | None] = mapped_column(DateTime)
    estado: Mapped[str] = mapped_column(String(20), default="programada")
    prioridad: Mapped[str] = mapped_column(String(20), default="normal")
    eliminado: Mapped[bool] = mapped_column(default=False)


class Auditoria(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    entidad: Mapped[str] = mapped_column(String(40), index=True)
    registro_id: Mapped[int] = mapped_column(Integer)
    accion: Mapped[str] = mapped_column(String(20))
    detalle: Mapped[str] = mapped_column(Text, default="")
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
