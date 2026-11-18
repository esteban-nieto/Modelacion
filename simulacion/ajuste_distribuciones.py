import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

CARPETA = Path(__file__).resolve().parent
ENTRADA = CARPETA / "datos" / "citas_historicas.csv"
SALIDA_TABLA = CARPETA / "salidas" / "ajuste_distribuciones.csv"
SALIDA_PARAMETROS = CARPETA / "salidas" / "parametros.json"

CANDIDATAS = ["expon", "gamma", "lognorm", "weibull_min", "norm"]
CLASES_CHI = 10
NIVEL = 0.05
APERTURA_HORA = 7
MINUTOS_JORNADA = 540


def tiempos_entre_llegadas(grupo):
    apertura = grupo["llegada"].dt.normalize() + pd.Timedelta(hours=APERTURA_HORA)
    llegadas = pd.concat([apertura.drop_duplicates(), grupo["llegada"]]).sort_values()
    dias = llegadas.dt.date
    diferencias = llegadas.groupby(dias).diff().dropna()
    return diferencias.dt.total_seconds().to_numpy() / 60


def ajustar(nombre, muestra):
    distribucion = getattr(stats, nombre)
    parametros = distribucion.fit(muestra) if nombre == "norm" else distribucion.fit(muestra, floc=0)
    return distribucion, parametros


def prueba_chi_cuadrado(distribucion, parametros, muestra):
    bordes = distribucion.ppf(np.linspace(0, 1, CLASES_CHI + 1)[1:-1], *parametros)
    observadas = np.bincount(np.searchsorted(bordes, muestra), minlength=CLASES_CHI)
    esperadas = np.full(CLASES_CHI, len(muestra) / CLASES_CHI)
    estadistico = float(((observadas - esperadas) ** 2 / esperadas).sum())
    estimados = len(parametros) - (0 if distribucion.name == "norm" else 1)
    grados = CLASES_CHI - 1 - estimados
    return estadistico, float(stats.chi2.sf(estadistico, grados))


def corregir_tasa_exponencial(elegida, grupo):
    dias = grupo["llegada"].dt.date.nunique()
    llegadas = len(grupo)
    return [0.0, dias * MINUTOS_JORNADA / llegadas]


def evaluar(muestra):
    filas = []
    for nombre in CANDIDATAS:
        distribucion, parametros = ajustar(nombre, muestra)
        log_verosimilitud = float(distribucion.logpdf(muestra, *parametros).sum())
        estimados = len(parametros) - (0 if nombre == "norm" else 1)
        ks = stats.kstest(muestra, distribucion.cdf, args=parametros)
        chi, p_chi = prueba_chi_cuadrado(distribucion, parametros, muestra)
        filas.append(
            {
                "distribucion": nombre,
                "parametros": [float(p) for p in parametros],
                "aic": 2 * estimados - 2 * log_verosimilitud,
                "ks_estadistico": float(ks.statistic),
                "ks_p": float(ks.pvalue),
                "chi2_estadistico": chi,
                "chi2_p": p_chi,
            }
        )
    return filas


def elegir(filas):
    aceptadas = [f for f in filas if f["ks_p"] > NIVEL and f["chi2_p"] > NIVEL]
    if aceptadas:
        return min(aceptadas, key=lambda f: f["aic"])
    return max(filas, key=lambda f: min(f["ks_p"], f["chi2_p"]))


def ajustar_todo(datos):
    tabla, parametros = [], {}
    for servicio, grupo in datos.groupby("servicio"):
        parametros[servicio] = {"profesionales": int(grupo["profesional"].nunique())}
        for variable, muestra in (
            ("llegadas", tiempos_entre_llegadas(grupo)),
            ("servicio", grupo["atencion_min"].to_numpy()),
        ):
            filas = evaluar(muestra)
            elegida = elegir(filas)
            estimados = elegida["parametros"]
            if variable == "llegadas" and elegida["distribucion"] == "expon":
                estimados = corregir_tasa_exponencial(elegida, grupo)
            parametros[servicio][variable] = {
                "distribucion": elegida["distribucion"],
                "parametros": estimados,
                "observaciones": int(len(muestra)),
                "media_muestral": float(muestra.mean()),
            }
            tabla.extend({"servicio": servicio, "variable": variable, "n": len(muestra), "elegida": f is elegida, **f} for f in filas)
    parametros["_global"] = {"fraccion_prioritaria": float((datos["prioridad"] == "prioritaria").mean())}
    return pd.DataFrame(tabla), parametros


def ejecutar():
    datos = pd.read_csv(ENTRADA, parse_dates=["llegada", "inicio_atencion", "fin_atencion"])
    tabla, parametros = ajustar_todo(datos)
    tabla.to_csv(SALIDA_TABLA, index=False)
    SALIDA_PARAMETROS.write_text(json.dumps(parametros, indent=2, ensure_ascii=False), encoding="utf-8")
    print(tabla[tabla["elegida"]][["servicio", "variable", "distribucion", "ks_p", "chi2_p"]].to_string(index=False))


if __name__ == "__main__":
    ejecutar()
