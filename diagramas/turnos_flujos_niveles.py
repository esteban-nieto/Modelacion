"""
Python model 'turnos_flujos_niveles.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.functions import if_then_else
from pysd.py_backend.statefuls import Integ
from pysd import Component

__pysd_version__ = "3.14.3"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 0,
    "final_time": lambda: 12,
    "time_step": lambda: 0.0625,
    "saveper": lambda: time_step(),
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="FINAL TIME", units="Hora", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    Parametro de control de la simulacion
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="Hora", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    Parametro de control de la simulacion
    """
    return __data["time"].initial_time()


@component.add(
    name="TIME STEP", units="Hora", comp_type="Constant", comp_subtype="Normal"
)
def time_step():
    """
    Parametro de control de la simulacion
    """
    return __data["time"].time_step()


@component.add(
    name="SAVEPER",
    units="Hora",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    """
    Frecuencia de registro
    """
    return __data["time"].saveper()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name="Cola de espera",
    units="pacientes",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_cola_de_espera": 1},
    other_deps={
        "_integ_cola_de_espera": {
            "initial": {},
            "step": {"llegadas": 1, "inicio_de_atencion": 1, "abandonos": 1},
        }
    },
)
def cola_de_espera():
    """
    Pacientes esperando turno
    """
    return _integ_cola_de_espera()


_integ_cola_de_espera = Integ(
    lambda: llegadas() - inicio_de_atencion() - abandonos(),
    lambda: 0,
    "_integ_cola_de_espera",
)


@component.add(
    name="En atencion",
    units="pacientes",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_en_atencion": 1},
    other_deps={
        "_integ_en_atencion": {
            "initial": {},
            "step": {"inicio_de_atencion": 1, "fin_de_atencion": 1},
        }
    },
)
def en_atencion():
    """
    Pacientes siendo atendidos
    """
    return _integ_en_atencion()


_integ_en_atencion = Integ(
    lambda: inicio_de_atencion() - fin_de_atencion(), lambda: 0, "_integ_en_atencion"
)


@component.add(
    name="Atendidos",
    units="pacientes",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_atendidos": 1},
    other_deps={"_integ_atendidos": {"initial": {}, "step": {"fin_de_atencion": 1}}},
)
def atendidos():
    """
    Pacientes atendidos en la jornada
    """
    return _integ_atendidos()


_integ_atendidos = Integ(lambda: fin_de_atencion(), lambda: 0, "_integ_atendidos")


@component.add(
    name="Abandonos acumulados",
    units="pacientes",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_abandonos_acumulados": 1},
    other_deps={
        "_integ_abandonos_acumulados": {"initial": {}, "step": {"abandonos": 1}}
    },
)
def abandonos_acumulados():
    """
    Pacientes que se retiran sin atencion
    """
    return _integ_abandonos_acumulados()


_integ_abandonos_acumulados = Integ(
    lambda: abandonos(), lambda: 0, "_integ_abandonos_acumulados"
)


@component.add(
    name="Confianza comunitaria",
    units="Dmnl",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_confianza_comunitaria": 1},
    other_deps={
        "_integ_confianza_comunitaria": {
            "initial": {},
            "step": {"ganancia_de_confianza": 1, "perdida_de_confianza": 1},
        }
    },
)
def confianza_comunitaria():
    """
    Confianza de la comunidad en el puesto de salud
    """
    return _integ_confianza_comunitaria()


_integ_confianza_comunitaria = Integ(
    lambda: ganancia_de_confianza() - perdida_de_confianza(),
    lambda: 0.75,
    "_integ_confianza_comunitaria",
)


@component.add(
    name="Llegadas",
    units="pacientes/Hora",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "duracion_de_jornada": 1,
        "factor_de_demanda": 1,
        "efecto_de_la_confianza": 1,
        "tasa_base_de_llegadas": 1,
    },
)
def llegadas():
    """
    Llegada de pacientes durante la jornada
    """
    return if_then_else(
        time() < duracion_de_jornada(),
        lambda: tasa_base_de_llegadas()
        * factor_de_demanda()
        * efecto_de_la_confianza(),
        lambda: 0,
    )


@component.add(
    name="Inicio de atencion",
    units="pacientes/Hora",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cola_de_espera": 1, "time_step": 2, "profesionales_libres": 1},
)
def inicio_de_atencion():
    """
    Pacientes que pasan a consulta
    """
    return float(
        np.minimum(cola_de_espera() / time_step(), profesionales_libres() / time_step())
    )


@component.add(
    name="Fin de atencion",
    units="pacientes/Hora",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"en_atencion": 1, "duracion_de_atencion": 1},
)
def fin_de_atencion():
    """
    Pacientes que terminan su consulta
    """
    return en_atencion() / duracion_de_atencion()


