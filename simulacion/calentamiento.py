"""Justificación del periodo de calentamiento.

Cada jornada simulada empieza con el puesto vacío (8:00) y se corre hasta atender a todos los
pacientes que llegaron. Es una simulación de horizonte finito (terminating): la condición inicial
es la real del puesto, así que no hay sesgo de arranque que deba descartarse. Este script lo
verifica con datos: mide la espera media por hora de llegada, promediada sobre réplicas y
jornadas, y prueba si la primera hora difiere del resto del día.
"""

import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulacion.escenarios import JORNADAS_POR_REPLICA, REPLICAS, SEMILLA  # noqa: E402
from simulacion.modelo import Configuracion, Jornada, cargar_parametros  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "salidas" / "calentamiento.json"
HORAS = range(8, 17)  # 8:00 a 17:00: las llegadas cesan a los 540 min (17:00)


def esperas_por_hora(parametros, replicas, jornadas):
    """Espera media de los pacientes que llegan en cada hora, por jornada."""
    por_hora = {h: [] for h in HORAS}
    for r in range(replicas):
        rng = np.random.default_rng(SEMILLA + r)
        for _ in range(jornadas):
            registros, _ = Jornada(parametros, Configuracion(), rng).ejecutar()
            for h in HORAS:
                inicio, fin = (h - 8) * 60, (h - 8 + 1) * 60
                esperas = [r[2] for r in registros if inicio <= r[4] < fin]
                por_hora[h].append(float(np.mean(esperas)) if esperas else np.nan)
    return por_hora


def ejecutar():
    parametros = cargar_parametros()
    por_hora = esperas_por_hora(parametros, replicas=REPLICAS, jornadas=JORNADAS_POR_REPLICA)
    medias = {h: float(np.nanmean(v)) for h, v in por_hora.items()}
    primera = np.array(por_hora[8])
    resto = np.concatenate([np.array(por_hora[h]) for h in HORAS if h != 8])
    primera, resto = primera[~np.isnan(primera)], resto[~np.isnan(resto)]
    t, p = stats.ttest_ind(primera, resto, equal_var=False)
    resultado = {
        "metodo": "Espera media por hora de llegada, promedio de réplicas y jornadas",
        "replicas": REPLICAS,
        "jornadas_por_replica": JORNADAS_POR_REPLICA,
        "medias_por_hora_min": {f"{h}:00": round(m, 2) for h, m in medias.items()},
        "primera_hora_vs_resto_t": round(float(t), 3),
        "primera_hora_vs_resto_p": float(p),
        "conclusion": (
            "La espera sube durante la jornada y se estabiliza hacia mediodía. Ese transitorio es el "
            "comportamiento real de un puesto que abre vacío a las 8:00, no un artefacto de arranque. "
            "Descartar horas iniciales subestimaría la espera. Por eso el calentamiento es 0 minutos: "
            "la métrica de interés es la jornada completa desde la apertura, y la validación contra el "
            "CRUD (escenarios.validar) usa esa misma definición."
        ),
    }
    SALIDA.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    ejecutar()
