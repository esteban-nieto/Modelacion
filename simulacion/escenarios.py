import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from simulacion.modelo import Configuracion, cargar_parametros, esperas_diarias, replica, servicios_de

CARPETA = Path(__file__).resolve().parent
DATOS = CARPETA / "datos" / "citas_historicas.csv"
SALIDA = CARPETA / "salidas"

REPLICAS = 30
JORNADAS_POR_REPLICA = 20
JORNADAS_VALIDACION = 400
SEMILLA = 12345
NIVEL = 0.95
PESO_GLOBAL = 0.7
METRICAS_CLAVE = ["espera_media_min", "espera_prioritarios_min", "espera_p90_min", "ocupacion_pct", "citas_por_dia"]

ESCENARIOS = {
    "base": {
        "descripcion": "Sistema actual: cada paciente queda en la fila de un profesional y se atiende en orden de llegada",
        "configuracion": Configuracion(),
        "tipo": "referencia",
        "costo_extra": 0,
    },
    "cola_unica": {
        "descripcion": "Una sola fila por servicio: el siguiente paciente lo atiende el primer profesional libre",
        "configuracion": Configuracion(cola_unica=True),
        "tipo": "mejora",
        "costo_extra": 0,
    },
    "cola_unica_prioridad": {
        "descripcion": "Fila única con prioridad para pacientes prioritarios",
        "configuracion": Configuracion(cola_unica=True, prioridad=True),
        "tipo": "mejora",
        "costo_extra": 0,
    },
    "medico_adicional": {
        "descripcion": "Se contrata un médico general adicional manteniendo filas por profesional",
        "configuracion": Configuracion(profesionales_extra={"Medicina general": 1}),
        "tipo": "mejora",
        "costo_extra": 1,
    },
    "demanda_mas_25": {
        "descripcion": "Aumento de la demanda del 25 % con el sistema actual",
        "configuracion": Configuracion(factor_demanda=1.25),
        "tipo": "estres",
        "costo_extra": 0,
    },
    "demanda_mas_25_recomendado": {
        "descripcion": "Aumento de la demanda del 25 % con fila única y prioridad",
        "configuracion": Configuracion(cola_unica=True, prioridad=True, factor_demanda=1.25),
        "tipo": "estres",
        "costo_extra": 0,
    },
}


def intervalo(valores):
    valores = np.asarray(valores, dtype=float)
    media = float(valores.mean())
    margen = float(stats.t.ppf(0.5 + NIVEL / 2, len(valores) - 1) * valores.std(ddof=1) / np.sqrt(len(valores)))
    return {"media": round(media, 3), "ic_inf": round(media - margen, 3), "ic_sup": round(media + margen, 3)}


def correr_escenario(parametros, configuracion):
    return [replica(parametros, configuracion, SEMILLA + i, JORNADAS_POR_REPLICA) for i in range(REPLICAS)]


def resumen_escenario(corridas, base):
    llaves = list(corridas[0].keys())
    resumen = {llave: intervalo([c[llave] for c in corridas]) for llave in llaves}
    if base is None:
        return resumen, {}
    diferencias = {
        llave: intervalo([c[llave] - b[llave] for c, b in zip(corridas, base)]) for llave in METRICAS_CLAVE
    }
    return resumen, diferencias


def puntaje(escenario):
    metricas = escenario["metricas"]
    return PESO_GLOBAL * metricas["espera_media_min"]["media"] + (1 - PESO_GLOBAL) * metricas["espera_prioritarios_min"]["media"]


def elegir_recomendado(escenarios):
    candidatos = {
        n: e for n, e in escenarios.items() if e["tipo"] == "mejora" and e["costo_extra"] == 0
    }
    return min(candidatos, key=lambda nombre: puntaje(candidatos[nombre]))