@component.add(
    name="Abandonos",
    units="pacientes/Hora",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cola_de_espera": 1, "fraccion_de_abandono": 1},
)
def abandonos():
    """
    Pacientes que se retiran por la espera
    """
    return cola_de_espera() * fraccion_de_abandono()


@component.add(
    name="Ganancia de confianza",
    units="1/Hora",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fin_de_atencion": 1, "efecto_por_atencion": 1},
)
def ganancia_de_confianza():
    """
    La atencion oportuna aumenta la confianza
    """
    return fin_de_atencion() * efecto_por_atencion()


@component.add(
    name="Perdida de confianza",
    units="1/Hora",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "abandonos": 1,
        "efecto_por_abandono": 1,
        "tiempo_de_espera_estimado": 1,
        "efecto_por_espera_larga": 1,
        "tolerancia_de_espera": 1,
    },
)
def perdida_de_confianza():
    """
    Abandonos y esperas largas reducen la confianza
    """
    return (
        abandonos() * efecto_por_abandono()
        + float(np.maximum(tiempo_de_espera_estimado() - tolerancia_de_espera(), 0))
        * efecto_por_espera_larga()
    )


@component.add(
    name="Efecto de la confianza",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"confianza_comunitaria": 1},
)
def efecto_de_la_confianza():
    """
    Factor de demanda segun la confianza
    """
    return 0.4 + 0.8 * float(
        np.maximum(0, float(np.minimum(1, confianza_comunitaria())))
    )


@component.add(
    name="Profesionales libres",
    units="profesionales",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"profesionales": 1, "en_atencion": 1},
)
def profesionales_libres():
    """
    Profesionales sin paciente
    """
    return float(np.maximum(profesionales() - en_atencion(), 0))


@component.add(
    name="Capacidad de atencion",
    units="pacientes/Hora",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"profesionales": 1, "duracion_de_atencion": 1},
)
def capacidad_de_atencion():
    """
    Pacientes que el puesto puede atender por hora
    """
    return profesionales() / duracion_de_atencion()


@component.add(
    name="Tiempo de espera estimado",
    units="Hora",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cola_de_espera": 1, "capacidad_de_atencion": 1},
)
def tiempo_de_espera_estimado():
    """
    Espera esperada para quien llega
    """
    return cola_de_espera() / capacidad_de_atencion()


@component.add(
    name="Fraccion de abandono",
    units="1/Hora",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"sensibilidad_al_abandono": 1, "tiempo_de_espera_estimado": 1},
)
def fraccion_de_abandono():
    """
    Proporcion de la cola que se retira por hora
    """
    return float(
        np.minimum(0.5, sensibilidad_al_abandono() * tiempo_de_espera_estimado())
    )


@component.add(
    name="Tasa base de llegadas",
    units="pacientes/Hora",
    comp_type="Constant",
    comp_subtype="Normal",
)
def tasa_base_de_llegadas():
    """
    Llegadas por hora con confianza media
    """
    return 8.4


@component.add(
    name="Factor de demanda", units="Dmnl", comp_type="Constant", comp_subtype="Normal"
)
def factor_de_demanda():
    """
    Multiplicador para probar escenarios de demanda
    """
    return 1


@component.add(
    name="Duracion de jornada",
    units="Hora",
    comp_type="Constant",
    comp_subtype="Normal",
)
def duracion_de_jornada():
    """
    Horas en que se reciben pacientes
    """
    return 9


@component.add(
    name="Profesionales",
    units="profesionales",
    comp_type="Constant",
    comp_subtype="Normal",
)
def profesionales():
    """
    Profesionales de salud disponibles
    """
    return 4


@component.add(
    name="Duracion de atencion",
    units="Hora",
    comp_type="Constant",
    comp_subtype="Normal",
)
def duracion_de_atencion():
    """
    Duracion media de una consulta
    """
    return 0.29


@component.add(
    name="Efecto por atencion",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def efecto_por_atencion():
    """
    Confianza ganada por paciente atendido
    """
    return 0.002


@component.add(
    name="Efecto por abandono",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def efecto_por_abandono():
    """
    Confianza perdida por abandono
    """
    return 0.01


@component.add(
    name="Tolerancia de espera",
    units="Hora",
    comp_type="Constant",
    comp_subtype="Normal",
)
def tolerancia_de_espera():
    """
    Espera aceptada por la comunidad
    """
    return 0.5


@component.add(
    name="Efecto por espera larga",
    units="1/Hora",
    comp_type="Constant",
    comp_subtype="Normal",
)
def efecto_por_espera_larga():
    """
    Confianza perdida por esperas superiores a la tolerancia
    """
    return 0.05


@component.add(
    name="Sensibilidad al abandono",
    units="1/Hora/Hora",
    comp_type="Constant",
    comp_subtype="Normal",
)
def sensibilidad_al_abandono():
    """
    Que tan rapido abandonan los pacientes al esperar
    """
    return 0.1
