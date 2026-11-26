import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import simpy
from scipy import stats

MINUTOS_JORNADA = 540
RUTA_PARAMETROS = Path(__file__).resolve().parent / "salidas" / "parametros.json"


@dataclass(frozen=True)
class Configuracion:
    cola_unica: bool = False
    prioridad: bool = False
    factor_demanda: float = 1.0
    factor_servicio: float = 1.0
    profesionales_extra: dict = field(default_factory=dict)


def cargar_parametros(ruta=RUTA_PARAMETROS):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def servicios_de(parametros):
    return [nombre for nombre in parametros if not nombre.startswith("_")]


def construir(especificacion):
    return getattr(stats, especificacion["distribucion"])(*especificacion["parametros"])


class Muestreador:
    def __init__(self, distribucion, rng, bloque=2048):
        self.distribucion = distribucion
        self.rng = rng
        self.bloque = bloque
        self.valores = iter(())

    def siguiente(self):
        try:
            return next(self.valores)
        except StopIteration:
            muestra = np.maximum(self.distribucion.rvs(size=self.bloque, random_state=self.rng), 0.0)
            self.valores = iter(muestra.tolist())
            return next(self.valores)


class Jornada:
    def __init__(self, parametros, configuracion, rng):
        self.parametros = parametros
        self.configuracion = configuracion
        self.rng = rng
        self.entorno = simpy.Environment()
        self.registros = []
        self.minutos_atencion = {}

    def recursos_de(self, servicio):
        cantidad = self.parametros[servicio]["profesionales"] + self.configuracion.profesionales_extra.get(servicio, 0)
        if self.configuracion.cola_unica:
            return [simpy.PriorityResource(self.entorno, capacity=cantidad)]
        return [simpy.PriorityResource(self.entorno, capacity=1) for _ in range(cantidad)]

    def paciente(self, servicio, recursos, muestreo_servicio, prioritario):
        llegada = self.entorno.now
        recurso = recursos[int(self.rng.integers(len(recursos)))]
        orden = 0 if (self.configuracion.prioridad and prioritario) else 1
        with recurso.request(priority=orden) as turno:
            yield turno
            espera = self.entorno.now - llegada
            duracion = muestreo_servicio.siguiente() * self.configuracion.factor_servicio
            yield self.entorno.timeout(duracion)
        self.minutos_atencion[servicio] += duracion
        self.registros.append((servicio, prioritario, espera, duracion, llegada))

    def llegadas(self, servicio):
        especificacion = self.parametros[servicio]
        recursos = self.recursos_de(servicio)
        muestreo_llegadas = Muestreador(construir(especificacion["llegadas"]), self.rng)
        muestreo_servicio = Muestreador(construir(especificacion["servicio"]), self.rng)
        fraccion = self.parametros["_global"]["fraccion_prioritaria"]
        while True:
            yield self.entorno.timeout(muestreo_llegadas.siguiente() / self.configuracion.factor_demanda)
            if self.entorno.now > MINUTOS_JORNADA:
                break
            prioritario = bool(self.rng.random() < fraccion)
            self.entorno.process(self.paciente(servicio, recursos, muestreo_servicio, prioritario))

    def ejecutar(self):
        for servicio in servicios_de(self.parametros):
            self.minutos_atencion[servicio] = 0.0
            self.entorno.process(self.llegadas(servicio))
        self.entorno.run()
        return self.registros, self.minutos_atencion


def resumir(registros, minutos_atencion, parametros, configuracion, jornadas):
    esperas = np.array([r[2] for r in registros])
    esperas_prioritarias = np.array([r[2] for r in registros if r[1]])
    capacidad = sum(
        (parametros[s]["profesionales"] + configuracion.profesionales_extra.get(s, 0)) * MINUTOS_JORNADA * jornadas
        for s in servicios_de(parametros)
    )
    resumen = {
        "espera_media_min": float(esperas.mean()),
        "espera_prioritarios_min": float(esperas_prioritarias.mean()) if len(esperas_prioritarias) else 0.0,
        "espera_p90_min": float(np.percentile(esperas, 90)),
        "ocupacion_pct": 100 * sum(minutos_atencion.values()) / capacidad,
        "citas_por_dia": len(registros) / jornadas,
    }
    for servicio in servicios_de(parametros):
        propias = [r[2] for r in registros if r[0] == servicio]
        resumen[f"espera_{servicio}"] = float(np.mean(propias)) if propias else 0.0
        cantidad = parametros[servicio]["profesionales"] + configuracion.profesionales_extra.get(servicio, 0)
        resumen[f"ocupacion_{servicio}"] = 100 * minutos_atencion[servicio] / (cantidad * MINUTOS_JORNADA * jornadas)
    return resumen


def replica(parametros, configuracion, semilla, jornadas=20):
    rng = np.random.default_rng(semilla)
    registros, minutos = [], {}
    for _ in range(jornadas):
        nuevos, usados = Jornada(parametros, configuracion, rng).ejecutar()
        registros.extend(nuevos)
        for servicio, valor in usados.items():
            minutos[servicio] = minutos.get(servicio, 0.0) + valor
    return resumir(registros, minutos, parametros, configuracion, jornadas)


def esperas_diarias(parametros, configuracion, jornadas, semilla):
    rng = np.random.default_rng(semilla)
    medias = []
    for _ in range(jornadas):
        registros, _ = Jornada(parametros, configuracion, rng).ejecutar()
        medias.append(float(np.mean([r[2] for r in registros])))
    return medias
