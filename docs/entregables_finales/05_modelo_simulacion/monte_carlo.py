import heapq
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from simulacion.modelo import MINUTOS_JORNADA, cargar_parametros, construir, servicios_de

SALIDA = Path(__file__).resolve().parent / "salidas"
ITERACIONES = 10_000
SEMILLA = 2025
PROBABILIDAD_AUSENCIA = 0.05
SIGMA_DEMANDA = 0.15
FACTOR_SERVICIO = (0.9, 1.0, 1.3)
UMBRAL_ESPERA_MIN = 30
PERCENTILES = (5, 50, 90, 95, 99)


def esperas_fila_unica(llegadas, duraciones, servidores):
    libres = [0.0] * servidores
    esperas = []
    for llegada, duracion in zip(llegadas, duraciones):
        libre = heapq.heappop(libres)
        inicio = max(llegada, libre)
        esperas.append(inicio - llegada)
        heapq.heappush(libres, inicio + duracion)
    return esperas


def esperas_fila_por_profesional(llegadas, duraciones, asignados, servidores):
    libres = [0.0] * servidores
    esperas = []
    for llegada, duracion, profesional in zip(llegadas, duraciones, asignados):
        inicio = max(llegada, libres[profesional])
        esperas.append(inicio - llegada)
        libres[profesional] = inicio + duracion
    return esperas


def jornada(rng, parametros, demanda, factor_servicio, fila_unica):
    esperas, sin_atender = [], 0
    for servicio in servicios_de(parametros):
        especificacion = parametros[servicio]
        escala_llegadas = especificacion["llegadas"]["parametros"][-1]
        cantidad = rng.poisson(MINUTOS_JORNADA * demanda / escala_llegadas)
        llegadas = np.sort(rng.uniform(0, MINUTOS_JORNADA, cantidad))
        duraciones = construir(especificacion["servicio"]).rvs(size=cantidad, random_state=rng) * factor_servicio
        presentes = int((rng.random(especificacion["profesionales"]) > PROBABILIDAD_AUSENCIA).sum())
        if presentes == 0:
            sin_atender += cantidad
        elif fila_unica:
            esperas.extend(esperas_fila_unica(llegadas, duraciones, presentes))
        else:
            asignados = rng.integers(presentes, size=cantidad)
            esperas.extend(esperas_fila_por_profesional(llegadas, duraciones, asignados, presentes))
    return (float(np.mean(esperas)) if esperas else 0.0), sin_atender


def simular(parametros, fila_unica, iteraciones=ITERACIONES, semilla=SEMILLA):
    rng = np.random.default_rng(semilla)
    medias, perdidos = [], []
    for _ in range(iteraciones):
        demanda = rng.lognormal(-SIGMA_DEMANDA**2 / 2, SIGMA_DEMANDA)
        factor = rng.triangular(*FACTOR_SERVICIO)
        media, sin_atender = jornada(rng, parametros, demanda, factor, fila_unica)
        medias.append(media)
        perdidos.append(sin_atender)
    return np.array(medias), np.array(perdidos)


def resumir(medias, perdidos):
    resumen = {f"p{p}": round(float(np.percentile(medias, p)), 2) for p in PERCENTILES}
    resumen.update(
        {
            "media": round(float(medias.mean()), 2),
            "desviacion": round(float(medias.std(ddof=1)), 2),
            "probabilidad_superar_umbral": round(float((medias > UMBRAL_ESPERA_MIN).mean()), 4),
            "pacientes_sin_atender_por_dia": round(float(perdidos.mean()), 3),
        }
    )
    return resumen


def graficar(actual, propuesta):
    figura, eje = plt.subplots(figsize=(9, 4.5))
    limite = max(np.percentile(actual, 99.5), np.percentile(propuesta, 99.5))
    cortes = np.linspace(0, limite, 50)
    eje.hist(actual, bins=cortes, alpha=0.6, label="Sistema actual", color="#b42318")
    eje.hist(propuesta, bins=cortes, alpha=0.6, label="Fila única", color="#0b6e4f")
    eje.axvline(UMBRAL_ESPERA_MIN, linestyle="--", color="black", label="Umbral de 30 min")
    eje.set_xlabel("Espera media diaria (min)")
    eje.set_ylabel("Jornadas simuladas")
    eje.set_title(f"Monte Carlo con {len(actual):,} iteraciones".replace(",", "."))
    eje.legend()
    figura.tight_layout()
    figura.savefig(SALIDA / "monte_carlo_histograma.png", dpi=150)
    plt.close(figura)


def ejecutar():
    parametros = cargar_parametros()
    actual, perdidos_actual = simular(parametros, fila_unica=False)
    propuesta, perdidos_propuesta = simular(parametros, fila_unica=True)
    resultados = {
        "iteraciones": ITERACIONES,
        "supuestos": {
            "probabilidad_ausencia_profesional": PROBABILIDAD_AUSENCIA,
            "sigma_log_demanda": SIGMA_DEMANDA,
            "factor_servicio_triangular": FACTOR_SERVICIO,
            "umbral_espera_min": UMBRAL_ESPERA_MIN,
        },
        "sistema_actual": resumir(actual, perdidos_actual),
        "fila_unica": resumir(propuesta, perdidos_propuesta),
    }
    (SALIDA / "monte_carlo.json").write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    graficar(actual, propuesta)
    print(json.dumps(resultados, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    ejecutar()