def validar(parametros):
    datos = pd.read_csv(DATOS, parse_dates=["llegada"])
    reales = datos.groupby(datos["llegada"].dt.date)["espera_min"].mean().to_numpy()
    simuladas = np.array(esperas_diarias(parametros, Configuracion(), JORNADAS_VALIDACION, SEMILLA + 999))
    welch = stats.ttest_ind(reales, simuladas, equal_var=False)
    ks = stats.ks_2samp(reales, simuladas)
    mann = stats.mannwhitneyu(reales, simuladas)
    return {
        "dias_reales": int(len(reales)),
        "jornadas_simuladas": int(len(simuladas)),
        "espera_diaria_real_media": round(float(reales.mean()), 3),
        "espera_diaria_simulada_media": round(float(simuladas.mean()), 3),
        "welch_t_p": round(float(welch.pvalue), 4),
        "ks_dos_muestras_p": round(float(ks.pvalue), 4),
        "mann_whitney_p": round(float(mann.pvalue), 4),
        "conclusion": "No se rechaza la igualdad entre el comportamiento real y el simulado (p > 0,05)"
        if min(welch.pvalue, ks.pvalue, mann.pvalue) > 0.05
        else "Hay evidencia de diferencia entre el comportamiento real y el simulado",
    }


def sensibilidad(parametros, recomendado):
    filas = []
    for nombre, base in (("base", Configuracion()), (recomendado, ESCENARIOS[recomendado]["configuracion"])):
        for factor_demanda in (0.8, 1.0, 1.2, 1.4):
            for factor_servicio in (0.9, 1.0, 1.1):
                configuracion = Configuracion(
                    cola_unica=base.cola_unica,
                    prioridad=base.prioridad,
                    factor_demanda=factor_demanda,
                    factor_servicio=factor_servicio,
                )
                corridas = [replica(parametros, configuracion, SEMILLA + i, JORNADAS_POR_REPLICA) for i in range(10)]
                filas.append(
                    {
                        "escenario": nombre,
                        "factor_demanda": factor_demanda,
                        "factor_servicio": factor_servicio,
                        "espera_media_min": intervalo([c["espera_media_min"] for c in corridas])["media"],
                        "ocupacion_pct": intervalo([c["ocupacion_pct"] for c in corridas])["media"],
                    }
                )
    return filas


def graficar(escenarios):
    nombres = list(escenarios)
    medias = [escenarios[n]["metricas"]["espera_media_min"]["media"] for n in nombres]
    errores = [escenarios[n]["metricas"]["espera_media_min"]["media"] - escenarios[n]["metricas"]["espera_media_min"]["ic_inf"] for n in nombres]
    figura, eje = plt.subplots(figsize=(9, 4.5))
    eje.bar(nombres, medias, yerr=errores, capsize=4, color="#0b6e4f")
    eje.set_ylabel("Espera media (min)")
    eje.set_title("Espera media por escenario con IC del 95 %")
    plt.setp(eje.get_xticklabels(), rotation=20, ha="right")
    figura.tight_layout()
    figura.savefig(SALIDA / "espera_escenarios.png", dpi=150)
    plt.close(figura)


def ejecutar():
    parametros = cargar_parametros()
    corridas = {nombre: correr_escenario(parametros, e["configuracion"]) for nombre, e in ESCENARIOS.items()}
    escenarios = {}
    for nombre, definicion in ESCENARIOS.items():
        metricas, diferencias = resumen_escenario(corridas[nombre], None if nombre == "base" else corridas["base"])
        escenarios[nombre] = {
            "descripcion": definicion["descripcion"],
            "tipo": definicion["tipo"],
            "costo_extra": definicion["costo_extra"],
            "metricas": metricas,
            "diferencia_vs_base": diferencias,
        }
    recomendado = elegir_recomendado(escenarios)
    base = escenarios["base"]["metricas"]
    cuellos = {s: base[f"ocupacion_{s}"]["media"] for s in servicios_de(parametros)}
    resultados = {
        "configuracion": {
            "replicas": REPLICAS,
            "jornadas_por_replica": JORNADAS_POR_REPLICA,
            "calentamiento_min": 0,
            "nivel_confianza": NIVEL,
            "semilla": SEMILLA,
        },
        "validacion": validar(parametros),
        "escenarios": escenarios,
        "recomendado": recomendado,
        "cuellos_de_botella_ocupacion_pct": cuellos,
        "sensibilidad": sensibilidad(parametros, recomendado),
    }
    (SALIDA / "resultados.json").write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    graficar(escenarios)
    print("Recomendado:", recomendado)
    for nombre, e in escenarios.items():
        print(nombre, e["metricas"]["espera_media_min"], e["metricas"]["espera_prioritarios_min"]["media"], e["metricas"]["ocupacion_pct"]["media"])
    print(resultados["validacion"])


if __name__ == "__main__":
    ejecutar()
